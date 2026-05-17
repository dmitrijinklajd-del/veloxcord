from __future__ import annotations
from typing import Iterator


class BaseFlags:
    __slots__ = ("value",)

    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)

    def __or__(self, other: "BaseFlags") -> "BaseFlags":
        result = self.__class__(self.value | other.value)
        return result

    def __and__(self, other: "BaseFlags") -> "BaseFlags":
        result = self.__class__(self.value & other.value)
        return result

    def __xor__(self, other: "BaseFlags") -> "BaseFlags":
        result = self.__class__(self.value ^ other.value)
        return result

    def __invert__(self) -> "BaseFlags":
        return self.__class__(~self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def has(self, flag: "BaseFlags") -> bool:
        return (self.value & flag.value) == flag.value

    def add(self, flag: "BaseFlags") -> None:
        self.value |= flag.value

    def remove(self, flag: "BaseFlags") -> None:
        self.value &= ~flag.value


class Permissions(BaseFlags):
    __slots__ = ()

    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    USE_VAD = 1 << 25
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_GUILD_EXPRESSIONS = 1 << 30
    USE_APPLICATION_COMMANDS = 1 << 31
    REQUEST_TO_SPEAK = 1 << 32
    MANAGE_EVENTS = 1 << 33
    MANAGE_THREADS = 1 << 34
    CREATE_PUBLIC_THREADS = 1 << 35
    CREATE_PRIVATE_THREADS = 1 << 36
    USE_EXTERNAL_STICKERS = 1 << 37
    SEND_MESSAGES_IN_THREADS = 1 << 38
    USE_EMBEDDED_ACTIVITIES = 1 << 39
    MODERATE_MEMBERS = 1 << 40
    VIEW_CREATOR_MONETIZATION_ANALYTICS = 1 << 41
    USE_SOUNDBOARD = 1 << 42
    CREATE_GUILD_EXPRESSIONS = 1 << 43
    CREATE_EVENTS = 1 << 44
    USE_EXTERNAL_SOUNDS = 1 << 45
    SEND_VOICE_MESSAGES = 1 << 46

    def __init__(self, value: int = 0) -> None:
        super().__init__(value)

    @classmethod
    def none(cls) -> "Permissions":
        return cls(0)

    @classmethod
    def all(cls) -> "Permissions":
        value = 0
        for attr in dir(cls):
            v = getattr(cls, attr)
            if isinstance(v, int) and v > 0:
                value |= v
        return cls(value)

    @classmethod
    def all_channel(cls) -> "Permissions":
        return cls(
            cls.CREATE_INSTANT_INVITE
            | cls.MANAGE_CHANNELS
            | cls.ADD_REACTIONS
            | cls.VIEW_CHANNEL
            | cls.SEND_MESSAGES
            | cls.SEND_TTS_MESSAGES
            | cls.MANAGE_MESSAGES
            | cls.EMBED_LINKS
            | cls.ATTACH_FILES
            | cls.READ_MESSAGE_HISTORY
            | cls.MENTION_EVERYONE
            | cls.USE_EXTERNAL_EMOJIS
            | cls.MANAGE_ROLES
            | cls.MANAGE_WEBHOOKS
            | cls.USE_APPLICATION_COMMANDS
            | cls.MANAGE_THREADS
            | cls.CREATE_PUBLIC_THREADS
            | cls.CREATE_PRIVATE_THREADS
            | cls.USE_EXTERNAL_STICKERS
            | cls.SEND_MESSAGES_IN_THREADS
        )

    @classmethod
    def text(cls) -> "Permissions":
        return cls(
            cls.ADD_REACTIONS
            | cls.VIEW_CHANNEL
            | cls.SEND_MESSAGES
            | cls.SEND_TTS_MESSAGES
            | cls.MANAGE_MESSAGES
            | cls.EMBED_LINKS
            | cls.ATTACH_FILES
            | cls.READ_MESSAGE_HISTORY
            | cls.MENTION_EVERYONE
            | cls.USE_EXTERNAL_EMOJIS
            | cls.USE_APPLICATION_COMMANDS
            | cls.MANAGE_THREADS
            | cls.CREATE_PUBLIC_THREADS
            | cls.CREATE_PRIVATE_THREADS
            | cls.USE_EXTERNAL_STICKERS
            | cls.SEND_MESSAGES_IN_THREADS
        )

    @classmethod
    def voice(cls) -> "Permissions":
        return cls(
            cls.CONNECT
            | cls.SPEAK
            | cls.MUTE_MEMBERS
            | cls.DEAFEN_MEMBERS
            | cls.MOVE_MEMBERS
            | cls.USE_VAD
            | cls.PRIORITY_SPEAKER
            | cls.STREAM
            | cls.USE_SOUNDBOARD
            | cls.USE_EMBEDDED_ACTIVITIES
            | cls.SEND_VOICE_MESSAGES
        )

    @property
    def create_instant_invite(self) -> bool:
        return bool(self.value & self.CREATE_INSTANT_INVITE)

    @property
    def kick_members(self) -> bool:
        return bool(self.value & self.KICK_MEMBERS)

    @property
    def ban_members(self) -> bool:
        return bool(self.value & self.BAN_MEMBERS)

    @property
    def administrator(self) -> bool:
        return bool(self.value & self.ADMINISTRATOR)

    @property
    def manage_channels(self) -> bool:
        return bool(self.value & self.MANAGE_CHANNELS)

    @property
    def manage_guild(self) -> bool:
        return bool(self.value & self.MANAGE_GUILD)

    @property
    def add_reactions(self) -> bool:
        return bool(self.value & self.ADD_REACTIONS)

    @property
    def view_audit_log(self) -> bool:
        return bool(self.value & self.VIEW_AUDIT_LOG)

    @property
    def priority_speaker(self) -> bool:
        return bool(self.value & self.PRIORITY_SPEAKER)

    @property
    def stream(self) -> bool:
        return bool(self.value & self.STREAM)

    @property
    def view_channel(self) -> bool:
        return bool(self.value & self.VIEW_CHANNEL)

    @property
    def send_messages(self) -> bool:
        return bool(self.value & self.SEND_MESSAGES)

    @property
    def send_tts_messages(self) -> bool:
        return bool(self.value & self.SEND_TTS_MESSAGES)

    @property
    def manage_messages(self) -> bool:
        return bool(self.value & self.MANAGE_MESSAGES)

    @property
    def embed_links(self) -> bool:
        return bool(self.value & self.EMBED_LINKS)

    @property
    def attach_files(self) -> bool:
        return bool(self.value & self.ATTACH_FILES)

    @property
    def read_message_history(self) -> bool:
        return bool(self.value & self.READ_MESSAGE_HISTORY)

    @property
    def mention_everyone(self) -> bool:
        return bool(self.value & self.MENTION_EVERYONE)

    @property
    def use_external_emojis(self) -> bool:
        return bool(self.value & self.USE_EXTERNAL_EMOJIS)

    @property
    def view_guild_insights(self) -> bool:
        return bool(self.value & self.VIEW_GUILD_INSIGHTS)

    @property
    def connect(self) -> bool:
        return bool(self.value & self.CONNECT)

    @property
    def speak(self) -> bool:
        return bool(self.value & self.SPEAK)

    @property
    def mute_members(self) -> bool:
        return bool(self.value & self.MUTE_MEMBERS)

    @property
    def deafen_members(self) -> bool:
        return bool(self.value & self.DEAFEN_MEMBERS)

    @property
    def move_members(self) -> bool:
        return bool(self.value & self.MOVE_MEMBERS)

    @property
    def use_vad(self) -> bool:
        return bool(self.value & self.USE_VAD)

    @property
    def change_nickname(self) -> bool:
        return bool(self.value & self.CHANGE_NICKNAME)

    @property
    def manage_nicknames(self) -> bool:
        return bool(self.value & self.MANAGE_NICKNAMES)

    @property
    def manage_roles(self) -> bool:
        return bool(self.value & self.MANAGE_ROLES)

    @property
    def manage_webhooks(self) -> bool:
        return bool(self.value & self.MANAGE_WEBHOOKS)

    @property
    def manage_guild_expressions(self) -> bool:
        return bool(self.value & self.MANAGE_GUILD_EXPRESSIONS)

    @property
    def use_application_commands(self) -> bool:
        return bool(self.value & self.USE_APPLICATION_COMMANDS)

    @property
    def request_to_speak(self) -> bool:
        return bool(self.value & self.REQUEST_TO_SPEAK)

    @property
    def manage_events(self) -> bool:
        return bool(self.value & self.MANAGE_EVENTS)

    @property
    def manage_threads(self) -> bool:
        return bool(self.value & self.MANAGE_THREADS)

    @property
    def create_public_threads(self) -> bool:
        return bool(self.value & self.CREATE_PUBLIC_THREADS)

    @property
    def create_private_threads(self) -> bool:
        return bool(self.value & self.CREATE_PRIVATE_THREADS)

    @property
    def use_external_stickers(self) -> bool:
        return bool(self.value & self.USE_EXTERNAL_STICKERS)

    @property
    def send_messages_in_threads(self) -> bool:
        return bool(self.value & self.SEND_MESSAGES_IN_THREADS)

    @property
    def use_embedded_activities(self) -> bool:
        return bool(self.value & self.USE_EMBEDDED_ACTIVITIES)

    @property
    def moderate_members(self) -> bool:
        return bool(self.value & self.MODERATE_MEMBERS)

    @property
    def send_voice_messages(self) -> bool:
        return bool(self.value & self.SEND_VOICE_MESSAGES)

    def _iter_enabled(self) -> Iterator[str]:
        flag_map = {
            "create_instant_invite": self.CREATE_INSTANT_INVITE,
            "kick_members": self.KICK_MEMBERS,
            "ban_members": self.BAN_MEMBERS,
            "administrator": self.ADMINISTRATOR,
            "manage_channels": self.MANAGE_CHANNELS,
            "manage_guild": self.MANAGE_GUILD,
            "add_reactions": self.ADD_REACTIONS,
            "view_audit_log": self.VIEW_AUDIT_LOG,
            "priority_speaker": self.PRIORITY_SPEAKER,
            "stream": self.STREAM,
            "view_channel": self.VIEW_CHANNEL,
            "send_messages": self.SEND_MESSAGES,
            "send_tts_messages": self.SEND_TTS_MESSAGES,
            "manage_messages": self.MANAGE_MESSAGES,
            "embed_links": self.EMBED_LINKS,
            "attach_files": self.ATTACH_FILES,
            "read_message_history": self.READ_MESSAGE_HISTORY,
            "mention_everyone": self.MENTION_EVERYONE,
            "use_external_emojis": self.USE_EXTERNAL_EMOJIS,
            "view_guild_insights": self.VIEW_GUILD_INSIGHTS,
            "connect": self.CONNECT,
            "speak": self.SPEAK,
            "mute_members": self.MUTE_MEMBERS,
            "deafen_members": self.DEAFEN_MEMBERS,
            "move_members": self.MOVE_MEMBERS,
            "use_vad": self.USE_VAD,
            "change_nickname": self.CHANGE_NICKNAME,
            "manage_nicknames": self.MANAGE_NICKNAMES,
            "manage_roles": self.MANAGE_ROLES,
            "manage_webhooks": self.MANAGE_WEBHOOKS,
            "manage_guild_expressions": self.MANAGE_GUILD_EXPRESSIONS,
            "use_application_commands": self.USE_APPLICATION_COMMANDS,
            "request_to_speak": self.REQUEST_TO_SPEAK,
            "manage_events": self.MANAGE_EVENTS,
            "manage_threads": self.MANAGE_THREADS,
            "create_public_threads": self.CREATE_PUBLIC_THREADS,
            "create_private_threads": self.CREATE_PRIVATE_THREADS,
            "use_external_stickers": self.USE_EXTERNAL_STICKERS,
            "send_messages_in_threads": self.SEND_MESSAGES_IN_THREADS,
            "use_embedded_activities": self.USE_EMBEDDED_ACTIVITIES,
            "moderate_members": self.MODERATE_MEMBERS,
            "send_voice_messages": self.SEND_VOICE_MESSAGES,
        }
        for name, bit in flag_map.items():
            if self.value & bit:
                yield name

    def __repr__(self) -> str:
        enabled = list(self._iter_enabled())
        return f"Permissions({', '.join(enabled)})"


class MessageFlags(BaseFlags):
    __slots__ = ()

    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8
    SUPPRESS_NOTIFICATIONS = 1 << 12
    IS_VOICE_MESSAGE = 1 << 13

    @property
    def crossposted(self) -> bool:
        return bool(self.value & self.CROSSPOSTED)

    @property
    def is_crosspost(self) -> bool:
        return bool(self.value & self.IS_CROSSPOST)

    @property
    def suppress_embeds(self) -> bool:
        return bool(self.value & self.SUPPRESS_EMBEDS)

    @property
    def ephemeral(self) -> bool:
        return bool(self.value & self.EPHEMERAL)

    @property
    def loading(self) -> bool:
        return bool(self.value & self.LOADING)

    @property
    def suppress_notifications(self) -> bool:
        return bool(self.value & self.SUPPRESS_NOTIFICATIONS)

    @property
    def is_voice_message(self) -> bool:
        return bool(self.value & self.IS_VOICE_MESSAGE)


class UserFlags(BaseFlags):
    __slots__ = ()

    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSEUDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19
    ACTIVE_DEVELOPER = 1 << 22

    @property
    def staff(self) -> bool:
        return bool(self.value & self.STAFF)

    @property
    def partner(self) -> bool:
        return bool(self.value & self.PARTNER)

    @property
    def bug_hunter_level_1(self) -> bool:
        return bool(self.value & self.BUG_HUNTER_LEVEL_1)

    @property
    def hypesquad_bravery(self) -> bool:
        return bool(self.value & self.HYPESQUAD_ONLINE_HOUSE_1)

    @property
    def hypesquad_brilliance(self) -> bool:
        return bool(self.value & self.HYPESQUAD_ONLINE_HOUSE_2)

    @property
    def hypesquad_balance(self) -> bool:
        return bool(self.value & self.HYPESQUAD_ONLINE_HOUSE_3)

    @property
    def early_supporter(self) -> bool:
        return bool(self.value & self.PREMIUM_EARLY_SUPPORTER)

    @property
    def verified_bot(self) -> bool:
        return bool(self.value & self.VERIFIED_BOT)

    @property
    def verified_developer(self) -> bool:
        return bool(self.value & self.VERIFIED_DEVELOPER)

    @property
    def active_developer(self) -> bool:
        return bool(self.value & self.ACTIVE_DEVELOPER)


class SystemChannelFlags(BaseFlags):
    __slots__ = ()

    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 1 << 2
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 1 << 3
    SUPPRESS_ROLE_SUBSCRIPTION_PURCHASE_NOTIFICATIONS = 1 << 4
    SUPPRESS_ROLE_SUBSCRIPTION_PURCHASE_NOTIFICATION_REPLIES = 1 << 5
