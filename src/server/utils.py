import os
import subprocess

from server.config import CHECKPOINT_DIR, CHECKPOINT_NAME


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


def get_checkpoint_path(container_id):
    checkpoint_name = f"{CHECKPOINT_NAME}-{container_id}.tar.gz"
    return os.path.join(CHECKPOINT_DIR, checkpoint_name)
