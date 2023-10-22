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


def remove_container(container_id):
    run_command(f"docker rm {container_id}", ignore_error=True)


def stop_container(container_id):
    run_command(f"docker stop {container_id}", ignore_error=True)


def stop_and_remove_container(container_id):
    stop_container(container_id)
    remove_container(container_id)
