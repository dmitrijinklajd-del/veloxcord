from __future__ import annotations

__title__ = "veloxcord"
__author__ = "VeloxCord Contributors"
__version__ = "1.0.0"
__license__ = "MIT"

from .client import Client

from .intents import Intents
from .flags import (
    Permissions,
    MessageFlags,
    UserFlags,
    SystemChannelFlags,
    BaseFlags,
)
from .enums import (
    ChannelType,
    MessageType,
    InteractionType,
    ApplicationCommandType,
    ApplicationCommandOptionType,
    ComponentType,
    ButtonStyle,
    TextInputStyle,
    InteractionCallbackType,
    VerificationLevel,
    DefaultMessageNotificationLevel,
    ExplicitContentFilterLevel,
    MFALevel,
    PremiumTier,
    NSFWLevel,
    GuildScheduledEventStatus,
    GuildScheduledEventEntityType,
    StageInstancePrivacyLevel,
    StickerType,
    StickerFormatType,
    InviteTargetType,
    WebhookType,
    VideoQualityMode,
    SortOrderType,
    ForumLayoutType,
    AuditLogEvent,
    EventType,
    OpCode,
    Status,
    ActivityType,
    OverwriteType,
)
from .errors import (
    VeloxException,
    HTTPException,
    NotFound,
    Forbidden,
    Unauthorized,
    BadRequest,
    RateLimited,
    ServerError,
    GatewayException,
    AuthenticationFailed,
    DisallowedIntents,
    ShardingRequired,
    InvalidShard,
    CommandException,
    CommandNotFound,
    CommandOnCooldown,
    MissingPermissions,
    BotMissingPermissions,
    CheckFailure,
    InvalidArgument,
    CacheException,
)
from .utils import (
    snowflake_time,
    time_snowflake,
    parse_timestamp,
    utcnow,
    find,
    get,
    chunk_list,
    parse_mentions,
    build_query_string,
    color_to_int,
    int_to_color_hex,
    escape_markdown,
    format_dt,
    sleep_until,
    MISSING,
)

from .models.base import Snowflake, DiscordModel, Object
from .models.user import User
from .models.member import Member
from .models.role import Role, RoleTags
from .models.emoji import Emoji, PartialEmoji
from .models.guild import Guild, WelcomeScreen, WelcomeScreenChannel
from .models.channel import (
    TextChannel,
    VoiceChannel,
    CategoryChannel,
    DMChannel,
    _channel_from_data,
)
from .models.message import Message, MessageReference, Reaction
from .models.embed import Embed, EmbedField, EmbedFooter, EmbedAuthor, EmbedMedia
from .models.attachment import Attachment, File
from .models.sticker import Sticker, StickerItem
from .models.invite import Invite, InviteGuild
from .models.webhook import Webhook
from .models.permissions import PermissionOverwrite, resolve_permissions
from .models.component import (
    ActionRow,
    Button,
    SelectMenu,
    SelectOption,
    TextInput,
    _component_from_data,
)
from .models.modal import Modal
from .models.interaction import Interaction, InteractionData
from .models.thread import Thread, ThreadMember, ThreadMetadata
from .models.scheduled_event import GuildScheduledEvent, GuildScheduledEventEntityMetadata
from .models.stage import StageInstance
from .models.application import Application, ApplicationInstallParams

from .builders.embed import EmbedBuilder
from .builders.message import MessageBuilder
from .builders.button import ButtonBuilder
from .builders.select import SelectMenuBuilder
from .builders.modal import ModalBuilder
from .builders.action_row import ActionRowBuilder

from .commands.core import BaseCommand
from .commands.slash import SlashCommand, SlashCommandOption
from .commands.context_menu import UserCommand, MessageCommand
from .commands.prefix import PrefixCommand, PrefixCommandHandler
from .commands.group import SlashCommandGroup, SubCommand, SubCommandGroup
from .commands.cooldown import Cooldown, BucketType, CooldownBucket
from .commands.context import PrefixContext, SlashContext, ComponentContext, ModalContext
from .commands.decorators import (
    cooldown,
    guild_only,
    dm_only,
    require_permissions,
    require_bot_permissions,
    check,
    is_owner,
    max_concurrency,
)

from .cache.store import CacheStore, CacheConfig
from .cache.lru import LRUCache

from .events.dispatcher import EventDispatcher, EventListener
from .events.middleware import MiddlewareChain, LoggingMiddleware, FilterMiddleware

from .gateway.connection import GatewayConnection
from .gateway.heartbeat import HeartbeatManager
from .gateway.shard import ShardManager

from .voice.client import VoiceClient

from .http.client import HTTPClient
from .http.ratelimit import RateLimitManager, RateLimitBucket, GlobalRateLimiter
from .http.endpoints import Route, Endpoints

__all__ = [
    "__title__",
    "__author__",
    "__version__",
    "__license__",
    "Client",
    "Intents",
    "Permissions",
    "MessageFlags",
    "UserFlags",
    "SystemChannelFlags",
    "BaseFlags",
    "ChannelType",
    "MessageType",
    "InteractionType",
    "ApplicationCommandType",
    "ApplicationCommandOptionType",
    "ComponentType",
    "ButtonStyle",
    "TextInputStyle",
    "InteractionCallbackType",
    "VerificationLevel",
    "DefaultMessageNotificationLevel",
    "ExplicitContentFilterLevel",
    "MFALevel",
    "PremiumTier",
    "NSFWLevel",
    "GuildScheduledEventStatus",
    "GuildScheduledEventEntityType",
    "StageInstancePrivacyLevel",
    "StickerType",
    "StickerFormatType",
    "InviteTargetType",
    "WebhookType",
    "VideoQualityMode",
    "SortOrderType",
    "ForumLayoutType",
    "AuditLogEvent",
    "EventType",
    "OpCode",
    "Status",
    "ActivityType",
    "OverwriteType",
    "VeloxException",
    "HTTPException",
    "NotFound",
    "Forbidden",
    "Unauthorized",
    "BadRequest",
    "RateLimited",
    "ServerError",
    "GatewayException",
    "AuthenticationFailed",
    "DisallowedIntents",
    "ShardingRequired",
    "InvalidShard",
    "CommandException",
    "CommandNotFound",
    "CommandOnCooldown",
    "MissingPermissions",
    "BotMissingPermissions",
    "CheckFailure",
    "InvalidArgument",
    "CacheException",
    "snowflake_time",
    "time_snowflake",
    "parse_timestamp",
    "utcnow",
    "find",
    "get",
    "chunk_list",
    "parse_mentions",
    "build_query_string",
    "color_to_int",
    "int_to_color_hex",
    "escape_markdown",
    "format_dt",
    "sleep_until",
    "MISSING",
    "Snowflake",
    "DiscordModel",
    "Object",
    "User",
    "Member",
    "Role",
    "RoleTags",
    "Emoji",
    "PartialEmoji",
    "Guild",
    "WelcomeScreen",
    "WelcomeScreenChannel",
    "TextChannel",
    "VoiceChannel",
    "CategoryChannel",
    "DMChannel",
    "_channel_from_data",
    "Message",
    "MessageReference",
    "Reaction",
    "Embed",
    "EmbedField",
    "EmbedFooter",
    "EmbedAuthor",
    "EmbedMedia",
    "Attachment",
    "File",
    "Sticker",
    "StickerItem",
    "Invite",
    "InviteGuild",
    "Webhook",
    "PermissionOverwrite",
    "resolve_permissions",
    "ActionRow",
    "Button",
    "SelectMenu",
    "SelectOption",
    "TextInput",
    "_component_from_data",
    "Modal",
    "Interaction",
    "InteractionData",
    "Thread",
    "ThreadMember",
    "ThreadMetadata",
    "GuildScheduledEvent",
    "GuildScheduledEventEntityMetadata",
    "StageInstance",
    "Application",
    "ApplicationInstallParams",
    "EmbedBuilder",
    "MessageBuilder",
    "ButtonBuilder",
    "SelectMenuBuilder",
    "ModalBuilder",
    "ActionRowBuilder",
    "BaseCommand",
    "SlashCommand",
    "SlashCommandOption",
    "UserCommand",
    "MessageCommand",
    "PrefixCommand",
    "PrefixCommandHandler",
    "SlashCommandGroup",
    "SubCommand",
    "SubCommandGroup",
    "Cooldown",
    "BucketType",
    "CooldownBucket",
    "PrefixContext",
    "SlashContext",
    "ComponentContext",
    "ModalContext",
    "cooldown",
    "guild_only",
    "dm_only",
    "require_permissions",
    "require_bot_permissions",
    "check",
    "is_owner",
    "max_concurrency",
    "CacheStore",
    "CacheConfig",
    "LRUCache",
    "EventDispatcher",
    "EventListener",
    "MiddlewareChain",
    "LoggingMiddleware",
    "FilterMiddleware",
    "GatewayConnection",
    "HeartbeatManager",
    "ShardManager",
    "VoiceClient",
    "HTTPClient",
    "RateLimitManager",
    "RateLimitBucket",
    "GlobalRateLimiter",
    "Route",
    "Endpoints",
]
