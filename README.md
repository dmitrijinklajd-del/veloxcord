# VeloxCord

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/veloxcord)](https://pypi.org/project/veloxcord/)

**VeloxCord** — production-ready асинхронная обёртка над Discord API для Python 3.11+.

Библиотека предоставляет полный доступ к Discord API: слэш-команды, prefix-команды, компоненты, модальные окна, кэширование с LRU/TTL, sharding, gateway с автоматическим reconnect и heartbeat, rate-limit менеджер и гибкий событийный диспетчер.

---

## Содержание

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Client](#client)
- [Intents](#intents)
- [События (Events)](#события-events)
- [Slash-команды](#slash-команды)
- [Prefix-команды](#prefix-команды)
- [Группы команд](#группы-команд)
- [Context Menu-команды](#context-menu-команды)
- [Декораторы и проверки](#декораторы-и-проверки)
- [Cooldown](#cooldown)
- [Builders](#builders)
- [Компоненты (Buttons, Select)](#компоненты-buttons-select)
- [Модальные окна (Modals)](#модальные-окна-modals)
- [Кэш](#кэш)
- [Middleware](#middleware)
- [Модели](#модели)
- [Обработка ошибок](#обработка-ошибок)
- [Архитектура](#архитектура)

---

## Установка

```bash
pip install veloxcord
```

**Зависимости:**
- Python 3.11+
- aiohttp >= 3.9.0

---

## Быстрый старт

```python
import veloxcord

client = veloxcord.Client(intents=veloxcord.Intents.default())

@client.on(veloxcord.EventType.MESSAGE_CREATE)
async def on_message(message: veloxcord.Message):
    if message.content == "!ping":
        await message.channel.send("Pong!")

client.run("YOUR_BOT_TOKEN")
```

Если нужно запустить бота внутри уже работающего event loop:

```python
import asyncio
import veloxcord

client = veloxcord.Client(intents=veloxcord.Intents.default())

async def main():
    await client.start("YOUR_BOT_TOKEN")

asyncio.run(main())
```

---

## Client

`veloxcord.Client` — центральная точка входа в библиотеку.

### Конструктор

```python
client = veloxcord.Client(
    intents=veloxcord.Intents.default(),
    cache_config=None,          # CacheConfig | None
    shard_ids=None,             # list[int] | None
    shard_count=None,           # int | None
    owner_id=None,              # int | None
    owner_ids=None,             # list[int] | None
    prefix=None,                # str | list[str] | None — для prefix-команд
    case_insensitive=False,     # bool — регистр prefix-команд
)
```

### Свойства

| Свойство | Тип | Описание |
|---|---|---|
| `client.user` | `User \| None` | Пользователь бота (доступен после READY) |
| `client.application_id` | `int \| None` | ID приложения |
| `client.latency` | `float` | Задержка gateway в секундах |
| `client.guilds` | `list[Guild]` | Все серверы из кэша |
| `client.users` | `list[User]` | Все пользователи из кэша |
| `client.is_ready` | `bool` | Бот готов к работе |
| `client.is_closed` | `bool` | Соединение закрыто |
| `client.cache` | `CacheStore` | Доступ к кэшу |

### Методы получения объектов

```python
guild   = client.get_guild(guild_id)      # из кэша
channel = client.get_channel(channel_id)  # из кэша
user    = client.get_user(user_id)        # из кэша
message = client.get_message(message_id)  # из кэша

guild   = await client.fetch_guild(guild_id)    # HTTP-запрос
channel = await client.fetch_channel(channel_id)
user    = await client.fetch_user(user_id)
```

### Синхронизация команд

```python
# Синхронизировать все команды
await client.sync_commands()

# Синхронизировать в конкретный сервер
await client.sync_commands(guild_id=123456789)
```

### Управление статусом

```python
await client.change_presence(
    status=veloxcord.Status.ONLINE,        # ONLINE, IDLE, DND, INVISIBLE
    activity_name="watching the void",
    activity_type=veloxcord.ActivityType.WATCHING,
    activity_url=None,                     # для STREAMING
)
```

### Запуск и остановка

```python
client.run("TOKEN")          # синхронный запуск (блокирует поток)
await client.start("TOKEN")  # асинхронный запуск
await client.close()         # остановка
```

---

## Intents

Intents определяют, какие события Discord будет присылать боту.

```python
# Стандартный набор (без привилегированных)
intents = veloxcord.Intents.default()

# Все интенты (включая привилегированные)
intents = veloxcord.Intents.all()

# Только привилегированные: GUILD_MEMBERS, GUILD_PRESENCES, MESSAGE_CONTENT
intents = veloxcord.Intents.privileged()

# Составной интент вручную
intents = veloxcord.Intents(
    veloxcord.Intents.GUILDS
    | veloxcord.Intents.GUILD_MESSAGES
    | veloxcord.Intents.MESSAGE_CONTENT
)
```

### Таблица интентов

| Константа | Описание |
|---|---|
| `GUILDS` | Создание/удаление/обновление серверов |
| `GUILD_MEMBERS` ⚠️ | Вход/выход участников |
| `GUILD_MODERATION` | Банлисты, модерация |
| `GUILD_EMOJIS_AND_STICKERS` | Эмодзи и стикеры |
| `GUILD_MESSAGES` | Сообщения в серверных каналах |
| `MESSAGE_CONTENT` ⚠️ | Содержимое сообщений |
| `GUILD_MESSAGE_REACTIONS` | Реакции |
| `DIRECT_MESSAGES` | Личные сообщения |
| `GUILD_VOICE_STATES` | Голосовые состояния |
| `GUILD_PRESENCES` ⚠️ | Статусы пользователей |
| `GUILD_SCHEDULED_EVENTS` | Запланированные события |

> ⚠️ Привилегированные интенты — нужно включить на [Discord Developer Portal](https://discord.com/developers/applications).

---

## События (Events)

### Регистрация обработчика

```python
# Через декоратор
@client.on(veloxcord.EventType.MESSAGE_CREATE)
async def on_message(message: veloxcord.Message):
    print(f"[{message.author.username}]: {message.content}")

# С приоритетом (больше = раньше вызывается)
@client.on(veloxcord.EventType.GUILD_CREATE, priority=10)
async def on_guild_create(guild: veloxcord.Guild):
    print(f"Joined guild: {guild.name}")

# Вызвать только один раз
@client.once(veloxcord.EventType.READY)
async def on_ready(user: veloxcord.User):
    print(f"Logged in as {user.username}")
    await client.sync_commands()

# Алиас — client.listen()
@client.listen("MESSAGE_CREATE")
async def handler(message):
    ...
```

### Программная подписка

```python
async def my_handler(message):
    ...

client.add_listener(my_handler, veloxcord.EventType.MESSAGE_CREATE)
client.remove_listener(my_handler, veloxcord.EventType.MESSAGE_CREATE)
```

### Ожидание события

```python
# Ждать следующего сообщения от конкретного пользователя
msg = await client.wait_for(
    veloxcord.EventType.MESSAGE_CREATE,
    check=lambda m: m.author.id == 123456789,
    timeout=30.0,  # секунды, None = бесконечно
)
```

### Основные EventType

| EventType | Аргумент обработчика |
|---|---|
| `READY` | `User` |
| `MESSAGE_CREATE` | `Message` |
| `MESSAGE_UPDATE` | `Message` |
| `MESSAGE_DELETE` | `Message \| dict` |
| `GUILD_CREATE` | `Guild` |
| `GUILD_UPDATE` | `Guild` |
| `GUILD_DELETE` | `Guild \| dict` |
| `GUILD_MEMBER_ADD` | `Member` |
| `GUILD_MEMBER_REMOVE` | `Member \| User` |
| `GUILD_MEMBER_UPDATE` | `Member` |
| `CHANNEL_CREATE` | `TextChannel \| VoiceChannel \| ...` |
| `CHANNEL_UPDATE` | аналогично |
| `CHANNEL_DELETE` | аналогично |
| `INTERACTION_CREATE` | `Interaction` |
| `ERROR` | `Exception` |

---

## Slash-команды

### Простая команда

```python
@client.slash_command(name="ping", description="Проверить задержку")
async def ping(ctx: veloxcord.SlashContext):
    await ctx.respond(f"Pong! Задержка: {client.latency * 1000:.1f}мс")
```

### Параметры @client.slash_command

```python
@client.slash_command(
    name="greet",
    description="Поприветствовать пользователя",
    guild_ids=[123456789],                   # только для этих серверов
    options=[...],                           # список SlashCommandOption
    default_member_permissions=None,         # int битовая маска прав
    dm_permission=True,                      # доступна в DM
    nsfw=False,
)
async def greet(ctx: veloxcord.SlashContext):
    ...
```

### SlashContext

```python
async def my_command(ctx: veloxcord.SlashContext):
    # Свойства
    ctx.interaction       # Interaction
    ctx.bot               # Client
    ctx.command_name      # str
    ctx.guild_id          # int | None
    ctx.channel_id        # int
    ctx.author            # Member | User
    ctx.user              # User
    ctx.guild             # Guild | None

    # Ответ
    await ctx.respond("Текст ответа", ephemeral=True)
    await ctx.respond(embeds=[embed])
    await ctx.respond(components=[action_row])

    # Отправить сообщение в канал
    await ctx.send("Сообщение", embeds=[embed])

    # Отложенный ответ (нужен, если обработка > 3с)
    await ctx.defer(ephemeral=True)
    await ctx.followup("Готово!")

    # Открыть модальное окно
    await ctx.send_modal(modal)
```

> **Авто-defer:** если команда не отвечает в течение 2 секунд, VeloxCord автоматически откладывает ответ, чтобы избежать ошибки Discord.

---

## Prefix-команды

```python
client = veloxcord.Client(
    intents=veloxcord.Intents.default() | veloxcord.Intents(veloxcord.Intents.MESSAGE_CONTENT),
    prefix="!",          # или список: ["!", "?", ">>"]
    case_insensitive=True,
)

@client.command(name="ping", description="Pong!")
async def ping(ctx: veloxcord.PrefixContext):
    await ctx.respond("Pong!")

@client.command(name="say", aliases=["echo"])
async def say(ctx: veloxcord.PrefixContext):
    text = " ".join(ctx.args)
    await ctx.respond(text)
```

### PrefixContext

```python
async def my_cmd(ctx: veloxcord.PrefixContext):
    ctx.message        # Message
    ctx.bot            # Client
    ctx.prefix         # str — использованный префикс
    ctx.command_name   # str
    ctx.args           # list[str] — позиционные аргументы
    ctx.kwargs         # dict[str, Any]
    ctx.author         # Member | User
    ctx.channel        # TextChannel | ...
    ctx.guild_id       # int | None

    await ctx.respond("Ответ")  # reply на сообщение
    await ctx.send("Сообщение в канал")
```

---

## Группы команд

```python
admin = veloxcord.SlashCommandGroup(
    "admin",
    "Административные команды",
    guild_ids=[YOUR_GUILD_ID],
)

@admin.sub_command("kick", "Кикнуть участника")
async def admin_kick(ctx: veloxcord.SlashContext):
    await ctx.respond("Участник кикнут!")

@admin.sub_command("ban", "Забанить участника")
async def admin_ban(ctx: veloxcord.SlashContext):
    await ctx.respond("Участник забанен!")

# Подгруппа
config_group = admin.sub_group("config", "Настройки")

@config_group.sub_command("prefix", "Сменить префикс")
async def config_prefix(ctx: veloxcord.SlashContext):
    await ctx.respond("Префикс изменён!")

# Зарегистрировать группу
client._slash_commands["admin"] = admin
```

---

## Context Menu-команды

```python
# Команда на пользователе (ПКМ → Apps)
@client.user_command(name="Профиль")
async def user_profile(ctx: veloxcord.SlashContext):
    await ctx.respond(f"Пользователь: {ctx.interaction.data.resolved}")

# Команда на сообщении (ПКМ → Apps)
@client.message_command(name="Перевести", guild_ids=[123456])
async def translate_message(ctx: veloxcord.SlashContext):
    await ctx.respond("Перевод: ...")
```

---

## Декораторы и проверки

```python
from veloxcord import guild_only, dm_only, require_permissions, is_owner, check, max_concurrency

# Только на серверах
@client.slash_command(name="kick")
@veloxcord.guild_only()
async def kick(ctx):
    ...

# Только в DM
@client.slash_command(name="dm_only_cmd")
@veloxcord.dm_only()
async def dm_cmd(ctx):
    ...

# Требовать права у пользователя
@client.slash_command(name="ban")
@veloxcord.require_permissions("ban_members", "kick_members")
async def ban(ctx):
    ...

# Только владелец
@client.slash_command(name="shutdown")
@veloxcord.is_owner()
async def shutdown(ctx):
    await client.close()

# Кастомная проверка
def is_premium(ctx) -> bool:
    return ctx.author.id in PREMIUM_USERS

@client.slash_command(name="premium")
@veloxcord.check(is_premium)
async def premium(ctx):
    ...

# Ограничение параллельных вызовов
@client.slash_command(name="render")
@veloxcord.max_concurrency(1, veloxcord.BucketType.USER)
async def render(ctx):
    ...
```

---

## Cooldown

```python
from veloxcord import BucketType

# 1 раз в 5 секунд на пользователя
@client.slash_command(name="daily")
@veloxcord.cooldown(rate=1, per=86400, bucket=BucketType.USER)
async def daily(ctx: veloxcord.SlashContext):
    await ctx.respond("Вот твоя ежедневная награда!")

# Обработка ошибки cooldown
@client.on("COMMAND_ERROR")
async def on_error(exc, ctx):
    if isinstance(exc, veloxcord.CommandOnCooldown):
        await ctx.respond(
            f"Подожди ещё {exc.retry_after:.1f}с!",
            ephemeral=True
        )
```

### BucketType

| BucketType | Описание |
|---|---|
| `USER` | Отдельный кулдаун для каждого пользователя |
| `GUILD` | Один кулдаун на весь сервер |
| `CHANNEL` | Один кулдаун на канал |
| `GLOBAL` | Один кулдаун для всех |

---

## Builders

### EmbedBuilder

```python
embed = (
    veloxcord.EmbedBuilder()
    .title("Заголовок")
    .description("Описание **с поддержкой** markdown")
    .color(0x5865F2)
    .url("https://discord.com")
    .author("Имя автора", icon_url="https://...")
    .footer("Текст подвала", icon_url="https://...")
    .thumbnail("https://image.url/thumb.png")
    .image("https://image.url/image.png")
    .field("Поле 1", "Значение", inline=True)
    .field("Поле 2", "Значение", inline=True)
    .timestamp()  # текущее время
    .build()
)
```

### MessageBuilder

```python
message = (
    veloxcord.MessageBuilder()
    .content("Текст сообщения")
    .embed(embed)
    .component(action_row)
    .tts(False)
    .suppress_embeds(False)
    .build()
)
```

### ButtonBuilder

```python
# Основные стили
button = veloxcord.ButtonBuilder().primary().label("Кнопка").custom_id("btn_1").build()
button = veloxcord.ButtonBuilder().secondary().label("Кнопка").custom_id("btn_2").build()
button = veloxcord.ButtonBuilder().success().label("Принять").custom_id("accept").build()
button = veloxcord.ButtonBuilder().danger().label("Удалить").custom_id("delete").build()

# Ссылка
button = veloxcord.ButtonBuilder().link("https://discord.com").label("Discord").build()

# Отключённая кнопка
button = veloxcord.ButtonBuilder().primary().label("Недоступно").custom_id("x").disabled().build()

# С эмодзи
button = veloxcord.ButtonBuilder().primary().label("Огонь").emoji("🔥").custom_id("fire").build()
```

### SelectMenuBuilder

```python
select = (
    veloxcord.SelectMenuBuilder()
    .custom_id("color_select")
    .placeholder("Выбери цвет")
    .min_values(1)
    .max_values(1)
    .option("Красный", "red", description="Цвет страсти", emoji="🔴")
    .option("Зелёный", "green", description="Цвет природы", emoji="🟢")
    .option("Синий", "blue", description="Цвет неба", default=True, emoji="🔵")
    .build()
)
```

### ActionRowBuilder

```python
row = (
    veloxcord.ActionRowBuilder()
    .add_button(button)
    .build()
)

select_row = (
    veloxcord.ActionRowBuilder()
    .add_select(select)
    .build()
)
```

### ModalBuilder

```python
modal = (
    veloxcord.ModalBuilder()
    .custom_id("feedback_form")
    .title("Обратная связь")
    .short_text(
        custom_id="subject",
        label="Тема",
        placeholder="Коротко о проблеме",
        required=True,
        min_length=5,
        max_length=100,
    )
    .paragraph_text(
        custom_id="body",
        label="Описание",
        placeholder="Подробно опишите...",
        required=False,
    )
    .build()
)
```

---

## Компоненты (Buttons, Select)

```python
# Обработчик кнопки по точному custom_id
@client.on_component("accept_btn")
async def handle_accept(ctx: veloxcord.ComponentContext):
    await ctx.respond("Принято!", ephemeral=True)

# Обработчик по regex-паттерну
@client.on_component(pattern=r"page_\d+")
async def handle_page(ctx: veloxcord.ComponentContext):
    page_num = ctx.custom_id.split("_")[1]
    await ctx.respond(f"Страница {page_num}")

# ComponentContext
async def handler(ctx: veloxcord.ComponentContext):
    ctx.custom_id        # str
    ctx.interaction      # Interaction
    ctx.author           # Member | User
    ctx.guild_id         # int | None

    await ctx.respond("Ответ")
    await ctx.defer()
    await ctx.followup("Обновлено!")
    await ctx.update_message(content="Сообщение обновлено")  # обновить оригинал
```

---

## Модальные окна (Modals)

```python
@client.slash_command(name="feedback", description="Оставить отзыв")
async def feedback_cmd(ctx: veloxcord.SlashContext):
    modal = (
        veloxcord.ModalBuilder()
        .custom_id("feedback")
        .title("Оставьте отзыв")
        .short_text("name", "Ваше имя")
        .paragraph_text("message", "Ваш отзыв", required=False)
        .build()
    )
    await ctx.send_modal(modal)

@client.on_modal("feedback")
async def handle_feedback(ctx: veloxcord.ModalContext):
    name    = ctx.get_value("name")
    message = ctx.get_value("message")
    await ctx.respond(f"Спасибо, {name}! Ваш отзыв принят.", ephemeral=True)
```

### ModalContext

```python
async def handler(ctx: veloxcord.ModalContext):
    ctx.custom_id          # str
    ctx.get_value("field") # str | None — значение поля по custom_id
    ctx.values             # dict[str, str] — все поля

    await ctx.respond("Ответ")
    await ctx.defer()
```

---

## Кэш

VeloxCord использует LRU-кэш с поддержкой TTL для всех Discord-объектов.

```python
cache_config = veloxcord.CacheConfig(
    guild_max_size=1024,
    channel_max_size=4096,
    member_max_size=65536,
    message_max_size=1024,
    user_max_size=65536,
    role_max_size=4096,
    emoji_max_size=4096,
    # TTL в секундах (None = бессрочно)
    member_ttl=3600.0,
    message_ttl=1800.0,
    user_ttl=3600.0,
    # Отключить отдельные кэши
    disable_message_cache=False,
)

client = veloxcord.Client(
    intents=veloxcord.Intents.default(),
    cache_config=cache_config,
)
```

### Прямой доступ к кэшу

```python
store = client.cache

store.guilds              # dict[int, Guild]
store.channels            # dict[int, Channel]
store.users               # dict[int, User]
store.messages            # dict[int, Message]

store.get_guild(id)
store.get_channel(id)
store.get_user(id)
store.get_message(id)
store.get_member(guild_id, user_id)
store.get_role(id)
store.get_emoji(id)
```

---

## Middleware

Middleware позволяет перехватывать все события до их диспатча.

```python
from veloxcord.events.middleware import LoggingMiddleware, FilterMiddleware

# Встроенное логирование
client.add_middleware(LoggingMiddleware())

# Фильтрация событий
client.add_middleware(FilterMiddleware(
    allowed_events={"MESSAGE_CREATE", "GUILD_CREATE"}
))

# Кастомный middleware
from veloxcord.events.middleware import MiddlewareChain

class MetricsMiddleware:
    async def __call__(self, event_name: str, data, next_handler):
        # до
        print(f"Event: {event_name}")
        result = await next_handler(event_name, data)
        # после
        return result

client.add_middleware(MetricsMiddleware())
```

---

## Модели

### User

```python
user.id           # int
user.username     # str
user.discriminator # str
user.tag          # str  — "username#0000"
user.avatar       # str | None — hash аватара
user.avatar_url   # str — прямая ссылка на аватар
user.bot          # bool
user.system       # bool
```

### Member

```python
member.user           # User
member.nick           # str | None
member.roles          # list[int] — список ID ролей
member.joined_at      # datetime | None
member.premium_since  # datetime | None
member.pending        # bool
member.permissions    # Permissions | None
```

### Guild

```python
guild.id              # int
guild.name            # str
guild.icon            # str | None
guild.owner_id        # int
guild.member_count    # int
guild.channels        # list[Channel]
guild.members         # list[Member]
guild.roles           # list[Role]
guild.emojis          # list[Emoji]
guild.premium_tier    # PremiumTier
```

### Message

```python
message.id           # int
message.content      # str
message.author       # User
message.member       # Member | None
message.channel_id   # int
message.channel      # TextChannel | None
message.guild_id     # int | None
message.embeds       # list[Embed]
message.attachments  # list[Attachment]
message.reactions    # list[Reaction]
message.pinned       # bool

await message.reply("Ответ")
await message.delete()
await message.edit(content="Обновлено")
await message.pin()
await message.add_reaction("👍")
```

### TextChannel / VoiceChannel / CategoryChannel / DMChannel

```python
channel.id        # int
channel.name      # str
channel.guild_id  # int | None
channel.position  # int

await channel.send("Привет!")
await channel.send(embeds=[embed], components=[row])
await channel.fetch_message(message_id)
await channel.purge(limit=100)
```

### Embed

```python
embed.title        # str | None
embed.description  # str | None
embed.color        # int | None
embed.url          # str | None
embed.fields       # list[EmbedField]
embed.footer       # EmbedFooter | None
embed.author       # EmbedAuthor | None
embed.thumbnail    # EmbedMedia | None
embed.image        # EmbedMedia | None
embed.timestamp    # str | None

embed_dict = embed.to_dict()
```

### Role

```python
role.id          # int
role.name        # str
role.color       # int
role.hoist       # bool — выделена ли в списке участников
role.position    # int
role.permissions # Permissions
role.managed     # bool
role.mentionable # bool
role.mention     # str — "<@&id>"
```

---

## Обработка ошибок

### Иерархия исключений

```
VeloxException
├── HTTPException
│   ├── BadRequest (400)
│   ├── Unauthorized (401)
│   ├── Forbidden (403)
│   ├── NotFound (404)
│   ├── RateLimited (429)
│   └── ServerError (5xx)
├── GatewayException
│   ├── AuthenticationFailed (4004)
│   ├── DisallowedIntents (4014)
│   ├── ShardingRequired (4011)
│   └── InvalidShard (4010)
└── CommandException
    ├── CommandNotFound
    ├── CommandOnCooldown
    ├── MissingPermissions
    ├── BotMissingPermissions
    ├── CheckFailure
    └── InvalidArgument
```

### Пример обработки

```python
import veloxcord

@client.on("ERROR")
async def on_error(exc: Exception):
    if isinstance(exc, veloxcord.RateLimited):
        print(f"Rate limited! Retry after: {exc.retry_after}s")
    elif isinstance(exc, veloxcord.Forbidden):
        print("Нет прав!")
    elif isinstance(exc, veloxcord.NotFound):
        print("Ресурс не найден")
    else:
        raise exc

@client.on("COMMAND_ERROR")
async def on_command_error(exc: Exception, ctx):
    if isinstance(exc, veloxcord.CommandOnCooldown):
        await ctx.respond(f"Кулдаун! Подожди {exc.retry_after:.1f}с", ephemeral=True)
    elif isinstance(exc, veloxcord.MissingPermissions):
        await ctx.respond(f"Нет прав: {', '.join(exc.missing)}", ephemeral=True)
    elif isinstance(exc, veloxcord.CheckFailure):
        await ctx.respond(str(exc), ephemeral=True)

try:
    guild = await client.fetch_guild(123456)
except veloxcord.NotFound:
    print("Сервер не найден")
except veloxcord.Forbidden:
    print("Нет доступа к серверу")
except veloxcord.HTTPException as e:
    print(f"HTTP ошибка {e.status}: {e.message}")
```

---

## Архитектура

```
veloxcord/
├── client.py           — Client: главный класс бота
├── intents.py          — Intents: типизированные флаги намерений
├── flags.py            — Permissions, MessageFlags, UserFlags
├── enums.py            — Все Discord-перечисления
├── errors.py           — Иерархия исключений
├── utils.py            — Вспомогательные функции
│
├── gateway/            — WebSocket-соединение
│   ├── connection.py   — GatewayConnection (heartbeat, reconnect, resume)
│   ├── heartbeat.py    — HeartbeatManager
│   ├── shard.py        — ShardManager
│   └── opcodes.py      — OpCodes
│
├── http/               — Async HTTP-клиент
│   ├── client.py       — HTTPClient (все методы API)
│   ├── endpoints.py    — Route, Endpoints
│   └── ratelimit.py    — RateLimitManager, глобальный rate-limiter
│
├── models/             — Все Discord-сущности
│   ├── base.py         — Snowflake, DiscordModel, Object
│   ├── user.py         — User
│   ├── member.py       — Member
│   ├── guild.py        — Guild, WelcomeScreen
│   ├── channel.py      — TextChannel, VoiceChannel, ...
│   ├── message.py      — Message, MessageReference, Reaction
│   ├── embed.py        — Embed, EmbedField, EmbedFooter, EmbedAuthor
│   ├── role.py         — Role, RoleTags
│   ├── emoji.py        — Emoji, PartialEmoji
│   ├── interaction.py  — Interaction, InteractionData
│   ├── component.py    — ActionRow, Button, SelectMenu, TextInput
│   ├── modal.py        — Modal
│   ├── thread.py       — Thread, ThreadMember
│   ├── scheduled_event.py — GuildScheduledEvent
│   ├── stage.py        — StageInstance
│   ├── webhook.py      — Webhook
│   ├── invite.py       — Invite
│   ├── sticker.py      — Sticker
│   ├── attachment.py   — Attachment, File
│   ├── application.py  — Application
│   └── permissions.py  — PermissionOverwrite
│
├── commands/           — Система команд
│   ├── core.py         — BaseCommand
│   ├── slash.py        — SlashCommand, SlashCommandOption
│   ├── prefix.py       — PrefixCommand, PrefixCommandHandler
│   ├── context_menu.py — UserCommand, MessageCommand
│   ├── group.py        — SlashCommandGroup, SubCommand, SubCommandGroup
│   ├── cooldown.py     — Cooldown, BucketType, CooldownBucket
│   ├── context.py      — PrefixContext, SlashContext, ComponentContext, ModalContext
│   └── decorators.py   — cooldown, guild_only, dm_only, require_permissions, check, ...
│
├── builders/           — Fluent-строители
│   ├── embed.py        — EmbedBuilder
│   ├── message.py      — MessageBuilder
│   ├── button.py       — ButtonBuilder
│   ├── select.py       — SelectMenuBuilder
│   ├── modal.py        — ModalBuilder
│   └── action_row.py   — ActionRowBuilder
│
├── cache/              — LRU-кэш
│   ├── store.py        — CacheStore, CacheConfig
│   └── lru.py          — LRUCache (с поддержкой TTL)
│
├── events/             — Диспетчер событий
│   ├── dispatcher.py   — EventDispatcher, EventListener
│   ├── middleware.py   — MiddlewareChain, LoggingMiddleware, FilterMiddleware
│   └── types.py        — EventType
│
└── voice/              — Голосовой клиент
    └── client.py       — VoiceClient
```

---

## Лицензия

MIT License. Подробнее — см. файл [LICENSE](LICENSE).
