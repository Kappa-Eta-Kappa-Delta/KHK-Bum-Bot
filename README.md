# KHK Bum Bot

A Discord bot that fills out the KHK excuse form. Members run `/excuse` with a
reason, and the bot posts back a filled `.docx` addressed to the chapter, signed
with the invoker's Discord nickname and dated today.

## What `/excuse` does

`/excuse body:<reason>` produces a copy of `KHK Excuse Form.docx` with three
substitutions:

| Template placeholder     | Filled with                                              |
| ------------------------ | -------------------------------------------------------- |
| `Month day, Year`        | Today's date, e.g. `July 22, 2026`                       |
| `xyz`                    | The `body` argument (goes in "for reasons ___.")         |
| `[insert member name]`   | The invoker's Discord nickname (falls back to username)  |

The filled file is uploaded to the same channel as `<nickname>_excuse_<YYYY-MM-DD>.docx`.

## Prerequisites

- Python 3.10 or newer (developed on 3.14).
- A Discord account with permission to create applications and invite bots to
  the target server.

## First-time setup

### 1. Create the Discord application and bot

1. Go to <https://discord.com/developers/applications> and click **New Application**.
2. Under **Bot**, click **Add Bot** and copy the **Token** (this is what goes in `.env`).
   You can regenerate it if you lose it — treat it like a password.
3. Under **OAuth2 → URL Generator**:
   - Scopes: check **`bot`** and **`applications.commands`**.
   - Bot Permissions: check **View Channels**, **Send Messages**, **Attach Files**,
     **Embed Links**, and **Use Slash Commands**.
   - Copy the generated URL and open it to invite the bot to your server.

### 2. Install dependencies

From the repo root:

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure `.env`

Copy `.env.example` to `.env` and fill it in:

```dotenv
DISCORD_TOKEN=your-bot-token-here
# Optional: set to your chapter server's guild ID for instant slash-command
# availability. Leave blank to publish globally (takes up to ~1 hour to appear).
DISCORD_GUILD_ID=
```

To grab a guild ID: enable Developer Mode in Discord (Settings → Advanced),
right-click the server icon, **Copy Server ID**.

> `.env` is gitignored — never commit it.

### 4. Run it

```powershell
python bot.py
```

When it prints `Logged in as ...; slash commands synced (...)`, the `/excuse`
command is live. If you set `DISCORD_GUILD_ID`, it shows up in that server
immediately; without it, allow up to an hour for Discord to propagate globally.

## Keeping it running

The bot needs to be running for slash commands to respond. Options:

### Windows (Task Scheduler)

1. Open **Task Scheduler → Create Task**.
2. **General**: check *Run whether user is logged on or not* and *Run with
   highest privileges*.
3. **Triggers**: add *At startup* (and optionally *At log on*).
4. **Actions**: *Start a program*
   - Program: `python.exe` (full path, e.g. `C:\Users\jdesi\AppData\Local\Programs\Python\Python314-arm64\python.exe`)
   - Arguments: `bot.py`
   - Start in: the repo path (`C:\Users\jdesi\OneDrive\Documents\School\Coding\KHK-Bum-Bot`)
5. **Settings**: enable *If the task fails, restart every 1 minute* (a couple of
   retries covers transient network hiccups).

### Windows (NSSM — run as a service)

If you want a proper background service on Windows:

```powershell
# One-time: install NSSM (https://nssm.cc/) and put nssm.exe on PATH.
nssm install KHKBumBot "C:\path\to\python.exe" "bot.py"
nssm set KHKBumBot AppDirectory "C:\Users\jdesi\OneDrive\Documents\School\Coding\KHK-Bum-Bot"
nssm start KHKBumBot
```

### Linux (systemd — for a Raspberry Pi or home server)

Create `/etc/systemd/system/khk-bum-bot.service`:

```ini
[Unit]
Description=KHK Bum Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/khk-bum-bot
ExecStart=/usr/bin/python3 bot.py
EnvironmentFile=/opt/khk-bum-bot/.env
Restart=on-failure
RestartSec=5
User=khkbot

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now khk-bum-bot
journalctl -u khk-bum-bot -f   # tail logs
```

### Cloud hosting

For a hosted setup, any small VPS or PaaS with a persistent Python worker will
work — e.g. Railway, Fly.io, Render, or an Oracle Cloud free-tier VM. Wherever
you host, set `DISCORD_TOKEN` (and optionally `DISCORD_GUILD_ID`) as environment
variables instead of shipping the `.env` file, and make sure `KHK Excuse Form.docx`
is deployed alongside `bot.py`.

## Updating the excuse template

The bot swaps text by exact string match against three placeholders in
`word/document.xml`:

- `<w:t>Month day, Year</w:t>`
- `<w:t>xyz</w:t>`
- `<w:t>[insert member name]</w:t>`

If you edit the template in Word, keep those exact strings on their own text
runs (don't split them by formatting mid-word), or update the substitution
strings in `bot.py` to match.

## Troubleshooting

- **`/excuse` doesn't appear in Discord.** Make sure the bot was invited with
  the `applications.commands` scope. If `DISCORD_GUILD_ID` is unset, global
  sync can take up to an hour — set the guild ID to make it instant during
  testing.
- **`DISCORD_TOKEN is not set`.** Your `.env` is missing, or the process didn't
  load it from the repo root. Confirm you're launching `python bot.py` from
  the repo directory.
- **The bot logs in but can't post.** In the target channel, the bot's role
  needs **Send Messages** and **Attach Files**. Re-invite via the URL generator
  with those permissions checked, or grant them in the channel's role settings.
