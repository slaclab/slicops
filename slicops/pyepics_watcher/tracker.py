"""Track pyepics PVs in a running process: which PVs it has touched, which
are monitored and connected, memory held in pyepics' caches, monitor update
rates, and data bytes received from gets and monitors.

Create the tracker before the process creates its first PV or CA channel.
It monkeypatches pyepics, and raises AssertionError if a channel already
exists. Take snapshots on demand::

    from slicops.pyepics_watcher import report, tracker

    t = tracker.PVTracker()
    # ... code under test ...
    s = t.snapshot()
    report.print_summary(s)
    report.print_snapshot(s)

or log them from a background thread::

    t = tracker.PVTracker(log_path="pv.log", snapshot_interval_s=60)
    # ... later ...
    t.start()
    # ... app runs ...
    t.stop()
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import ctypes
import functools
import sys
import threading
import time

# pyepics' (not this module's) name for each callback _install() wraps
_PATCHED = PKDict(
    _CB_GET=PKDict(handler="_onGetEvent", kind="get"),
    _CB_EVENT=PKDict(handler="_onMonitorEvent", kind="monitor"),
)

# epics.ca functions _install() wraps to track _subscriptions
_SUBSCRIPTION_FUNCTIONS = ("clear_channel", "clear_subscription", "create_subscription")

_installed = False

# POSIT: guards _received, _subscriptions and _installed; also taken on
# libca's callback thread
_lock = threading.Lock()

# pvname -> PKDict(get_bytes=, get_count=, monitor_bytes=, monitor_count=),
# lifetime totals since _install(), plus monitor_first_at: time.monotonic()
# of the first monitor event (None until one arrives)
_received = PKDict()

# event id (int) -> PKDict(chid=, pvname=) for each active subscription
_subscriptions = {}


class PVTracker:
    """Snapshots of the process's pyepics PVs, on demand or logged by start()

    Construct before the process creates its first PV or CA channel, or it
    raises AssertionError. Constructing early and calling start() later is
    fine.

    Args:
        csv_path (str): append a full per-PV row every poll
        sample_interval_s (float): start()'s poll interval
        log_path (str): append a summary line every log_interval_s
        log_interval_s (float): defaults to sample_interval_s
        snapshot_interval_s (float): also append the full per-PV table to
            log_path at this interval
    """

    def __init__(
        self,
        csv_path: str = None,
        sample_interval_s: float = 1.0,
        log_path: str = None,
        log_interval_s: float = None,
        snapshot_interval_s: float = None,
    ):
        self._csv_path = csv_path
        self._sample_interval_s = sample_interval_s
        self._log_path = log_path
        self._log_interval_s = (
            log_interval_s if log_interval_s is not None else sample_interval_s
        )
        self._last_log_at = None
        self._snapshot_interval_s = snapshot_interval_s
        self._last_snapshot_log_at = None
        self._lock = threading.Lock()
        self._last_rate_check: dict = {}
        self._stop = threading.Event()
        self._thread = None
        self._t_start = time.monotonic()
        _install()

    def snapshot(self) -> PKDict:
        import epics
        import epics.ca
        from epics.pv import _PVcache_

        pvs = PKDict()

        for pvid in list(_PVcache_):
            pv_obj = _PVcache_.get(pvid)
            if pv_obj is None:
                continue
            monitored = bool(pv_obj.auto_monitor) and pv_obj._monref is not None
            pvs[pv_obj.pvname] = PKDict(
                pvname=pv_obj.pvname,
                has_pv_object=True,
                monitored=monitored,
                auto_monitor=bool(pv_obj.auto_monitor),
                connected=bool(pv_obj.connected),
                cache_bytes=_pv_value_bytes(pv_obj),
            )

        ctx = epics.ca.current_context()
        context_cache = epics.ca._cache.get(ctx, {}) if ctx else {}
        # Copy: the app creates channels while we iterate, which would raise
        # "dictionary changed size during iteration" and kill start()'s thread
        for pvname, entry in list(context_cache.items()):
            # get_results bytes (explicit-.get() cache) -- added to, not
            # replacing, whatever _pv_value_bytes() already found for this
            # pvname above: they're two distinct caches (see module
            # docstring) and either, or both, can hold real data.
            get_bytes = _entry_cache_bytes(entry)
            existing = pvs.get(pvname)
            if existing is not None:
                existing.cache_bytes += get_bytes
                continue

            pv_obj = _find_pv_object(epics, entry)
            if pv_obj is not None:
                monitored = bool(pv_obj.auto_monitor) and pv_obj._monref is not None
                pvs[pvname] = PKDict(
                    pvname=pvname,
                    has_pv_object=True,
                    monitored=monitored,
                    auto_monitor=bool(pv_obj.auto_monitor),
                    connected=bool(pv_obj.connected),
                    cache_bytes=get_bytes + _pv_value_bytes(pv_obj),
                )
            else:
                pvs[pvname] = PKDict(
                    pvname=pvname,
                    has_pv_object=False,
                    # Set from _subscriptions below
                    monitored=False,
                    auto_monitor=None,
                    # Not the CA channel's state: pyepics keeps the channel
                    # open after PV.disconnect(), with nothing using it
                    connected=False,
                    cache_bytes=get_bytes,
                )

        with _lock:
            r = PKDict({k: v.copy() for k, v in _received.items()})
            s = PKDict()
            for x in _subscriptions.values():
                s[x.pvname] = s.get(x.pvname, 0) + 1
        for n, p in pvs.items():
            x = r.get(n) or _received_zero()
            f = x.pkdel("monitor_first_at")
            p.update(x)
            p.subscriptions = s.get(n, 0)
            p.monitored = p.monitored or p.subscriptions > 0
            p.connected = p.connected or p.subscriptions > 0
            # None: never monitored, so no rate to report
            p.update_hz = (
                self._update_hz(n, p.monitor_count, f)
                if p.monitored or p.monitor_count
                else None
            )
        return PKDict(
            pvs=pvs,
            total_cache_bytes=sum(p.cache_bytes for p in pvs.values()),
            total_get_bytes=sum(p.get_bytes for p in pvs.values()),
            total_monitor_bytes=sum(p.monitor_bytes for p in pvs.values()),
            taken_at=time.monotonic(),
        )

    def start(self) -> None:
        if self._csv_path:
            from slicops.pyepics_watcher import report

            report.write_header(self._csv_path)
        # Log timestamps are relative to start(), not construction
        self._t_start = time.monotonic()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)

    def _attach_to_ca_context(self) -> None:
        # First CA call this thread makes -- best-effort attach.
        try:
            import epics.ca

            epics.ca.use_initial_context()
        except Exception as exc:
            if "already attached" not in str(exc):
                raise

    def _poll(self, report) -> None:
        snap = self.snapshot()
        elapsed_s = time.monotonic() - self._t_start
        if self._csv_path:
            report.append_rows(self._csv_path, snap, elapsed_s)
        if self._log_path and (
            self._last_log_at is None
            or elapsed_s - self._last_log_at >= self._log_interval_s
        ):
            report.write_summary(self._log_path, snap, elapsed_s)
            self._last_log_at = elapsed_s
        if (
            self._log_path
            and self._snapshot_interval_s
            and (
                self._last_snapshot_log_at is None
                or elapsed_s - self._last_snapshot_log_at >= self._snapshot_interval_s
            )
        ):
            report.write_snapshot(self._log_path, snap, elapsed_s)
            self._last_snapshot_log_at = elapsed_s

    def _run(self) -> None:
        self._attach_to_ca_context()

        from slicops.pyepics_watcher import report

        while not self._stop.is_set():
            try:
                self._poll(report)
            except Exception as e:
                # Broad on purpose: an uncaught error would end this thread,
                # silently stopping all logging for the rest of the process
                pkdlog("error={} stack={}", e, pkdexc())
            self._stop.wait(self._sample_interval_s)

    def _update_hz(self, pvname: str, monitor_count: int, first_at) -> float:
        """Monitor events per second since the *last* call for this pvname
        (a windowed rate), not a lifetime average -- a lifetime average
        freezes its numerator (the count) once updates stop while its
        denominator keeps growing on every later call, so it decays toward
        zero as ~1/t long after the monitor has gone quiet, instead of
        reflecting that. Confirmed directly: this was exactly why update_hz
        was seen decaying slowly rather than dropping once a monitor
        actually stopped.

        The first window for a pvname starts at its first monitor event
        (first_at) and counts only the events after it, so it measures the
        rate data actually arrives at, not time spent before the monitor
        started. Until that first event, the rate is 0.0.
        """
        if first_at is None:
            return 0.0
        n = time.monotonic()
        with self._lock:
            c, t = self._last_rate_check.get(pvname, (1, first_at))
            self._last_rate_check[pvname] = (monitor_count, n)
        return (monitor_count - c) / (n - t) if n > t else 0.0


def _assert_no_channels(epics):
    """Raise if any CA channel exists yet (see _install())"""
    c = sorted(n for x in list(epics.ca._cache.values()) for n in list(x))
    if c:
        raise AssertionError(
            "PVTracker() must be created before any CA channels;"
            + f" {len(c)} already exist, e.g. {c[:3]}"
        )


def _count_received(epics, args, kind):
    if args.status != epics.dbr.ECA_NORMAL:
        return
    t = epics.dbr.Map.get(epics.dbr.native_type(args.type))
    if t is None:
        return
    try:
        n = epics.ca._get_cache_by_chid(args.chid).pvname
    except KeyError:
        return
    with _lock:
        if n not in _received:
            _received[n] = _received_zero()
        r = _received[n]
        r[kind + "_bytes"] += args.count * ctypes.sizeof(t)
        r[kind + "_count"] += 1
        if kind == "monitor" and r.monitor_first_at is None:
            r.monitor_first_at = time.monotonic()


def _counting_handler(epics, handler, kind):
    def _handler(args, **kwargs):
        try:
            _count_received(epics, args, kind)
        finally:
            # pyepics must see every event, even if counting failed
            handler(args, **kwargs)

    return _handler


def _ctypes_value(value):
    """chid/event id as an int, whether passed as a ctypes object or int"""
    return getattr(value, "value", value)


def _entry_cache_bytes(entry) -> int:
    """Size, in bytes, of the values epics.ca._CacheItem.get_results is
    holding for this channel.

    Each holder[0] is what epics.ca._onGetEvent() stored: normally a
    [meta_or_None, ctypes_array] pair from dbr.cast_args() (confirmed
    directly against epics/dbr.py) -- ctypes.sizeof() on that array element
    gives the real wire-format byte count. Anything else found there (the
    GET_PENDING sentinel while a get is in flight, or a
    ChannelAccessGetFailure on error) isn't ctypes-sizeable, so it falls
    back to nbytes/sys.getsizeof of whatever's actually there.
    """
    results = getattr(entry, "get_results", None)
    if not results:
        return 0
    total = 0
    # Copy: libca's callback thread stores get results while we iterate
    for _ftype, holder in list(results.items()):
        value = holder[0] if holder else None
        if value is None:
            continue
        payload = (
            value[1] if isinstance(value, (list, tuple)) and len(value) == 2 else value
        )
        if payload is None:
            continue
        try:
            total += ctypes.sizeof(payload)
        except TypeError:
            nbytes = getattr(payload, "nbytes", None)
            total += nbytes if nbytes is not None else sys.getsizeof(payload)
    return total


def _find_pv_object(epics_module, entry):
    """Recover the PV wrapper for a channel _PVcache_ never registered,
    by walking the connection callbacks pyepics itself put on entry.callbacks.

    If more than one independent PV object shares this channel (two separate
    epics.PV(same_name) calls in the same process), only one is returned as
    a representative -- good enough for reporting per-pvname, not per
    PV-instance, monitor status.
    """
    # Copy: PV.disconnect() removes callbacks from another thread
    for cb in list(getattr(entry, "callbacks", [])):
        owner = getattr(cb, "__self__", None)
        if isinstance(owner, epics_module.PV):
            return owner
    return None


def _install() -> None:
    """Monkeypatch pyepics to count gets, monitor events and their data
    bytes, and track active subscriptions, per pvname

    Idempotent. Raises AssertionError if a CA channel already exists, since
    anything subscribed before this would be missed. Counts data only
    (count x element size), not DBR metadata or CA headers.
    """
    global _installed

    import epics.ca
    import epics.dbr

    with _lock:
        if _installed:
            return
        for n in (
            *_PATCHED.keys(),
            *(v.handler for v in _PATCHED.values()),
            *_SUBSCRIPTION_FUNCTIONS,
            "_cache",
            "_get_cache_by_chid",
        ):
            if not hasattr(epics.ca, n):
                raise AssertionError(f"pyepics missing epics.ca.{n}")
        _assert_no_channels(epics)
        for k, v in _PATCHED.items():
            # POSIT: libca holds a raw pointer to the callback; the module
            # global keeps it alive for the life of the process
            setattr(
                epics.ca,
                k,
                epics.dbr.make_callback(
                    _counting_handler(epics, getattr(epics.ca, v.handler), v.kind),
                    epics.dbr.event_handler_args,
                ),
            )
        for k, v in _subscription_wrappers(epics).items():
            setattr(epics.ca, k, v)
        _installed = True


def _pv_value_bytes(pv_obj) -> int:
    """Size, in bytes, of the value a live PV object is holding right now
    (pv_obj._args['value']) -- this is what a *monitored* PV actually
    updates on every push, never
    _CacheItem.get_results. as_numpy defaults to True in pyepics, so for
    array/waveform data this is normally a real numpy array with .nbytes;
    sys.getsizeof() covers anything else (a scalar, a string).
    """
    args = getattr(pv_obj, "_args", None)
    if not args:
        return 0
    value = args.get("value")
    if value is None:
        return 0
    nbytes = getattr(value, "nbytes", None)
    return nbytes if nbytes is not None else sys.getsizeof(value)


def _received_zero():
    return PKDict(
        get_bytes=0,
        get_count=0,
        monitor_bytes=0,
        monitor_count=0,
        monitor_first_at=None,
    )


def _subscription_wrappers(epics):
    """Wrappers for _SUBSCRIPTION_FUNCTIONS that maintain _subscriptions"""
    o = PKDict({k: getattr(epics.ca, k) for k in _SUBSCRIPTION_FUNCTIONS})

    @functools.wraps(o.clear_channel)
    def clear_channel(chid, *args, **kwargs):
        c = _ctypes_value(chid)
        with _lock:
            for k in [k for k, v in _subscriptions.items() if v.chid == c]:
                del _subscriptions[k]
        return o.clear_channel(chid, *args, **kwargs)

    @functools.wraps(o.clear_subscription)
    def clear_subscription(event_id, *args, **kwargs):
        with _lock:
            _subscriptions.pop(_ctypes_value(event_id), None)
        return o.clear_subscription(event_id, *args, **kwargs)

    @functools.wraps(o.create_subscription)
    def create_subscription(chid, *args, **kwargs):
        rv = o.create_subscription(chid, *args, **kwargs)
        # None when libca has been finalized
        if rv is not None:
            n = epics.ca.name(chid)
            with _lock:
                _subscriptions[_ctypes_value(rv[2])] = PKDict(
                    chid=_ctypes_value(chid), pvname=n
                )
        return rv

    return PKDict(
        clear_channel=clear_channel,
        clear_subscription=clear_subscription,
        create_subscription=create_subscription,
    )
