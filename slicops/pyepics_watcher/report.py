"""Table/CSV rendering for PVTracker.snapshot(): one column list, a
header-writing function, and a row-appending function.
"""

from pykern.pkdebug import pkdc, pkdlog, pkdp
import csv

CSV_COLUMNS = [
    "elapsed_s",
    "pvname",
    "has_pv_object",
    "monitored",
    "auto_monitor",
    "connected",
    "cache_bytes",
    "update_hz",
    "get_bytes",
    "monitor_bytes",
]


def append_rows(csv_path: str, snapshot, elapsed_s: float) -> None:
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        for pv in snapshot.pvs.values():
            writer.writerow(
                [round(elapsed_s, 1)]
                + [pv[col] for col in CSV_COLUMNS if col != "elapsed_s"]
            )


def print_snapshot(snapshot) -> None:
    """Full per-PV breakdown. See print_summary() for a one-line aggregate."""
    # One message so the table's lines stay together under one log prefix
    pkdlog("{}", "\n".join(_snapshot_lines(snapshot)))


def print_summary(snapshot) -> None:
    """Terse, one-line summary of a snapshot's aggregate values -- how many
    PVs touched, how many are monitored/unmonitored, total cache
    memory, and total bytes received. See print_snapshot() for the full
    per-PV breakdown."""
    pkdlog("{}", _summary_line(snapshot))


def write_header(csv_path: str) -> None:
    with open(csv_path, "w", newline="") as f:
        csv.writer(f).writerow(CSV_COLUMNS)


def write_snapshot(log_path: str, snapshot, elapsed_s: float) -> None:
    """Append the full per-PV breakdown (see print_snapshot()) to log_path --
    used internally by tracker._run() for PVTracker's snapshot_interval_s
    option, independent of and typically coarser than log_interval_s's terse
    summary line (a full breakdown is much more log volume per write).
    Opened in append mode, like write_summary().
    """
    with open(log_path, "a") as f:
        f.write("\n".join(_snapshot_lines(snapshot, elapsed_s)) + "\n")


def write_summary(log_path: str, snapshot, elapsed_s: float) -> None:
    """Append one terse summary line (see print_summary()) to log_path --
    used internally by tracker._run() for PVTracker's log_path option.
    Opened in append mode: restarting the tracker adds to the log rather
    than truncating it.
    """
    with open(log_path, "a") as f:
        f.write(_summary_line(snapshot, elapsed_s) + "\n")


def _fmt(value) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "X" if value else ""
    if isinstance(value, float):
        return f"{value:.0f}"
    return str(value)


def _kb(num_bytes) -> str:
    return f"{num_bytes / 1000:.0f}"


def _snapshot_lines(snapshot, elapsed_s: float = None) -> list:
    prefix = f"[{elapsed_s:>9.1f}s] " if elapsed_s is not None else ""
    lines = [
        f"{prefix}{len(snapshot.pvs)} PVs, {_kb(snapshot.total_cache_bytes)} kB cached total",
        f"{'pvname':<24} {'monitored':<9} {'connected':<9} {'cache_kb':>11} {'update_hz':>10}"
        + f" {'get_kb':>12} {'monitor_kb':>14}",
    ]
    for pv in sorted(snapshot.pvs.values(), key=lambda p: -p.cache_bytes):
        lines.append(
            f"{pv.pvname:<24} {_fmt(pv.monitored):<9} {_fmt(pv.connected):<9} "
            f"{_kb(pv.cache_bytes):>11} {'' if pv.update_hz is None else _fmt(pv.update_hz):>10} "
            f"{_kb(pv.get_bytes):>12} {_kb(pv.monitor_bytes):>14}"
        )
    return lines


def _summary_line(snapshot, elapsed_s: float = None) -> str:
    monitored = sum(1 for p in snapshot.pvs.values() if p.monitored)
    unmonitored = sum(1 for p in snapshot.pvs.values() if p.monitored is False)
    prefix = f"[{elapsed_s:>9.1f}s] " if elapsed_s is not None else ""
    rates = [(p.pvname, p.update_hz) for p in snapshot.pvs.values() if p.update_hz]
    if rates:
        top_name, top_hz = max(rates, key=lambda r: r[1])
        avg_hz = sum(hz for _, hz in rates) / len(rates)
        hz_part = f", avg_update_hz={avg_hz:.0f} (max {top_hz:.0f} on {top_name})"
    else:
        hz_part = ", update_hz=n/a (no monitor events yet)"
    return (
        f"{prefix}{len(snapshot.pvs)} PVs touched: "
        f"{monitored} monitored, {unmonitored} not monitored -- "
        f"{_kb(snapshot.total_cache_bytes)} kB cached{hz_part}, "
        f"received get_kb={_kb(snapshot.total_get_bytes)} "
        f"monitor_kb={_kb(snapshot.total_monitor_bytes)}"
    )
