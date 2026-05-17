# VeloxCord

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/veloxcord)](https://pypi.org/project/veloxcord/)

**VeloxCord** is a Python library for creating Discord bots. It handles all the communication with Discord for you — you just write the logic.

---

## Table of Contents

- [Installation](#installation)
- [Your First Bot](#your-first-bot)
- [Intents](#intents)
- [Client](#client)
- [Events](#events)
- [Slash Commands](#slash-commands)
- [Prefix Commands](#prefix-commands)
- [Command Groups](#command-groups)
- [Checks & Permissions](#checks--permissions)
- [Cooldowns](#cooldowns)
- [Buttons & Select Menus](#buttons--select-menus)
- [Modals (Popups)](#modals-popups)
- [Embeds](#embeds)
- [Cache](#cache)
- [Error Handling](#error-handling)

---

## Installation

Open your terminal and run:

```bash
pip install veloxcord
```

**Requirements:**
- Python 3.11 or newer
- aiohttp (installed automatically)

---

## Your First Bot

Here is the simplest possible bot. It replies "Pong!" when someone types `!ping`.

```python
import veloxcord

# Step 1: set up intents (what events your bot wants to receive)
intents = veloxcord.Intents.default()
intents = veloxcord.Intents(
    intents.value | veloxcord.Intents.MESSAGE_CONTENT
)

# Step 2: create the client
client = veloxcord.Client(intents=intents)

# Step 3: listen for messages
@client.on(veloxcord.EventType.MESSAGE_CREATE)
async def on_message(message: veloxcord.Message):
    if message.content == "!ping":
        await message.channel.send("Pong!")

# Step 4: run the bot with your token
client.run("YOUR_BOT_TOKEN")
```

> Get your token from the [Discord Developer Portal](https://discord.com/developers/applications). Never share it with anyone.

If you already have an event loop running (for example inside another async program):

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

Intents tell Discord what kinds of events your bot wants to receive. Without the right intents, your bot will not see certain events at all.

```python
# Default intents — good for most bots
intents = veloxcord.Intents.default()

# If you need to read message content (e.g. prefix commands or !ping)
# you must add MESSAGE_CONTENT like this:
intents = veloxcord.Intents.default()
intents = veloxcord.Intents(
    intents.value | veloxcord.Intents.MESSAGE_CONTENT
)

# All intents at once (includes privileged ones)
intents = veloxcord.Intents.all()

# Build your own combination manually
intents = veloxcord.Intents(
    veloxcord.Intents.GUILDS
    | veloxcord.Intents.GUILD_MESSAGES
    | veloxcord.Intents.MESSAGE_CONTENT
)
```

### Intent List

| Intent | What it does |
|--------|-------------|
| `GUILDS` | Server created, deleted, updated |
| `GUILD_MEMBERS` ⚠️ | Members joining or leaving |
| `GUILD_MESSAGES` | Messages sent in server channels |
| `MESSAGE_CONTENT` ⚠️ | Read the actual text of messages |
| `GUILD_MESSAGE_REACTIONS` | Reactions added or removed |
| `DIRECT_MESSAGES` | Direct messages sent to your bot |
| `GUILD_VOICE_STATES` | Users joining/leaving voice channels |
| `GUILD_PRESENCES` ⚠️ | User online/offline status |
| `GUILD_MODERATION` | Bans, timeouts, moderation actions |
| `GUILD_EMOJIS_AND_STICKERS` | Emoji and sticker changes |
| `GUILD_SCHEDULED_EVENTS` | Scheduled event updates |

> ⚠️ **Privileged intents** (`GUILD_MEMBERS`, `GUILD_PRESENCES`, `MESSAGE_CONTENT`) must be manually enabled in the [Discord Developer Portal](https://discord.com/developers/applications) under your app → Bot → Privileged Gateway Intents.

---

## Client

The `Client` is the main object of your bot. Everything goes through it.

```python
client = veloxcord.Client(
    intents=intents,          # required — your Intents object
    prefix="!",               # prefix for text commands, e.g. "!" or ["!", "?"]
    case_insensitive=False,   # if True, !Ping and !ping both work
    owner_id=123456789,       # your Discord user ID (for is_owner() check)
    cache_config=None,        # custom cache settings (see Cache section)
    shard_ids=None,           # for large bots with sharding
    shard_count=None,
)
```

### Properties

```python
client.user         # the bot's own User object (only available after READY fires)
client.latency      # ping to Discord in seconds (multiply by 1000 for ms)
client.guilds       # list of all servers the bot is in (from cache)
client.users        # list of all cached users
client.is_ready     # True once the bot has connected and received READY
client.is_closed    # True if the connection has been closed
client.cache        # direct access to the cache
```

### Getting Objects

```python
# Fast — reads from local cache, no network request
guild   = client.get_guild(guild_id)
channel = client.get_channel(channel_id)
user    = client.get_user(user_id)
message = client.get_message(message_id)

# Slower — makes an HTTP request to Discord
guild   = await client.fetch_guild(guild_id)
channel = await client.fetch_channel(channel_id)
user    = await client.fetch_user(user_id)
```

### Syncing Slash Commands

After registering slash commands you need to sync them with Discord:

```python
# Sync globally (can take up to 1 hour to appear everywhere)
await client.sync_commands()

# Sync to one specific server (appears instantly — great for testing)
await client.sync_commands(guild_id=123456789)
```

### Changing Bot Status

```python
await client.change_presence(
    status=veloxcord.Status.ONLINE,      # ONLINE, IDLE, DND, INVISIBLE
    activity_name="with Python",
    activity_type=veloxcord.ActivityType.PLAYING,  # PLAYING, WATCHING, LISTENING, STREAMING
)
```

### Starting and Stopping

```python
client.run("TOKEN")          # starts the bot (blocks until stopped)
await client.start("TOKEN")  # async version
await client.close()         # gracefully stop the bot
```

---

## Events

Events are things that happen in Discord — a message is sent, someone joins a server, etc. You register functions that get called when an event happens.

```python
# Basic event listener
@client.on(veloxcord.EventType.MESSAGE_CREATE)
async def on_message(message: veloxcord.Message):
    print(f"{message.author.username} said: {message.content}")

# Run only the first time this event fires, then unregister automatically
@client.once(veloxcord.EventType.READY)
async def on_ready(user: veloxcord.User):
    print(f"Bot is online as {user.username}")
    await client.sync_commands()

# Priority: if multiple handlers listen to the same event,
# higher priority runs first (default is 0)
@client.on(veloxcord.EventType.GUILD_CREATE, priority=10)
async def on_guild_join(guild: veloxcord.Guild):
    print(f"Joined server: {guild.name}")
```

### Waiting for an Event

You can pause your code and wait until a specific event happens:

```python
# Wait for the next message from a specific user (timeout after 30 seconds)
try:
    msg = await client.wait_for(
        veloxcord.EventType.MESSAGE_CREATE,
        check=lambda m: m.author.id == 123456789,
        timeout=30.0,
    )
    print(f"Got reply: {msg.content}")
except asyncio.TimeoutError:
    print("User didn't reply in time")
```

### Add/Remove Listeners Manually

```python
async def my_handler(message):
    print(message.content)

client.add_listener(my_handler, veloxcord.EventType.MESSAGE_CREATE)
client.remove_listener(my_handler, veloxcord.EventType.MESSAGE_CREATE)
```

### All Main Event Types

| Event | What triggers it | Handler receives |
|-------|-----------------|-----------------|
| `READY` | Bot connected to Discord | `User` |
| `MESSAGE_CREATE` | New message sent | `Message` |
| `MESSAGE_UPDATE` | Message edited | `Message` |
| `MESSAGE_DELETE` | Message deleted | `Message` or `dict` |
| `GUILD_CREATE` | Bot joins a server | `Guild` |
| `GUILD_UPDATE` | Server settings changed | `Guild` |
| `GUILD_DELETE` | Bot removed from server | `Guild` or `dict` |
| `GUILD_MEMBER_ADD` | User joined server | `Member` |
| `GUILD_MEMBER_REMOVE` | User left server | `Member` or `User` |
| `GUILD_MEMBER_UPDATE` | Member updated (role, nick) | `Member` |
| `CHANNEL_CREATE` | Channel created | `Channel` |
| `CHANNEL_UPDATE` | Channel updated | `Channel` |
| `CHANNEL_DELETE` | Channel deleted | `Channel` |
| `INTERACTION_CREATE` | Any interaction (slash, button, etc.) | `Interaction` |
| `ERROR` | Unhandled exception | `Exception` |

---

## Slash Commands

Slash commands appear in Discord when users type `/`. They are the modern way to make bot commands.

```python
@client.slash_command(name="ping", description="Check if the bot is alive")
async def ping(ctx: veloxcord.SlashContext):
    ms = client.latency * 1000
    await ctx.respond(f"Pong! Latency: {ms:.1f}ms")
```

### Command Options

```python
@client.slash_command(
    name="greet",
    description="Greet someone",
    guild_ids=[123456789],            # only show in these servers (optional)
    default_member_permissions=None,  # permission bitmask (None = everyone)
    dm_permission=True,               # allow in DMs
    nsfw=False,
)
async def greet(ctx: veloxcord.SlashContext):
    await ctx.respond("Hello!")
```

### SlashContext — What You Can Do

```python
async def my_command(ctx: veloxcord.SlashContext):
    # Information about who ran the command
    ctx.author      # the user who used the command (Member or User)
    ctx.user        # same, but always a User object
    ctx.guild_id    # ID of the server (None if used in DMs)
    ctx.channel_id  # ID of the channel
    ctx.guild       # Guild object (None in DMs)

    # Send a reply visible only to the user
    await ctx.respond("Only you can see this!", ephemeral=True)

    # Send a reply with an embed
    await ctx.respond(embeds=[embed])

    # Send a reply with buttons
    await ctx.respond("Choose:", components=[row])

    # If your command takes more than 3 seconds,
    # call defer() first to prevent Discord from showing "failed"
    await ctx.defer(ephemeral=True)
    # ... do slow stuff ...
    await ctx.followup("Done!")

    # Open a modal (popup form)
    await ctx.send_modal(modal)
```

> **Auto-defer:** VeloxCord automatically defers your response if you take longer than 2 seconds, so you don't have to worry about it.

---

## Prefix Commands

Prefix commands are triggered by a message starting with a symbol like `!ping`.

> You must enable the `MESSAGE_CONTENT` intent for these to work, and it must be enabled in the Developer Portal too.

```python
intents = veloxcord.Intents.default()
intents = veloxcord.Intents(
    intents.value | veloxcord.Intents.MESSAGE_CONTENT
)

client = veloxcord.Client(
    intents=intents,
    prefix="!",             # or a list: ["!", "?", ">>"]
    case_insensitive=True,  # !Ping and !ping both work
)

@client.command(name="ping")
async def ping(ctx: veloxcord.PrefixContext):
    await ctx.respond("Pong!")

# aliases let users type !echo instead of !say
@client.command(name="say", aliases=["echo"])
async def say(ctx: veloxcord.PrefixContext):
    # ctx.args is a list of words after the command name
    text = " ".join(ctx.args)
    await ctx.respond(text)
```

### PrefixContext — What You Can Do

```python
async def my_cmd(ctx: veloxcord.PrefixContext):
    ctx.message       # the original Message object
    ctx.prefix        # which prefix was used (e.g. "!")
    ctx.command_name  # name of the command that was called
    ctx.args          # list of arguments as strings: ["hello", "world"]
    ctx.author        # who sent the message (Member or User)
    ctx.channel       # the channel it was sent in
    ctx.guild_id      # server ID (None in DMs)

    await ctx.respond("Sends a reply to the message")
    await ctx.send("Sends a new message to the channel")
```

---

## Command Groups

Group related slash commands together under one name like `/admin kick` or `/admin ban`.

```python
# Create a group
admin = veloxcord.SlashCommandGroup(
    "admin",
    "Admin commands",
    guild_ids=[YOUR_GUILD_ID],  # optional: only in specific servers
)

# Add subcommands to the group
@admin.sub_command("kick", "Kick a member")
async def admin_kick(ctx: veloxcord.SlashContext):
    await ctx.respond("Member kicked!")

@admin.sub_command("ban", "Ban a member")
async def admin_ban(ctx: veloxcord.SlashContext):
    await ctx.respond("Member banned!")

# You can also create subgroups: /admin config prefix
config = admin.sub_group("config", "Bot configuration")

@config.sub_command("prefix", "Change prefix")
async def config_prefix(ctx: veloxcord.SlashContext):
    await ctx.respond("Prefix changed!")

# Register the group with the client
client._slash_commands["admin"] = admin
```

---

## Checks & Permissions

Checks let you restrict who can use a command.

```python
# Only works in servers (not DMs)
@client.slash_command(name="kick")
@veloxcord.guild_only()
async def kick(ctx):
    await ctx.respond("Kicked!")

# Only works in DMs
@client.slash_command(name="private")
@veloxcord.dm_only()
async def private(ctx):
    await ctx.respond("This is private!")

# User must have these permissions in the server
@client.slash_command(name="ban")
@veloxcord.require_permissions("ban_members")
async def ban(ctx):
    await ctx.respond("Banned!")

# Only the bot owner can use this (set owner_id when creating Client)
@client.slash_command(name="shutdown")
@veloxcord.is_owner()
async def shutdown(ctx):
    await ctx.respond("Shutting down...")
    await client.close()

# Custom check — write any condition you want
def is_premium_user(ctx) -> bool:
    PREMIUM_IDS = [111111111, 222222222]
    return ctx.author.id in PREMIUM_IDS

@client.slash_command(name="premium")
@veloxcord.check(is_premium_user)
async def premium(ctx):
    await ctx.respond("Welcome, premium user!")

# Limit how many people can run this at the same time
@client.slash_command(name="render")
@veloxcord.max_concurrency(1, veloxcord.BucketType.USER)
async def render(ctx):
    await ctx.respond("Rendering...")
```

---

## Cooldowns

Cooldowns prevent users from spamming commands.

```python
from veloxcord import BucketType

# Allow 1 use per 24 hours per user
@client.slash_command(name="daily")
@veloxcord.cooldown(rate=1, per=86400, bucket=BucketType.USER)
async def daily(ctx: veloxcord.SlashContext):
    await ctx.respond("Here is your daily reward!")

# Handle the error when someone is on cooldown
@client.on("COMMAND_ERROR")
async def on_command_error(exc, ctx):
    if isinstance(exc, veloxcord.CommandOnCooldown):
        await ctx.respond(
            f"You're on cooldown! Try again in {exc.retry_after:.1f} seconds.",
            ephemeral=True
        )
```

### Bucket Types

| BucketType | Cooldown applies per... |
|------------|------------------------|
| `USER` | Each user separately |
| `GUILD` | The whole server |
| `CHANNEL` | Each channel separately |
| `GLOBAL` | Everyone globally |

---

## Buttons & Select Menus

Buttons and select menus are interactive components you attach to messages.

### Buttons

```python
@client.slash_command(name="vote", description="Cast a vote")
async def vote(ctx: veloxcord.SlashContext):
    yes_btn = (
        veloxcord.ButtonBuilder()
        .success()
        .label("Yes")
        .custom_id("vote_yes")
        .emoji("✅")
        .build()
    )
    no_btn = (
        veloxcord.ButtonBuilder()
        .danger()
        .label("No")
        .custom_id("vote_no")
        .emoji("❌")
        .build()
    )

    row = (
        veloxcord.ActionRowBuilder()
        .add_button(yes_btn)
        .add_button(no_btn)
        .build()
    )

    await ctx.respond("Cast your vote:", components=[row])

@client.on_component("vote_yes")
async def on_vote_yes(ctx: veloxcord.ComponentContext):
    await ctx.respond("You voted Yes!", ephemeral=True)

@client.on_component("vote_no")
async def on_vote_no(ctx: veloxcord.ComponentContext):
    await ctx.respond("You voted No!", ephemeral=True)
```

**Button styles:**

| Method | Color | Use for |
|--------|-------|---------|
| `.primary()` | Blue | Main action |
| `.secondary()` | Grey | Less important action |
| `.success()` | Green | Positive action |
| `.danger()` | Red | Destructive action |
| `.link("https://...")` | Grey + arrow | Opens a URL |

**Other button options:**

```python
button = (
    veloxcord.ButtonBuilder()
    .primary()
    .label("Click me")
    .custom_id("my_btn")
    .emoji("🔥")       # add an emoji
    .disabled()        # make it unclickable (greyed out)
    .build()
)
```

### Handle Buttons by Pattern

If you have many buttons with similar IDs (like `page_1`, `page_2`), use a regex pattern:

```python
@client.on_component(pattern=r"page_\d+")
async def handle_page(ctx: veloxcord.ComponentContext):
    page_number = ctx.custom_id.split("_")[1]
    await ctx.respond(f"Showing page {page_number}")
```

### Select Menus (Dropdowns)

```python
select = (
    veloxcord.SelectMenuBuilder()
    .custom_id("color_picker")
    .placeholder("Choose a color...")
    .min_values(1)
    .max_values(1)
    .option("Red",   "red",   description="Warm color",   emoji="🔴")
    .option("Green", "green", description="Nature color",  emoji="🟢")
    .option("Blue",  "blue",  description="Cool color",   emoji="🔵", default=True)
    .build()
)

select_row = veloxcord.ActionRowBuilder().add_select(select).build()
await ctx.respond("Pick a color:", components=[select_row])

@client.on_component("color_picker")
async def on_color_pick(ctx: veloxcord.ComponentContext):
    await ctx.respond(f"You picked: {ctx.custom_id}", ephemeral=True)
```

### ComponentContext — What You Can Do

```python
async def handler(ctx: veloxcord.ComponentContext):
    ctx.custom_id    # the custom_id of the button/select that was clicked
    ctx.author       # who clicked it
    ctx.guild_id     # server ID

    await ctx.respond("Reply to the interaction")
    await ctx.defer()
    await ctx.followup("Done!")
    await ctx.update_message(content="Updated!")  # edit the original message
```

---

## Modals (Popups)

Modals are popup forms with text fields. They open when a user clicks a button or runs a command.

```python
@client.slash_command(name="feedback", description="Send us your feedback")
async def feedback_cmd(ctx: veloxcord.SlashContext):
    modal = (
        veloxcord.ModalBuilder()
        .custom_id("feedback_form")
        .title("Send Feedback")
        .short_text(
            custom_id="subject",
            label="Subject",
            placeholder="What is this about?",
            required=True,
            min_length=5,
            max_length=100,
        )
        .paragraph_text(
            custom_id="body",
            label="Your message",
            placeholder="Tell us more...",
            required=False,
        )
        .build()
    )
    await ctx.send_modal(modal)

@client.on_modal("feedback_form")
async def handle_feedback(ctx: veloxcord.ModalContext):
    subject = ctx.get_value("subject")
    body    = ctx.get_value("body")
    await ctx.respond(f"Thanks! We got your message about: **{subject}**", ephemeral=True)
```

### ModalContext — What You Can Do

```python
async def handler(ctx: veloxcord.ModalContext):
    ctx.custom_id          # the modal's custom_id
    ctx.values             # dict of all field values: {"subject": "...", "body": "..."}
    ctx.get_value("field") # get one field's value by its custom_id

    await ctx.respond("Thank you!")
    await ctx.defer()
```

---

## Embeds

Embeds are rich message cards with colors, fields, images, and more.

```python
embed = (
    veloxcord.EmbedBuilder()
    .title("Server Stats")
    .description("Here are the current server statistics.")
    .color(0x5865F2)                                    # hex color (Discord blurple)
    .url("https://discord.com")                         # makes the title a clickable link
    .author("My Bot", icon_url="https://i.imgur.com/abc.png")
    .thumbnail("https://i.imgur.com/thumb.png")         # small image top-right
    .image("https://i.imgur.com/big.png")               # large image at the bottom
    .field("Members",  "1,234", inline=True)            # inline fields appear side by side
    .field("Channels", "42",    inline=True)
    .field("About", "A longer field that takes full width.", inline=False)
    .footer("Updated just now", icon_url="https://i.imgur.com/icon.png")
    .timestamp()                                        # adds current time to the footer
    .build()
)

await ctx.respond(embeds=[embed])
```

---

## Cache

VeloxCord automatically caches Discord objects so your bot doesn't make an HTTP request every time it needs a guild or user.

```python
cache_config = veloxcord.CacheConfig(
    guild_max_size=1024,      # max guilds to store
    channel_max_size=4096,
    member_max_size=65536,
    message_max_size=1024,
    user_max_size=65536,

    # How long to keep objects (seconds). None = keep forever.
    member_ttl=3600.0,        # drop members from cache after 1 hour
    message_ttl=1800.0,       # drop messages from cache after 30 minutes
    user_ttl=3600.0,

    disable_message_cache=False,
)

client = veloxcord.Client(intents=intents, cache_config=cache_config)
```

### Reading from Cache

```python
store = client.cache

guild   = store.get_guild(guild_id)
channel = store.get_channel(channel_id)
user    = store.get_user(user_id)
message = store.get_message(message_id)
member  = store.get_member(guild_id, user_id)
role    = store.get_role(role_id)
emoji   = store.get_emoji(emoji_id)

# All objects as dicts
store.guilds    # dict[int, Guild]
store.channels  # dict[int, Channel]
store.users     # dict[int, User]
store.messages  # dict[int, Message]
```

---

## Error Handling

### Global Error Listener

```python
@client.on("ERROR")
async def on_error(exc: Exception):
    if isinstance(exc, veloxcord.RateLimited):
        print(f"Being rate limited! Wait {exc.retry_after} seconds.")
    elif isinstance(exc, veloxcord.Forbidden):
        print("Bot is missing permissions.")
    elif isinstance(exc, veloxcord.NotFound):
        print("Resource not found.")
    else:
        raise exc
```

### Command Error Listener

```python
@client.on("COMMAND_ERROR")
async def on_command_error(exc: Exception, ctx):
    if isinstance(exc, veloxcord.CommandOnCooldown):
        await ctx.respond(f"Slow down! Try again in {exc.retry_after:.1f}s.", ephemeral=True)
    elif isinstance(exc, veloxcord.MissingPermissions):
        missing = ", ".join(exc.missing)
        await ctx.respond(f"You need these permissions: {missing}", ephemeral=True)
    elif isinstance(exc, veloxcord.CheckFailure):
        await ctx.respond(str(exc), ephemeral=True)
```

### Try/Except for HTTP Calls

```python
try:
    guild = await client.fetch_guild(123456789)
except veloxcord.NotFound:
    print("That server doesn't exist or the bot isn't in it.")
except veloxcord.Forbidden:
    print("Bot doesn't have access to that server.")
except veloxcord.HTTPException as e:
    print(f"Something went wrong: HTTP {e.status} — {e.message}")
```

### Exception List

```
VeloxException                    ← base for all errors
├── HTTPException                 ← Discord API returned an error
│   ├── BadRequest        (400)   ← your request was malformed
│   ├── Unauthorized      (401)   ← invalid token
│   ├── Forbidden         (403)   ← bot lacks permissions
│   ├── NotFound          (404)   ← resource doesn't exist
│   ├── RateLimited       (429)   ← too many requests
│   └── ServerError       (5xx)   ← Discord is having issues
├── GatewayException              ← WebSocket connection error
│   ├── AuthenticationFailed      ← bad token on connect
│   ├── DisallowedIntents         ← intent not enabled in portal
│   ├── ShardingRequired          ← bot is too large, needs sharding
│   └── InvalidShard              ← shard config is wrong
└── CommandException              ← command-related errors
    ├── CommandNotFound            ← no command with that name
    ├── CommandOnCooldown          ← user must wait
    ├── MissingPermissions         ← user lacks required perms
    ├── BotMissingPermissions      ← bot lacks required perms
    ├── CheckFailure               ← custom check returned False
    └── InvalidArgument            ← wrong argument type/value
```

---

## License

MIT — see [LICENSE](LICENSE).
