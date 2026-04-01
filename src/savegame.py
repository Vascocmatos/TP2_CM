import time
from state import storage_get, storage_set

SLOTS = [1, 2, 3]


def _slot_key(slot):
    return f"savegame_{slot}"


def _slot_meta_key(slot):
    return f"savegame_{slot}_meta"


def save_game(page, slot, data):
    key = _slot_key(slot)
    meta_key = _slot_meta_key(slot)
    meta = {
        "slot": slot,
        "timestamp": int(time.time()),
    }

    storage_set(page, key, data)
    storage_set(page, meta_key, meta)


def load_game(page, slot):
    key = _slot_key(slot)
    return storage_get(page, key)


def load_meta(page, slot):
    meta_key = _slot_meta_key(slot)
    return storage_get(page, meta_key)


def delete_game(page, slot):
    storage_set(page, _slot_key(slot), None)
    storage_set(page, _slot_meta_key(slot), None)


def list_slots(page):
    slots = []
    for s in SLOTS:
        slots.append(
            {
                "slot": s,
                "meta": load_meta(page, s),
                "data": load_game(page, s),
            }
        )
    return slots