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


def get_directory_size(path):
    """Returns the size of a directory in bytes."""
    size_output = run_command(f"sudo du -sb {path}")
    size_in_bytes, _ = size_output.split("\t", 1)
    return int(size_in_bytes)
