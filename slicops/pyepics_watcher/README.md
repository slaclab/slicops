# `pyepics_watcher` — general-purpose pyepics process introspection

Answers, for any process that has `import epics`'d: which PVs has it touched, which ones
currently have a live CA monitor, how much memory pyepics' internal caches are holding, how
fast each monitored PV is actually updating, and how many bytes of data each PV has received from
gets and from monitor events.

## Setup

> **Warning:** create the `PVTracker()` before the process creates its first PV or CA channel
> (the first `caget()`, `caput()`, `epics.PV()`, …). The first `PVTracker()` monkeypatches
> pyepics to count received data and track subscriptions, and anything created before it would be
> missed, so it raises `AssertionError` if a channel already exists. Creating it early and calling
> `start()` later is fine.

## Files

- `tracker.py` — `PVTracker` (which installs the monkeypatch, above):
  `snapshot()` (call any time, from any thread), `start()`/`stop()` (optional
  background poll loop) with two independent
  optional outputs: `csv_path` (full per-PV row every poll) and `log_path`/`log_interval_s` (one
  terse summary line appended every `log_interval_s`, default same as the poll interval).
- `report.py` — table printing and CSV export: `print_snapshot()` (full per-PV breakdown),
  `print_summary()` (one terse line of aggregate counts), and CSV helpers.

## Demo

```sh
slicops watcher_demo run [--log PATH] [--seconds N]
```

Implemented in `slicops/pkcli/watcher_demo.py`. Starts `slicops ioc run` on
`slicops/package_data/watcher_demo/` (on random local CA ports), reads four waveforms and a
scalar with plain `epics.caget()`, then starts a separate `slicops watcher_demo writer` process
that puts each PV at its own rate (SMALL 20 Hz, MEDIUM 5 Hz, IMAGE 1 Hz, LARGE 2 Hz, SCALAR
10 Hz; see `_PVS`). The writer's CA traffic is in its own process, so it doesn't show up in the
tracker's output. Meanwhile a `PVTracker` appends a summary line every second and a full per-PV
snapshot every 5 seconds to the log (default `pyepics_watcher_demo.log`):

```
[     10.0s] 5 PVs touched: 4 monitored, 1 not monitored -- 1988 kB cached, avg_update_hz=9 (max 20 on DEMO:WF:SMALL), received get_kb=994 monitor_kb=9855
[     10.0s] 5 PVs, 1988 kB cached total
pvname                   monitored connected    cache_kb  update_hz       get_kb     monitor_kb
DEMO:WF:LARGE                      X                1600                     800              0
DEMO:WF:MEDIUM           X         X                 320          5          160           8000
DEMO:WF:IMAGE            X         X                  52          1           26            286
DEMO:WF:SMALL            X         X                  16         20            8           1568
DEMO:SCALAR              X         X                   0         10            0              1
```

## Usage

```python
from slicops.pyepics_watcher import tracker, report

t = tracker.PVTracker()  # before the code under test creates any PVs, or it raises
# ... exercise the code under test ...
snap = t.snapshot()
report.print_summary(snap)   # one terse line of aggregate counts
report.print_snapshot(snap)  # full per-PV breakdown
```

For a long-running process, `start()`/`stop()` run the poll loop in a background thread instead:

```python
t = tracker.PVTracker(
    csv_path="pv_monitor.csv",              # full per-PV row every poll
    log_path="pv_monitor.log",              # terse summary + periodic snapshot, appended
    sample_interval_s=1.0,                  # poll cadence
    log_interval_s=30.0,                    # summary-line cadence (>= sample_interval_s)
    snapshot_interval_s=300.0,              # full per-PV breakdown cadence (optional, into log_path)
)
t.start()
# ... app runs ...
t.stop()
```

`snapshot_interval_s` is independent of `log_interval_s` and usually much coarser — a full
per-PV breakdown is a lot more log volume per write than one terse line. Both write into the
same `log_path`, interleaved by whichever comes due; omit `snapshot_interval_s` to get only the
terse summary lines (the default).
