"""Static Semgrep test input. Do not execute or import this fixture."""

import subprocess


def shell_enabled(command):
    # ruleid: python-shell-enabled
    subprocess.run(command, shell=True)
    # ruleid: python-shell-enabled
    subprocess.Popen(command, shell=True)


def shell_disabled(command):
    # ok: python-shell-enabled
    subprocess.run(command, shell=False)
    # ok: python-shell-enabled
    subprocess.Popen(["printf", "%s", command])
