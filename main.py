
import discord
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

with open("chat.txt", "r+") as file: # Load chat context accordingly (chat4.txt, chat3.txt, etc.)
    chat = file.read()
    chat += "\nUser: "
# Get tokens from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
HF_TOKEN = os.getenv('HF_TOKEN')

if not DISCORD_TOKEN or not HF_TOKEN:
    raise ValueError("Please make sure DISCORD_TOKEN and HF_TOKEN are set in your .env file")

# Set up client
client_hf = InferenceClient(token=HF_TOKEN, model="deepseek-ai/DeepSeek-V3-0324")

# === DISCORD SETUP ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# === Ask Hugging Face (Chat Completions) ===
def ask_ai(prompt):
    try:
        completion = client_hf.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("🔥 Error:", e)
        return "Sorry, something went wrong with the AI."

# === Bot Events ===
@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        prompt = chat+message.content.replace(f"<@{client.user.id}>", "").strip()

        if not prompt:
            await message.channel.send("Yes? What do you want to ask?")
            return

        async with message.channel.typing():
            reply = ask_ai(prompt)
            await message.channel.send(reply)

# === Run Bot ===
client.run(DISCORD_TOKEN)