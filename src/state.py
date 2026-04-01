from pathlib import Path
import json

DEFAULT_SETTINGS = {
    "card_back": "/images/card_back/card_back.png",
    "theme": "light",
}

_STORE_FILE = Path(__file__).resolve().parent / "local_storage.json"


def _file_load():
    if not _STORE_FILE.exists():
        return {}
    try:
        return json.loads(_STORE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _file_save(data):
    _STORE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_storage(page):
    if hasattr(page, "client_storage") and page.client_storage is not None:
        return ("client", page.client_storage)
    if hasattr(page, "storage") and page.storage is not None:
        return ("storage", page.storage)
    return ("file", None)  # fallback persistente


def storage_get(page, key, default=None):
    kind, storage = _get_storage(page)

    if kind in ("client", "storage"):
        try:
            return storage.get(key, default)
        except TypeError:
            return storage.get(key)

    if kind == "file":
        return _file_load().get(key, default)

    return default


def storage_set(page, key, value):
    kind, storage = _get_storage(page)

    if kind in ("client", "storage"):
        try:
            storage.set(key, value)
        except Exception:
            pass
        return

    if kind == "file":
        data = _file_load()
        data[key] = value
        _file_save(data)


def load_settings(page):
    data = storage_get(page, "settings", {})
    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    return merged


def save_settings(page, settings):
    storage_set(page, "settings", settings)


def has_savegame(page):
    return bool(
        storage_get(page, "savegame_1")
        or storage_get(page, "savegame_2")
        or storage_get(page, "savegame_3")
    )