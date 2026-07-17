import json
import logging
from pathlib import Path

logger = logging.getLogger('api')


def load_json_file(path: Path, default=None):
    """Безопасно читает JSON-файл; при ошибке возвращает default."""
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        content = path.read_text(encoding='utf-8').strip()
        if not content:
            return default
        return json.loads(content)
    except (json.JSONDecodeError, OSError, ValueError) as e:
        logger.error(f"Error loading JSON from {path}: {e}")
        return default


def save_json_file(path: Path, data, indent=None) -> None:
    """Атомарно записывает JSON во временный файл и заменяет целевой."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f'{path.suffix}.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        temp_path.replace(path)
    except OSError as e:
        logger.error(f"Error saving JSON to {path}: {e}")
