from pathlib import Path
import json
from duckdb_store import db_get, db_set

DEFAULT_SETTINGS = {
    "card_back": "/images/card_back/card_back.png",
    "theme": "light",
    "music_volume": 0.5,
    "sfx_volume": 0.8,
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
    return ("file", None)  


def storage_get(page, key, default=None):
    # Consulta primária estabelecida ao motor relacional local (DuckDB).
    db_value = db_get(key)
    if db_value is not None:
        return db_value

    # Método de fallback: inspeção da API de persistência da sessão em memória se houver latência/dado inexistente na base transacional.
    kind, storage = _get_storage(page)

    if kind in ("client", "storage"):
        try:
            value = storage.get(key, default)
        except TypeError:
            value = storage.get(key)
    elif kind == "file":
        value = _file_load().get(key, default)
    else:
        value = default

    # Procedimento reativo: Replica o estado volátil adquirido da memória para a persistência no storage local.
    if value is not None:
        db_set(key, value)

    return value


def storage_set(page, key, value):
    # Comutação contínua da mutação ao motor analítico.
    db_set(key, value)

    # Injeção em cache da sessão consoante o hardware local acessível para otimizar futuros acessos.
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