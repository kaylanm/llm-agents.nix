"""Regression checks for the packaged Kanban worker interpreter."""

# Standalone Nix build check, not an importable Python package.
# ruff: noqa: INP001, PT009

import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from hermes_cli.kanban_db_dispatch import _worker_argv


class WorkerPythonTests(unittest.TestCase):
    """Exercise interpreter selection and the resulting child's imports."""

    def test_packaged_interpreter_can_import_worker_dependencies(self) -> None:
        """Use the packaged dependencies even when the parent interpreter is bare."""
        python = os.environ["HERMES_PYTHON"]
        # Nix console-script wrappers add dependencies without changing this.
        with patch.object(sys, "executable", "/bare/python"):
            argv = _worker_argv(None, "default", None)
        self.assertEqual(argv, [python, "-m", "hermes_cli.kanban_worker_client"])
        subprocess.run(
            [
                argv[0],
                "-c",
                (
                    "import hermes_cli.kanban_worker_client; "
                    "from websockets.asyncio.client import connect"
                ),
            ],
            check=True,
        )

    def test_unset_override_preserves_running_interpreter(self) -> None:
        """Preserve upstream behavior when no packaged runtime is configured."""
        with patch.dict(os.environ):
            os.environ.pop("HERMES_PYTHON", None)
            self.assertEqual(
                _worker_argv(None, "default", None),
                [sys.executable, "-m", "hermes_cli.kanban_worker_client"],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
