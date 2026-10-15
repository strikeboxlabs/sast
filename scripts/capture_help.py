#!/usr/bin/env python3
"""Capture authoring evidence from known version/help invocations (Python 3.10+)."""

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import time


DISPLAY_ENV = {"PAGER": "cat", "MANPAGER": "cat", "NO_COLOR": "1"}


def positive_timeout(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("timeout must be a finite positive number")
    return number


def stop_process(process):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()
    process.wait()


def capture_command(argv, destination, name, timeout):
    stdout_path = destination / (name + ".stdout.txt")
    stderr_path = destination / (name + ".stderr.txt")
    record = {
        "argv": argv,
        "stdout": stdout_path.name,
        "stderr": stderr_path.name,
        "exit_code": None,
        "timed_out": False,
        "error": None,
    }
    started = time.monotonic()
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        try:
            process = subprocess.Popen(
                argv,
                cwd=destination,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                env={**os.environ, **DISPLAY_ENV},
                start_new_session=(os.name == "posix"),
            )
        except OSError as error:
            record["error"] = str(error)
        else:
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                record["timed_out"] = True
                stop_process(process)
            except BaseException:
                stop_process(process)
                raise
            record["exit_code"] = process.returncode
    record["duration_seconds"] = round(time.monotonic() - started, 3)
    record["stdout_bytes"] = stdout_path.stat().st_size
    record["stderr_bytes"] = stderr_path.stat().st_size
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", help="installed executable or explicit executable path")
    parser.add_argument("--output", type=Path, required=True, help="new capture directory; must not exist")
    parser.add_argument("--environment-id", help="optional image ID/digest or environment identifier supplied by the caller")
    parser.add_argument("--timeout", type=positive_timeout, default=30, help="seconds per command (default: 30)")
    parser.add_argument("--version-arg", action="append", help="replace default --version; repeat for multiple arguments, using --version-arg=VALUE")
    parser.add_argument("--help-arg", action="append", help="replace default --help; repeat for multiple arguments, using --help-arg=VALUE")
    args = parser.parse_args()
    if not args.tool:
        parser.error("tool cannot be empty")

    executable = shutil.which(args.tool)
    if executable:
        executable = str(Path(executable).resolve())
    destination = args.output.resolve()
    try:
        destination.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        parser.error("cannot create a fresh capture directory: " + str(error))

    os_release = None
    if platform.system() == "Linux":
        try:
            os_release = Path("/etc/os-release").read_text(encoding="utf-8")
        except OSError:
            pass
    report = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "version/help source capture, not workflow verification",
        "tool": args.tool,
        "resolved_executable": executable,
        "environment_id_supplied": args.environment_id,
        "system": platform.system(),
        "kernel_release": platform.release(),
        "machine": platform.machine(),
        "os_release": os_release,
        "cwd": str(destination),
        "environment_overrides": DISPLAY_ENV,
        "timeout_seconds": args.timeout,
        "commands": {},
    }
    for name, arguments in (
        ("version", args.version_arg if args.version_arg is not None else ["--version"]),
        ("help", args.help_arg if args.help_arg is not None else ["--help"]),
    ):
        report["commands"][name] = capture_command(
            [executable or args.tool, *arguments], destination, name, args.timeout
        )
    report["capture_complete"] = all(
        command["exit_code"] == 0 and not command["timed_out"] and command["error"] is None
        for command in report["commands"].values()
    )
    (destination / "capture.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print("{}: {}".format("Captured" if report["capture_complete"] else "Incomplete capture", destination))
    return 0 if report["capture_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
