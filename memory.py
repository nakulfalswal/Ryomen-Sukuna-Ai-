import asyncio
from collections import defaultdict
from typing import Callable

from db import getGuildMemory, setGuildMemory, getUserMemory, setUserMemory

# In-memory buffer:  guild_id -> user_id -> [formatted message strings]
_buffer: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

SUMMARIZE_THRESHOLD = 15  # messages per user before summarizing


def add_message(guild_id: str, user_id: str, username: str, content: str) -> bool:
    """Buffer one message. Returns True when summarization should be triggered."""
    _buffer[guild_id][user_id].append(f"{username}: {content}")
    return len(_buffer[guild_id][user_id]) >= SUMMARIZE_THRESHOLD


def get_recent_messages(guild_id: str, user_id: str, limit: int = 10) -> str:
    msgs = _buffer[guild_id][user_id]
    return "\n".join(msgs[-limit:]) if msgs else ""


def _get_all_guild_messages(guild_id: str, limit: int = 40) -> list[str]:
    all_msgs: list[str] = []
    for msgs in _buffer[guild_id].values():
        all_msgs.extend(msgs)
    return all_msgs[-limit:]


async def updateUserMemory(guild_id: str, user_id: str, ask_ai: Callable[[str], str]) -> None:
    """Summarize buffered messages into the user's long-term memory entry."""
    existing = getUserMemory(guild_id, user_id) or ""
    recent = "\n".join(_buffer[guild_id][user_id])

    prompt = (
        "You are a memory assistant for a Discord companion bot. "
        "Produce a concise summary (max 200 words) of what you know about this user. "
        "Capture: preferences, recurring topics, inside jokes, important facts they've mentioned. "
        "Do NOT copy messages verbatim.\n\n"
        f"Existing memory:\n{existing}\n\n"
        f"New messages:\n{recent}\n\n"
        "Updated memory summary:"
    )

    try:
        summary = await asyncio.to_thread(ask_ai, prompt)
        setUserMemory(guild_id, user_id, summary)
    except Exception as e:
        print(f"⚠️  User memory update failed ({user_id}): {e}")
    finally:
        _buffer[guild_id][user_id].clear()


async def updateGuildMemory(guild_id: str, ask_ai: Callable[[str], str]) -> None:
    """Summarize recent cross-user messages into the guild's long-term memory entry."""
    recent_msgs = _get_all_guild_messages(guild_id)
    if not recent_msgs:
        return

    existing = getGuildMemory(guild_id) or ""
    recent = "\n".join(recent_msgs)

    prompt = (
        "You are a memory assistant for a Discord companion bot. "
        "Produce a concise summary (max 200 words) of this server's community. "
        "Capture: server culture, running jokes, common interests, recurring topics. "
        "Do NOT copy messages verbatim.\n\n"
        f"Existing memory:\n{existing}\n\n"
        f"Recent server messages:\n{recent}\n\n"
        "Updated server memory summary:"
    )

    try:
        summary = await asyncio.to_thread(ask_ai, prompt)
        setGuildMemory(guild_id, summary)
    except Exception as e:
        print(f"⚠️  Guild memory update failed ({guild_id}): {e}")
