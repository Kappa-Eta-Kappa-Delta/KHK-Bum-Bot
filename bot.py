import io
import os
import re
import sys
import zipfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "KHK Excuse Form.docx"
GUILD_ID_RAW = os.environ.get("DISCORD_GUILD_ID")

if not TEMPLATE_PATH.exists():
    sys.exit(f"Template not found at {TEMPLATE_PATH}")

TEMPLATE_BYTES = TEMPLATE_PATH.read_bytes()


def _format_date(d: date) -> str:
    return f"{d:%B} {d.day}, {d:%Y}"


def _sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    return cleaned or "member"


def build_excuse_docx(nickname: str, body: str, today: date) -> bytes:
    # Normalize whitespace so pasted newlines don't break the sentence flow.
    body_clean = re.sub(r"\s+", " ", body).strip()
    date_str = _format_date(today)

    src = io.BytesIO(TEMPLATE_BYTES)
    dst = io.BytesIO()

    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                xml = data.decode("utf-8")
                xml = xml.replace(
                    "<w:t>Month day, Year</w:t>",
                    f"<w:t>{xml_escape(date_str)}</w:t>",
                )
                xml = xml.replace(
                    "<w:t>xyz</w:t>",
                    f'<w:t xml:space="preserve">{xml_escape(body_clean)}</w:t>',
                )
                xml = xml.replace(
                    "<w:t>[insert member name]</w:t>",
                    f'<w:t xml:space="preserve">{xml_escape(nickname)}</w:t>',
                )
                data = xml.encode("utf-8")
            new_info = zipfile.ZipInfo(item.filename, date_time=item.date_time)
            new_info.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(new_info, data)

    return dst.getvalue()


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def _display_name(interaction: discord.Interaction) -> str:
    # Member.display_name returns the guild nickname if set, else global name.
    return interaction.user.display_name


@tree.command(name="excuse", description="Generate a KHK excuse form addressed to the chapter.")
@app_commands.describe(body="Fill this out for the general body of your letter.")
async def excuse(interaction: discord.Interaction, body: str):
    nickname = _display_name(interaction)
    today = date.today()
    docx_bytes = build_excuse_docx(nickname, body, today)
    filename = f"{_sanitize_filename(nickname)}_excuse_{today.isoformat()}.docx"
    attachment = discord.File(io.BytesIO(docx_bytes), filename=filename)
    await interaction.response.send_message(
        content=f"Excuse form for **{nickname}**:",
        file=attachment,
    )


@client.event
async def on_ready():
    if GUILD_ID_RAW:
        guild = discord.Object(id=int(GUILD_ID_RAW))
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        scope = f"guild {GUILD_ID_RAW}"
    else:
        await tree.sync()
        scope = "global"
    print(f"Logged in as {client.user} (id={client.user.id}); slash commands synced ({scope}).")


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        sys.exit("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    client.run(token)
