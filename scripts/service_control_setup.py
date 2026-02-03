from __future__ import annotations

import argparse
from getpass import getpass
from pathlib import Path


def update_env(path: Path, enabled: bool, token: str, mlx_restart: str | None, mlx_stop: str | None) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    keys = {
        "ARIA_SERVICE_CONTROL_ENABLED": "true" if enabled else "false",
        "ARIA_ADMIN_TOKEN": token,
    }
    if mlx_restart is not None:
        keys["ARIA_SERVICE_CMD_MLX_RESTART"] = mlx_restart
    if mlx_stop is not None:
        keys["ARIA_SERVICE_CMD_MLX_STOP"] = mlx_stop

    seen = set()
    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            updated.append(line)
            continue
        key = line.split("=", 1)[0]
        if key in keys:
            if key not in seen:
                updated.append(f"{key}={keys[key]}")
                seen.add(key)
            continue
        updated.append(line)

    for key, value in keys.items():
        if key not in seen:
            updated.append(f"{key}={value}")

    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enable service control without storing secrets in repo")
    parser.add_argument("--env", default="stacks/brain/.env", help="Path to .env file")
    parser.add_argument("--enable", action="store_true", help="Enable service control")
    parser.add_argument("--disable", action="store_true", help="Disable service control")
    parser.add_argument("--token", default=None, help="Admin token (if omitted, will prompt)")
    parser.add_argument("--mlx-restart", default=None, help="Command for MLX restart")
    parser.add_argument("--mlx-stop", default=None, help="Command for MLX stop")
    args = parser.parse_args()

    env_path = Path(args.env).expanduser().resolve()
    if not env_path.exists():
        raise SystemExit(f"Env file not found: {env_path}")

    if args.disable and args.enable:
        raise SystemExit("Choose either --enable or --disable")

    enabled = args.enable and not args.disable
    token = args.token if args.token is not None else getpass("Admin token: ")

    update_env(env_path, enabled=enabled, token=token, mlx_restart=args.mlx_restart, mlx_stop=args.mlx_stop)
    print(f"Updated {env_path}")


if __name__ == "__main__":
    main()
