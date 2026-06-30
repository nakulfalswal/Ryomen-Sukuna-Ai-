import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from db import init_db, getGuildPersona, setGuildPersona, getGuildMemory, getUserMemory
from memory import add_message, get_recent_messages, updateUserMemory, updateGuildMemory
from keep_alive import keep_alive

load_dotenv()

# Default persona loaded from chat.txt (fallback when no server-specific persona is set).
# To use a different default, change the filename here.
with open("chat.txt", "r") as f:
    DEFAULT_PERSONA = f.read().strip()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not DISCORD_TOKEN or not HF_TOKEN:
    raise ValueError("Please make sure DISCORD_TOKEN and HF_TOKEN are set in your .env file")

client_hf = InferenceClient(token=HF_TOKEN, model="deepseek-ai/DeepSeek-V3-0324")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ── AI helper ─────────────────────────────────────────────────────────────────

def ask_ai(prompt: str) -> str:
    try:
        completion = client_hf.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("🔥 Error:", e)
        return "Sorry, something went wrong with the AI."


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_prompt(guild_id: str | None, user_id: str, username: str, user_message: str) -> str:
    """
    Assembles the full prompt in the order:
      1. Persona (server-custom or default)
      2. Guild memory summary (if any)
      3. User memory summary (if any)
      4. Recent buffered messages (if any)
      5. Current user message
    """
    if guild_id:
        persona = getGuildPersona(guild_id) or DEFAULT_PERSONA
        guild_memory = getGuildMemory(guild_id)
        user_memory = getUserMemory(guild_id, user_id)
        recent = get_recent_messages(guild_id, user_id)
    else:
        persona = DEFAULT_PERSONA
        guild_memory = user_memory = recent = None

    parts = [persona]
    if guild_memory:
        parts.append(f"\n[Server Memory: {guild_memory}]")
    if user_memory:
        parts.append(f"\n[What you remember about {username}: {user_memory}]")
    if recent:
        parts.append(f"\n[Recent conversation:\n{recent}]")
    parts.append(f"\nUser: {user_message}")

    return "\n".join(parts)


# ── Bot events ─────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    init_db()
    await bot.tree.sync()
    print(f"✅ Bot is online as {bot.user}")
    print("✅ Slash commands synced globally (may take up to 1h to appear everywhere)")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user not in message.mentions:
        return

    guild_id = str(message.guild.id) if message.guild else None
    user_id = str(message.author.id)
    username = message.author.display_name
    user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()

    if not user_message:
        await message.channel.send("Yes? What do you want to ask?")
        return

    # Buffer message and check if summarization threshold is reached
    should_summarize = False
    if guild_id:
        should_summarize = add_message(guild_id, user_id, username, user_message)

    async with message.channel.typing():
        prompt = build_prompt(guild_id, user_id, username, user_message)
        reply = await asyncio.to_thread(ask_ai, prompt)
        await message.channel.send(reply)

    # Run memory updates in the background without blocking the reply
    if should_summarize and guild_id:
        asyncio.create_task(updateUserMemory(guild_id, user_id, ask_ai))
        asyncio.create_task(updateGuildMemory(guild_id, ask_ai))


# ── Slash commands ─────────────────────────────────────────────────────────────

@bot.tree.command(
    name="update_persona",
    description="View or update this server's custom AI persona",
)
@app_commands.describe(new_persona="New persona text (leave blank to view the current one)")
@app_commands.checks.has_permissions(manage_guild=True)
async def update_persona(interaction: discord.Interaction, new_persona: str = None):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used inside a server.", ephemeral=True
        )
        return

    guild_id = str(interaction.guild.id)

    # ── View current persona ──
    if new_persona is None:
        current = getGuildPersona(guild_id)
        if current:
            preview = current[:1900] + ("…" if len(current) > 1900 else "")
            await interaction.response.send_message(
                f"**Current server persona:**\n```\n{preview}\n```\n"
                "Use `/update_persona new_persona:<text>` to change it.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "No custom persona set — using the **default** persona.\n\n"
                "Use `/update_persona new_persona:<text>` to set one.",
                ephemeral=True,
            )
        return

    # ── Update persona ──
    if len(new_persona) > 2000:
        await interaction.response.send_message(
            f"❌ Persona too long ({len(new_persona)} chars). Maximum is 2000 characters.",
            ephemeral=True,
        )
        return

    setGuildPersona(guild_id, new_persona)
    await interaction.response.send_message(
        f"✅ Server persona updated ({len(new_persona)} chars). "
        "The bot will use it for all new messages in this server.",
        ephemeral=True,
    )


@update_persona.error
async def update_persona_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need the **Manage Server** permission to change the persona.",
            ephemeral=True,
        )


# ── Run ────────────────────────────────────────────────────────────────────────

keep_alive()
bot.run(DISCORD_TOKEN)
