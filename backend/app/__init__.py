import os
from pathlib import Path


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


project_root = Path(__file__).resolve().parent
workspace_root = project_root.parent
load_dotenv_file(workspace_root / ".env")
load_dotenv_file(workspace_root / ".env.local")

# AgentFlow AI backend package
