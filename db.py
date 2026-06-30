import sqlite3
from datetime import datetime

DB_PATH = "bot_data.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS guild_personas (
                guild_id   TEXT PRIMARY KEY,
                persona    TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS guild_memories (
                guild_id   TEXT PRIMARY KEY,
                summary    TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_memories (
                guild_id   TEXT NOT NULL,
                user_id    TEXT NOT NULL,
                summary    TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            );
        """)


# ── Persona ──────────────────────────────────────────────────────────────────

def getGuildPersona(guild_id: str) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT persona FROM guild_personas WHERE guild_id = ?", (guild_id,)
        ).fetchone()
    return row[0] if row else None


def setGuildPersona(guild_id: str, persona: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO guild_personas(guild_id, persona, updated_at) VALUES(?,?,?) "
            "ON CONFLICT(guild_id) DO UPDATE SET persona=excluded.persona, updated_at=excluded.updated_at",
            (guild_id, persona, datetime.utcnow().isoformat()),
        )


# ── Guild memory ─────────────────────────────────────────────────────────────

def getGuildMemory(guild_id: str) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT summary FROM guild_memories WHERE guild_id = ?", (guild_id,)
        ).fetchone()
    return row[0] if row else None


def setGuildMemory(guild_id: str, summary: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO guild_memories(guild_id, summary, updated_at) VALUES(?,?,?) "
            "ON CONFLICT(guild_id) DO UPDATE SET summary=excluded.summary, updated_at=excluded.updated_at",
            (guild_id, summary, datetime.utcnow().isoformat()),
        )


# ── User memory ──────────────────────────────────────────────────────────────

def getUserMemory(guild_id: str, user_id: str) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT summary FROM user_memories WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        ).fetchone()
    return row[0] if row else None


def setUserMemory(guild_id: str, user_id: str, summary: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO user_memories(guild_id, user_id, summary, updated_at) VALUES(?,?,?,?) "
            "ON CONFLICT(guild_id, user_id) DO UPDATE SET summary=excluded.summary, updated_at=excluded.updated_at",
            (guild_id, user_id, summary, datetime.utcnow().isoformat()),
        )
