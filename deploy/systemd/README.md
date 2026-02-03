# Aria Stack Systemd Service

Auto-start and manage the Aria Docker stack on Linux servers.

## Installation

```bash
# 1. Copy service file
sudo cp aria-stack.service /etc/systemd/system/

# 2. Edit paths if needed (default: /opt/aria)
sudo systemctl edit aria-stack.service

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable auto-start on boot
sudo systemctl enable aria-stack.service

# 5. Start now
sudo systemctl start aria-stack.service
```

## Commands

```bash
# Check status
sudo systemctl status aria-stack

# View logs
sudo journalctl -u aria-stack -f

# Restart stack
sudo systemctl restart aria-stack

# Stop stack (keeps containers down after reboot)
sudo systemctl stop aria-stack
sudo systemctl disable aria-stack

# Reload (restart all containers)
sudo systemctl reload aria-stack
```

## Paths

Default installation assumes:
- Stack: `/opt/aria/stacks/brain/docker-compose.yml`
- Env: `/opt/aria/stacks/brain/.env`

Edit the service file to match your installation path:
```bash
sudo systemctl edit aria-stack.service
```

Add override:
```ini
[Service]
WorkingDirectory=/your/actual/path
EnvironmentFile=/your/actual/path/.env
```

## Note for macOS

macOS uses launchd, not systemd. See `deploy/mac/` for:
- `com.aria.mlx-server.plist` - MLX server auto-start
- Use Docker Desktop settings for container auto-restart
