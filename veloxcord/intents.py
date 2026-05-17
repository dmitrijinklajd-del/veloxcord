from __future__ import annotations
from .flags import BaseFlags


class Intents(BaseFlags):
    __slots__ = ()

    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21

    @classmethod
    def default(cls) -> "Intents":
        return cls(
            cls.GUILDS
            | cls.GUILD_MODERATION
            | cls.GUILD_EMOJIS_AND_STICKERS
            | cls.GUILD_INTEGRATIONS
            | cls.GUILD_WEBHOOKS
            | cls.GUILD_INVITES
            | cls.GUILD_VOICE_STATES
            | cls.GUILD_MESSAGES
            | cls.GUILD_MESSAGE_REACTIONS
            | cls.GUILD_MESSAGE_TYPING
            | cls.DIRECT_MESSAGES
            | cls.DIRECT_MESSAGE_REACTIONS
            | cls.DIRECT_MESSAGE_TYPING
            | cls.GUILD_SCHEDULED_EVENTS
        )

    @classmethod
    def all(cls) -> "Intents":
        value = 0
        for attr in dir(cls):
            v = getattr(cls, attr)
            if isinstance(v, int) and v > 0:
                value |= v
        return cls(value)

    @classmethod
    def privileged(cls) -> "Intents":
        return cls(cls.GUILD_MEMBERS | cls.GUILD_PRESENCES | cls.MESSAGE_CONTENT)

    @classmethod
    def none(cls) -> "Intents":
        return cls(0)

    @property
    def guilds(self) -> bool:
        return bool(self.value & self.GUILDS)

    @property
    def guild_members(self) -> bool:
        return bool(self.value & self.GUILD_MEMBERS)

    @property
    def guild_moderation(self) -> bool:
        return bool(self.value & self.GUILD_MODERATION)

    @property
    def guild_emojis_and_stickers(self) -> bool:
        return bool(self.value & self.GUILD_EMOJIS_AND_STICKERS)

    @property
    def guild_integrations(self) -> bool:
        return bool(self.value & self.GUILD_INTEGRATIONS)

    @property
    def guild_webhooks(self) -> bool:
        return bool(self.value & self.GUILD_WEBHOOKS)

    @property
    def guild_invites(self) -> bool:
        return bool(self.value & self.GUILD_INVITES)

    @property
    def guild_voice_states(self) -> bool:
        return bool(self.value & self.GUILD_VOICE_STATES)

    @property
    def guild_presences(self) -> bool:
        return bool(self.value & self.GUILD_PRESENCES)

    @property
    def guild_messages(self) -> bool:
        return bool(self.value & self.GUILD_MESSAGES)

    @property
    def guild_message_reactions(self) -> bool:
        return bool(self.value & self.GUILD_MESSAGE_REACTIONS)

    @property
    def guild_message_typing(self) -> bool:
        return bool(self.value & self.GUILD_MESSAGE_TYPING)

    @property
    def direct_messages(self) -> bool:
        return bool(self.value & self.DIRECT_MESSAGES)

    @property
    def direct_message_reactions(self) -> bool:
        return bool(self.value & self.DIRECT_MESSAGE_REACTIONS)

    @property
    def direct_message_typing(self) -> bool:
        return bool(self.value & self.DIRECT_MESSAGE_TYPING)

    @property
    def message_content(self) -> bool:
        return bool(self.value & self.MESSAGE_CONTENT)

    @property
    def guild_scheduled_events(self) -> bool:
        return bool(self.value & self.GUILD_SCHEDULED_EVENTS)

    @property
    def auto_moderation_configuration(self) -> bool:
        return bool(self.value & self.AUTO_MODERATION_CONFIGURATION)

    @property
    def auto_moderation_execution(self) -> bool:
        return bool(self.value & self.AUTO_MODERATION_EXECUTION)
