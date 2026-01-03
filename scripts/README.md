# Docker reinstall script

This folder contains `reinstall_docker.sh`, a helper script to uninstall and reinstall Docker on Ubuntu/Debian systems.

Usage (run as root):

```bash
sudo bash scripts/reinstall_docker.sh
```

What the script does:
- Optionally creates a tar.gz backup of `/var/lib/docker`.
- Removes Docker packages (and optionally deletes `/var/lib/docker` and `/var/lib/containerd`).
- Installs Docker from the official Docker repository.
- Enables and starts the Docker service and runs a quick verification (`hello-world`).

Run the script only if you accept that images/volumes may be lost unless you back them up.
