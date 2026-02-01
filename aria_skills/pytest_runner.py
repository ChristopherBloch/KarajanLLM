# aria_skills/pytest_runner.py
"""Pytest runner skill.

Runs pytest inside the OpenClaw workspace and returns structured results.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import time
from typing import List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry


@SkillRegistry.register
class PytestSkill(BaseSkill):
    """Run pytest for Aria codebase."""

    @property
    def name(self) -> str:
        return "pytest"

    async def initialize(self) -> bool:
        """Initialize the pytest runner."""
        try:
            import pytest  # noqa: F401
        except Exception:
            self._status = SkillStatus.UNAVAILABLE
            return False

        self._status = SkillStatus.AVAILABLE
        return True

    async def health_check(self) -> SkillStatus:
        """Check if pytest is available."""
        return self._status

    def _build_command(
        self,
        paths: Optional[List[str]] = None,
        markers: Optional[str] = None,
        keyword: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> List[str]:
        default_args = self.config.config.get("default_args", "-q")
        args = [sys.executable, "-m", "pytest"] + shlex.split(default_args)

        if markers:
            args += ["-m", markers]
        if keyword:
            args += ["-k", keyword]
        if extra_args:
            args += extra_args
        if paths:
            args += paths
        else:
            args += ["tests"]

        return args

    def run_pytest(
        self,
        paths: Optional[List[str]] = None,
        markers: Optional[str] = None,
        keyword: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        timeout_sec: Optional[int] = None,
    ) -> SkillResult:
        """Run pytest and return stdout/stderr and exit code."""
        if self._status != SkillStatus.AVAILABLE:
            return SkillResult.fail("pytest is not available")

        cwd = self.config.config.get("workspace", "/root/.openclaw/workspace")
        timeout = timeout_sec or int(self.config.config.get("timeout_sec", 600))
        cmd = self._build_command(paths, markers, keyword, extra_args)

        start = time.time()
        try:
            completed = subprocess.run(
                cmd,
                cwd=cwd,
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            duration = time.time() - start
            self._log_usage("run_pytest", completed.returncode == 0)
            return SkillResult.ok(
                {
                    "exit_code": completed.returncode,
                    "duration_sec": round(duration, 3),
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                    "command": cmd,
                    "cwd": cwd,
                }
            )
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            self._log_usage("run_pytest", False)
            return SkillResult.fail(f"pytest timed out after {round(duration, 3)}s")
        except Exception as exc:
            self._log_usage("run_pytest", False)
            return SkillResult.fail(str(exc))

    def collect_pytest(
        self,
        paths: Optional[List[str]] = None,
        markers: Optional[str] = None,
        keyword: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> SkillResult:
        """Collect pytest tests without running them."""
        if self._status != SkillStatus.AVAILABLE:
            return SkillResult.fail("pytest is not available")

        cwd = self.config.config.get("workspace", "/root/.openclaw/workspace")
        cmd = self._build_command(paths, markers, keyword, extra_args)
        cmd += ["--collect-only", "-q"]

        try:
            completed = subprocess.run(
                cmd,
                cwd=cwd,
                env=os.environ.copy(),
                capture_output=True,
                text=True,
            )
            self._log_usage("collect_pytest", completed.returncode == 0)
            return SkillResult.ok(
                {
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                    "command": cmd,
                    "cwd": cwd,
                }
            )
        except Exception as exc:
            self._log_usage("collect_pytest", False)
            return SkillResult.fail(str(exc))
