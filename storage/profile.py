# storage/profile.py
import json, os, time

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "randompac_profiles.json")

def _ensure_file(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"players": {}, "music": True}, f, ensure_ascii=False, indent=2)

def load_db(path=DEFAULT_PATH):
    _ensure_file(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db, path=DEFAULT_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def set_music_enabled(enabled: bool, path=DEFAULT_PATH):
    db = load_db(path)
    db["music"] = bool(enabled)
    save_db(db, path)

def is_music_enabled(path=DEFAULT_PATH) -> bool:
    db = load_db(path)
    return bool(db.get("music", True))

def ensure_player(name: str, path=DEFAULT_PATH):
    db = load_db(path)
    if name not in db["players"]:
        db["players"][name] = {
            "created_at": int(time.time()),
            "best_score": 0,
            "games": 0,
            "total_time_s": 0,
            "last_config": {}
        }
        save_db(db, path)

def update_stats(name: str, score: int, time_s: int, config: dict, path=DEFAULT_PATH):
    db = load_db(path)
    p = db["players"].setdefault(
        name, {
            "created_at": int(time.time()),
            "best_score": 0,
            "games": 0,
            "total_time_s": 0,
            "best_rng": "LCG",
            "best_difficulty": "Clásico",
            "last_config": {}
        }
    )

    # sumar estadísticas generales
    p["games"] += 1
    p["total_time_s"] += int(time_s)
    p["last_config"] = config or {}

    # si superó el récord, actualizar datos del top
    if int(score) > p.get("best_score", 0):
        p["best_score"] = int(score)
        p["best_rng"] = (config or {}).get("rng", "LCG")
        p["best_difficulty"] = (config or {}).get("difficulty", "Clásico")

    save_db(db, path)


def get_stats(name: str, path=DEFAULT_PATH):
    db = load_db(path)
    return db["players"].get(name)
