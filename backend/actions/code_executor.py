"""
Sandboxed code execution using Docker (preferred) or subprocess with limits.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile


class SandboxExecutor:
    def __init__(self, use_docker: bool = False):
        self.use_docker = use_docker and self._docker_available()

    @staticmethod
    def _docker_available() -> bool:
        try:
            subprocess.run(["docker", "info"], capture_output=True, timeout=5, check=True)
            return True
        except Exception:
            return False

    def run_python(self, code: str, timeout: int = 30) -> dict:
        if self.use_docker:
            return self._run_docker(code, "python3", timeout)
        return self._run_subprocess_python(code, timeout)

    def run_javascript(self, code: str, timeout: int = 30) -> dict:
        if self.use_docker:
            return self._run_docker(code, "node", timeout)
        return self._run_subprocess_js(code, timeout)

    # ──────────────────────────────────────────────────────────────────────────

    def _run_subprocess_python(self, code: str, timeout: int) -> dict:
        wrapper = (
            "import sys, resource\n"
            "try:\n"
            "    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))\n"
            "except Exception:\n"
            "    pass\n"
        ) + code

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(wrapper)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                env={k: v for k, v in os.environ.items() if k in (
                    "PATH", "HOME", "PYTHONPATH", "LANG", "LC_ALL"
                )},
            )
            return {
                "stdout": result.stdout[:4096],
                "stderr": result.stderr[:2048],
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Execution timed out", "exit_code": -1}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "exit_code": -1}
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _run_subprocess_js(self, code: str, timeout: int) -> dict:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(code)
            tmp_path = f.name
        try:
            result = subprocess.run(
                ["node", tmp_path],
                capture_output=True, text=True, timeout=timeout,
            )
            return {
                "stdout": result.stdout[:4096],
                "stderr": result.stderr[:2048],
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Execution timed out", "exit_code": -1}
        except FileNotFoundError:
            return {"stdout": "", "stderr": "Node.js not installed", "exit_code": -1}
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _run_docker(self, code: str, runtime: str, timeout: int) -> dict:
        images = {"python3": "python:3.12-slim", "node": "node:20-slim"}
        image = images.get(runtime, "python:3.12-slim")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".code", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "--memory=256m", "--cpus=0.5",
                    "--network=none",
                    "--read-only",
                    "-v", f"{tmp_path}:/code:ro",
                    image, runtime, "/code",
                ],
                capture_output=True, text=True, timeout=timeout + 10,
            )
            return {
                "stdout": result.stdout[:4096],
                "stderr": result.stderr[:2048],
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Container timed out", "exit_code": -1}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "exit_code": -1}
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
