# VeloxCord

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/veloxcord)](https://pypi.org/project/veloxcord/)

**VeloxCord** is an async Discord API wrapper for Python 3.11+.

---

## Installation

```bash
pip install veloxcord
```

**Requirements:** Python 3.11+, aiohttp >= 3.9.0

---

## Quick Start

```python
import veloxcord

intents = veloxcord.Intents.default()
intents = veloxcord.Intents(
    intents.value | veloxcord.Intents.MESSAGE_CONTENT
)

client = veloxcord.Client(intents=intents)

@client.on(veloxcord.EventType.MESSAGE_CREATE)
async def on_message(message: veloxcord.Message):
    if message.content == "!ping":
        await message.channel.send("Pong!")

client.run("YOUR_BOT_TOKEN")
```

Running inside an existing event loop:

```python
import asyncio
import veloxcord

client = veloxcord.Client(intents=veloxcord.Intents.default())

async def main():
    await client.start("YOUR_BOT_TOKEN")

asyncio.run(main())
```

---

## Intents

Intents tell Discord which events to send your bot.

```python
# Default set (no privileged intents)
intents = veloxcord.Intents.default()

# Add MESSAGE_CONTENT (privileged — enable in Developer Portal)
intents = veloxcord.Intents(
    intents.value | veloxcord.Intents.MESSAGE_CONTENT
)

# All intents (including privileged)
intents = veloxcord.Intents.all()

# Manual combination
intents = veloxcord.Intents(
    veloxcord.Intents.GUILDS | veloxcord.Intents.GUILD_MESSAGES
)
```

| Intent | Description |
|--------|-------------|
| `GUILDS` | Server create/delete/update |
| `GUILD_MEMBERS` ⚠️ | Member join/leave |
| `GUILD_MESSAGES` | Messages in server channels |
| `MESSAGE_CONTENT` ⚠️ | Message text content |
| `GUILD_MESSAGE_REACTIONS` | Reactions |
| `DIRECT_MESSAGES` | DMs |
| `GUILD_VOICE_STATES` | Voice states |
| `GUILD_PRESENCES` ⚠️ | User presence/status |
| `GUILD_MODERATION` | Bans, moderation |
| `GUILD_SCHEDULED_EVENTS` | Scheduled events |

> ⚠️ Privileged intents must be enabled on the [Discord Developer Portal](https://discord.com/developers/applications).

---

## Client

```python
client = veloxcord.Client(
    intents=intents,
    prefix="!",              # str or list[str] — for prefix commands
    case_insensitive=False,  # ignore case for prefix commands
    owner_id=None,           # int | None
    cache_config=None,       # CacheConfig | None
    shard_ids=None,          # list[int] | None
    shard_count=None,        # int | None
)
```

**Useful properties:**

```python
client.user           # Bot user (available after READY)
client.latency        # Gateway latency in seconds
client.guilds         # All cached guilds
client.is_ready       # bool
client.cache          # CacheStore
```

**Fetching objects:**

```python
guild   = client.get_guild(guild_id)       # from cache
channel = client.get_channel(channel_id)   # from cache
user    = client.get_user(user_id)         # from cache

guild   = await client.fetch_guild(guild_id)    # HTTP request
channel = await client.fetch_channel(channel_id)
user    = await client.fetch_user(user_id)
```

**Other methods:**

```python
await client.sync_commands()                    # sync slash commands globally
await client.sync_commands(guild_id=123456789)  # sync to one guild

await client.change_presence(
    status=veloxcord.Status.ONLINE,
    activity_name="watching stuff",
    activity_type=veloxcord.ActivityType.WATCHING,
)

await client.close()  # stop the bot
```

---

## Events

```python
# Listen to an event
@client.on(veloxcord.EventType.MESSAGE_CREATE)
async def on_message(message: veloxcord.Message):
    print(f"{message.author.username}: {message.content}")

# Fire only once
@client.once(veloxcord.EventType.READY)
async def on_ready(user: veloxcord.User):
    print(f"Logged in as {user.username}")
    await client.sync_commands()

# With priority (higher = called first)
@client.on(veloxcord.EventType.GUILD_CREATE, priority=10)
async def on_guild(guild: veloxcord.Guild):
    print(f"Joined: {guild.name}")

# Wait for a specific event
msg = await client.wait_for(
    veloxcord.EventType.MESSAGE_CREATE,
    check=lambda m: m.author.id == 123456789,
    timeout=30.0,
)
```

**Main event types:**

| EventType | Handler argument |
|-----------|-----------------|
| `READY` | `User` |
| `MESSAGE_CREATE` | `Message` |
| `MESSAGE_UPDATE` | `Message` |
| `MESSAGE_DELETE` | `Message \| dict` |
| `GUILD_CREATE` | `Guild` |
| `GUILD_MEMBER_ADD` | `Member` |
| `INTERACTION_CREATE` | `Interaction` |
| `ERROR` | `Exception` |

---

## Slash Commands

```python
@client.slash_command(name="ping", description="Check latency")
async def ping(ctx: veloxcord.SlashContext):
    await ctx.respond(f"Pong! {client.latency * 1000:.1f}ms")

# Guild-only command
@client.slash_command(name="secret", description="Secret", guild_ids=[123456789])
async def secret(ctx: veloxcord.SlashContext):
    await ctx.respond("Only here!", ephemeral=True)
```

**SlashContext:**

```python
async def my_command(ctx: veloxcord.SlashContext):
    ctx.author      # Member | User
    ctx.guild_id    # int | None
    ctx.channel_id  # int

    await ctx.respond("Hello!", ephemeral=True)
    await ctx.respond(embeds=[embed])
    await ctx.defer()           # use if processing takes > 3s
    await ctx.followup("Done!")
    await ctx.send_modal(modal)
```

> **Auto-defer:** if your command doesn't respond within 2 seconds, VeloxCord automatically defers it.

---

## Prefix Commands

```python
intents = veloxcord.Intents.default()
intents = veloxcord.Intents(
    intents.value | veloxcord.Intents.MESSAGE_CONTENT
)

client = veloxcord.Client(intents=intents, prefix="!")

@client.command(name="ping")
async def ping(ctx: veloxcord.PrefixContext):
    await ctx.respond("Pong!")

@client.command(name="say", aliases=["echo"])
async def say(ctx: veloxcord.PrefixContext):
    await ctx.respond(" ".join(ctx.args))
```

---

## Components (Buttons & Selects)

```python
# Build a button
button = (
    veloxcord.ButtonBuilder()
    .primary()
    .label("Click me")
    .custom_id("my_button")
    .build()
)

row = veloxcord.ActionRowBuilder().add_button(button).build()

await ctx.respond("Here:", components=[row])

# Handle the button click
@client.on_component("my_button")
async def handle_button(ctx: veloxcord.ComponentContext):
    await ctx.respond("Clicked!", ephemeral=True)

# Handle by pattern
@client.on_component(pattern=r"page_\d+")
async def handle_page(ctx: veloxcord.ComponentContext):
    await ctx.respond(f"Page {ctx.custom_id.split('_')[1]}")
```

**Button styles:** `.primary()` `.secondary()` `.success()` `.danger()` `.link(url)`

**Select menu:**

```python
select = (
    veloxcord.SelectMenuBuilder()
    .custom_id("color")
    .placeholder("Pick a color")
    .option("Red", "red", emoji="🔴")
    .option("Green", "green", emoji="🟢")
    .option("Blue", "blue", emoji="🔵")
    .build()
)
```

---

## Modals

```python
@client.slash_command(name="feedback", description="Leave feedback")
async def feedback_cmd(ctx: veloxcord.SlashContext):
    modal = (
        veloxcord.ModalBuilder()
        .custom_id("feedback")
        .title("Leave Feedback")
        .short_text("name", "Your name")
        .paragraph_text("message", "Your message", required=False)
        .build()
    )
    await ctx.send_modal(modal)

@client.on_modal("feedback")
async def handle_feedback(ctx: veloxcord.ModalContext):
    name = ctx.get_value("name")
    msg  = ctx.get_value("message")
    await ctx.respond(f"Thanks, {name}!", ephemeral=True)
```

---

## Embeds

```python
embed = (
    veloxcord.EmbedBuilder()
    .title("Hello!")
    .description("This is an embed.")
    .color(0x5865F2)
    .field("Field 1", "Value", inline=True)
    .field("Field 2", "Value", inline=True)
    .footer("Footer text")
    .timestamp()
    .build()
)

await ctx.respond(embeds=[embed])
```

---

## Checks & Cooldowns

```python
from veloxcord import BucketType

# Restrict to servers only
@client.slash_command(name="kick")
@veloxcord.guild_only()
async def kick(ctx): ...

# Require permissions
@client.slash_command(name="ban")
@veloxcord.require_permissions("ban_members")
async def ban(ctx): ...

# Owner only
@client.slash_command(name="shutdown")
@veloxcord.is_owner()
async def shutdown(ctx):
    await client.close()

# Cooldown: once per 5 seconds per user
@client.slash_command(name="daily")
@veloxcord.cooldown(rate=1, per=86400, bucket=BucketType.USER)
async def daily(ctx):
    await ctx.respond("Here's your daily reward!")

# Handle cooldown errors
@client.on("COMMAND_ERROR")
async def on_error(exc, ctx):
    if isinstance(exc, veloxcord.CommandOnCooldown):
        await ctx.respond(f"Wait {exc.retry_after:.1f}s!", ephemeral=True)
```

---

## Error Handling

```python
@client.on("ERROR")
async def on_error(exc: Exception):
    if isinstance(exc, veloxcord.RateLimited):
        print(f"Rate limited, retry after {exc.retry_after}s")
    elif isinstance(exc, veloxcord.Forbidden):
        print("Missing permissions")

# Try/except for HTTP calls
try:
    guild = await client.fetch_guild(123456)
except veloxcord.NotFound:
    print("Guild not found")
except veloxcord.Forbidden:
    print("No access")
except veloxcord.HTTPException as e:
    print(f"HTTP {e.status}: {e.message}")
```

**Exception hierarchy:**

```
VeloxException
├── HTTPException
│   ├── BadRequest (400)
│   ├── Unauthorized (401)
│   ├── Forbidden (403)
│   ├── NotFound (404)
│   └── RateLimited (429)
├── GatewayException
│   ├── AuthenticationFailed
│   └── DisallowedIntents
└── CommandException
    ├── CommandOnCooldown
    ├── MissingPermissions
    └── CheckFailure
```

---

## Cache

```python
cache_config = veloxcord.CacheConfig(
    guild_max_size=1024,
    message_max_size=1024,
    member_max_size=65536,
    message_ttl=1800.0,   # seconds, None = forever
    member_ttl=3600.0,
)

client = veloxcord.Client(intents=intents, cache_config=cache_config)

# Direct access
client.cache.get_guild(id)
client.cache.get_channel(id)
client.cache.get_user(id)
client.cache.get_message(id)
client.cache.get_member(guild_id, user_id)
```

---

## License

MIT — see [LICENSE](LICENSE).
