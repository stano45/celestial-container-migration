import os
import subprocess


def run_command(command, ignore_error=False):
    """Execute the command and return its output."""
    result = subprocess.run(
        command, capture_output=True, text=True, shell=True
    )
    if result.returncode != 0 and not ignore_error:
        raise RuntimeError(
            f"Error executing command: {command}\n{result.stderr}"
        )
    return result.stdout.strip()


def get_file_size(path):
    """Returns the size of a file in bytes."""
    return os.path.getsize(path)
