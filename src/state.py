DEFAULT_SETTINGS = {
    "card_back": "/images/card_back.png",
    "theme": "light",
}


def _get_storage(page):
    if hasattr(page, "client_storage"):
        return ("client", page.client_storage)
    if hasattr(page, "storage"):
        return ("storage", page.storage)
    return ("session", page.session)  # dict fallback


def load_settings(page):
    kind, storage = _get_storage(page)

    if kind == "session":
        data = storage.get("settings", {}) if isinstance(storage, dict) else {}
    else:
        data = storage.get("settings") or {}

    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    return merged


def save_settings(page, settings):
    kind, storage = _get_storage(page)

    if kind == "session":
        if isinstance(storage, dict):
            storage["settings"] = settings
    else:
        storage.set("settings", settings)


def has_savegame(page):
    kind, storage = _get_storage(page)

    if kind == "session":
        return bool(storage.get("savegame")) if isinstance(storage, dict) else False
    return storage.get("savegame") is not None