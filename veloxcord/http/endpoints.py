from __future__ import annotations


API_BASE = "https://discord.com/api/v10"


class Route:
    __slots__ = ("method", "path", "channel_id", "guild_id", "webhook_id")

    def __init__(
        self,
        method: str,
        path: str,
        *,
        channel_id: int = 0,
        guild_id: int = 0,
        webhook_id: int = 0,
    ) -> None:
        self.method = method
        self.path = path
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.webhook_id = webhook_id

    def __repr__(self) -> str:
        return f"<Route {self.method} {self.path}>"

    @property
    def url(self) -> str:
        return f"{API_BASE}{self.path}"

    @property
    def bucket_key(self) -> str:
        parts = [self.method, self.path]
        if self.channel_id:
            parts.append(f"channel:{self.channel_id}")
        if self.guild_id:
            parts.append(f"guild:{self.guild_id}")
        if self.webhook_id:
            parts.append(f"webhook:{self.webhook_id}")
        return ":".join(parts)


class Endpoints:
    @staticmethod
    def get_gateway() -> Route:
        return Route("GET", "/gateway")

    @staticmethod
    def get_gateway_bot() -> Route:
        return Route("GET", "/gateway/bot")

    @staticmethod
    def get_current_user() -> Route:
        return Route("GET", "/users/@me")

    @staticmethod
    def get_user(user_id: int) -> Route:
        return Route("GET", f"/users/{user_id}")

    @staticmethod
    def edit_current_user() -> Route:
        return Route("PATCH", "/users/@me")

    @staticmethod
    def get_current_user_guilds() -> Route:
        return Route("GET", "/users/@me/guilds")

    @staticmethod
    def leave_guild(guild_id: int) -> Route:
        return Route("DELETE", f"/users/@me/guilds/{guild_id}", guild_id=guild_id)

    @staticmethod
    def create_dm() -> Route:
        return Route("POST", "/users/@me/channels")

    @staticmethod
    def get_guild(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}", guild_id=guild_id)

    @staticmethod
    def create_guild() -> Route:
        return Route("POST", "/guilds")

    @staticmethod
    def edit_guild(guild_id: int) -> Route:
        return Route("PATCH", f"/guilds/{guild_id}", guild_id=guild_id)

    @staticmethod
    def delete_guild(guild_id: int) -> Route:
        return Route("DELETE", f"/guilds/{guild_id}", guild_id=guild_id)

    @staticmethod
    def get_guild_channels(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/channels", guild_id=guild_id)

    @staticmethod
    def create_guild_channel(guild_id: int) -> Route:
        return Route("POST", f"/guilds/{guild_id}/channels", guild_id=guild_id)

    @staticmethod
    def get_guild_member(guild_id: int, user_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/members/{user_id}", guild_id=guild_id)

    @staticmethod
    def list_guild_members(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/members", guild_id=guild_id)

    @staticmethod
    def search_guild_members(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/members/search", guild_id=guild_id)

    @staticmethod
    def edit_guild_member(guild_id: int, user_id: int) -> Route:
        return Route("PATCH", f"/guilds/{guild_id}/members/{user_id}", guild_id=guild_id)

    @staticmethod
    def remove_guild_member(guild_id: int, user_id: int) -> Route:
        return Route("DELETE", f"/guilds/{guild_id}/members/{user_id}", guild_id=guild_id)

    @staticmethod
    def add_guild_member_role(guild_id: int, user_id: int, role_id: int) -> Route:
        return Route("PUT", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", guild_id=guild_id)

    @staticmethod
    def remove_guild_member_role(guild_id: int, user_id: int, role_id: int) -> Route:
        return Route("DELETE", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", guild_id=guild_id)

    @staticmethod
    def get_guild_bans(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/bans", guild_id=guild_id)

    @staticmethod
    def get_guild_ban(guild_id: int, user_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id)

    @staticmethod
    def create_guild_ban(guild_id: int, user_id: int) -> Route:
        return Route("PUT", f"/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id)

    @staticmethod
    def remove_guild_ban(guild_id: int, user_id: int) -> Route:
        return Route("DELETE", f"/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id)

    @staticmethod
    def get_guild_roles(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/roles", guild_id=guild_id)

    @staticmethod
    def create_guild_role(guild_id: int) -> Route:
        return Route("POST", f"/guilds/{guild_id}/roles", guild_id=guild_id)

    @staticmethod
    def edit_guild_role(guild_id: int, role_id: int) -> Route:
        return Route("PATCH", f"/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id)

    @staticmethod
    def delete_guild_role(guild_id: int, role_id: int) -> Route:
        return Route("DELETE", f"/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id)

    @staticmethod
    def get_guild_emojis(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/emojis", guild_id=guild_id)

    @staticmethod
    def get_guild_emoji(guild_id: int, emoji_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id)

    @staticmethod
    def create_guild_emoji(guild_id: int) -> Route:
        return Route("POST", f"/guilds/{guild_id}/emojis", guild_id=guild_id)

    @staticmethod
    def edit_guild_emoji(guild_id: int, emoji_id: int) -> Route:
        return Route("PATCH", f"/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id)

    @staticmethod
    def delete_guild_emoji(guild_id: int, emoji_id: int) -> Route:
        return Route("DELETE", f"/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id)

    @staticmethod
    def get_channel(channel_id: int) -> Route:
        return Route("GET", f"/channels/{channel_id}", channel_id=channel_id)

    @staticmethod
    def edit_channel(channel_id: int) -> Route:
        return Route("PATCH", f"/channels/{channel_id}", channel_id=channel_id)

    @staticmethod
    def delete_channel(channel_id: int) -> Route:
        return Route("DELETE", f"/channels/{channel_id}", channel_id=channel_id)

    @staticmethod
    def get_channel_messages(channel_id: int) -> Route:
        return Route("GET", f"/channels/{channel_id}/messages", channel_id=channel_id)

    @staticmethod
    def get_channel_message(channel_id: int, message_id: int) -> Route:
        return Route("GET", f"/channels/{channel_id}/messages/{message_id}", channel_id=channel_id)

    @staticmethod
    def create_message(channel_id: int) -> Route:
        return Route("POST", f"/channels/{channel_id}/messages", channel_id=channel_id)

    @staticmethod
    def edit_message(channel_id: int, message_id: int) -> Route:
        return Route("PATCH", f"/channels/{channel_id}/messages/{message_id}", channel_id=channel_id)

    @staticmethod
    def delete_message(channel_id: int, message_id: int) -> Route:
        return Route("DELETE", f"/channels/{channel_id}/messages/{message_id}", channel_id=channel_id)

    @staticmethod
    def bulk_delete_messages(channel_id: int) -> Route:
        return Route("POST", f"/channels/{channel_id}/messages/bulk-delete", channel_id=channel_id)

    @staticmethod
    def crosspost_message(channel_id: int, message_id: int) -> Route:
        return Route("POST", f"/channels/{channel_id}/messages/{message_id}/crosspost", channel_id=channel_id)

    @staticmethod
    def create_reaction(channel_id: int, message_id: int, emoji: str) -> Route:
        import urllib.parse
        encoded = urllib.parse.quote(emoji)
        return Route("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded}/@me", channel_id=channel_id)

    @staticmethod
    def delete_own_reaction(channel_id: int, message_id: int, emoji: str) -> Route:
        import urllib.parse
        encoded = urllib.parse.quote(emoji)
        return Route("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded}/@me", channel_id=channel_id)

    @staticmethod
    def delete_user_reaction(channel_id: int, message_id: int, emoji: str, user_id: int) -> Route:
        import urllib.parse
        encoded = urllib.parse.quote(emoji)
        return Route("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded}/{user_id}", channel_id=channel_id)

    @staticmethod
    def delete_all_reactions(channel_id: int, message_id: int) -> Route:
        return Route("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions", channel_id=channel_id)

    @staticmethod
    def get_pinned_messages(channel_id: int) -> Route:
        return Route("GET", f"/channels/{channel_id}/pins", channel_id=channel_id)

    @staticmethod
    def pin_message(channel_id: int, message_id: int) -> Route:
        return Route("PUT", f"/channels/{channel_id}/pins/{message_id}", channel_id=channel_id)

    @staticmethod
    def unpin_message(channel_id: int, message_id: int) -> Route:
        return Route("DELETE", f"/channels/{channel_id}/pins/{message_id}", channel_id=channel_id)

    @staticmethod
    def trigger_typing_indicator(channel_id: int) -> Route:
        return Route("POST", f"/channels/{channel_id}/typing", channel_id=channel_id)

    @staticmethod
    def create_channel_invite(channel_id: int) -> Route:
        return Route("POST", f"/channels/{channel_id}/invites", channel_id=channel_id)

    @staticmethod
    def get_invite(code: str) -> Route:
        return Route("GET", f"/invites/{code}")

    @staticmethod
    def delete_invite(code: str) -> Route:
        return Route("DELETE", f"/invites/{code}")

    @staticmethod
    def get_webhook(webhook_id: int) -> Route:
        return Route("GET", f"/webhooks/{webhook_id}", webhook_id=webhook_id)

    @staticmethod
    def get_webhook_with_token(webhook_id: int, token: str) -> Route:
        return Route("GET", f"/webhooks/{webhook_id}/{token}", webhook_id=webhook_id)

    @staticmethod
    def edit_webhook(webhook_id: int) -> Route:
        return Route("PATCH", f"/webhooks/{webhook_id}", webhook_id=webhook_id)

    @staticmethod
    def edit_webhook_with_token(webhook_id: int, token: str) -> Route:
        return Route("PATCH", f"/webhooks/{webhook_id}/{token}", webhook_id=webhook_id)

    @staticmethod
    def delete_webhook(webhook_id: int) -> Route:
        return Route("DELETE", f"/webhooks/{webhook_id}", webhook_id=webhook_id)

    @staticmethod
    def delete_webhook_with_token(webhook_id: int, token: str) -> Route:
        return Route("DELETE", f"/webhooks/{webhook_id}/{token}", webhook_id=webhook_id)

    @staticmethod
    def execute_webhook(webhook_id: int, token: str) -> Route:
        return Route("POST", f"/webhooks/{webhook_id}/{token}", webhook_id=webhook_id)

    @staticmethod
    def create_interaction_response(interaction_id: int, token: str) -> Route:
        return Route("POST", f"/interactions/{interaction_id}/{token}/callback")

    @staticmethod
    def get_original_interaction_response(application_id: int, token: str) -> Route:
        return Route("GET", f"/webhooks/{application_id}/{token}/messages/@original")

    @staticmethod
    def edit_original_interaction_response(application_id: int, token: str) -> Route:
        return Route("PATCH", f"/webhooks/{application_id}/{token}/messages/@original")

    @staticmethod
    def delete_original_interaction_response(application_id: int, token: str) -> Route:
        return Route("DELETE", f"/webhooks/{application_id}/{token}/messages/@original")

    @staticmethod
    def create_followup_message(application_id: int, token: str) -> Route:
        return Route("POST", f"/webhooks/{application_id}/{token}")

    @staticmethod
    def get_global_application_commands(application_id: int) -> Route:
        return Route("GET", f"/applications/{application_id}/commands")

    @staticmethod
    def create_global_application_command(application_id: int) -> Route:
        return Route("POST", f"/applications/{application_id}/commands")

    @staticmethod
    def edit_global_application_command(application_id: int, command_id: int) -> Route:
        return Route("PATCH", f"/applications/{application_id}/commands/{command_id}")

    @staticmethod
    def delete_global_application_command(application_id: int, command_id: int) -> Route:
        return Route("DELETE", f"/applications/{application_id}/commands/{command_id}")

    @staticmethod
    def bulk_overwrite_global_application_commands(application_id: int) -> Route:
        return Route("PUT", f"/applications/{application_id}/commands")

    @staticmethod
    def get_guild_application_commands(application_id: int, guild_id: int) -> Route:
        return Route("GET", f"/applications/{application_id}/guilds/{guild_id}/commands", guild_id=guild_id)

    @staticmethod
    def create_guild_application_command(application_id: int, guild_id: int) -> Route:
        return Route("POST", f"/applications/{application_id}/guilds/{guild_id}/commands", guild_id=guild_id)

    @staticmethod
    def bulk_overwrite_guild_application_commands(application_id: int, guild_id: int) -> Route:
        return Route("PUT", f"/applications/{application_id}/guilds/{guild_id}/commands", guild_id=guild_id)

    @staticmethod
    def get_current_application() -> Route:
        return Route("GET", "/applications/@me")

    @staticmethod
    def get_guild_scheduled_events(guild_id: int) -> Route:
        return Route("GET", f"/guilds/{guild_id}/scheduled-events", guild_id=guild_id)

    @staticmethod
    def create_guild_scheduled_event(guild_id: int) -> Route:
        return Route("POST", f"/guilds/{guild_id}/scheduled-events", guild_id=guild_id)

    @staticmethod
    def edit_guild_scheduled_event(guild_id: int, event_id: int) -> Route:
        return Route("PATCH", f"/guilds/{guild_id}/scheduled-events/{event_id}", guild_id=guild_id)

    @staticmethod
    def delete_guild_scheduled_event(guild_id: int, event_id: int) -> Route:
        return Route("DELETE", f"/guilds/{guild_id}/scheduled-events/{event_id}", guild_id=guild_id)

    @staticmethod
    def create_stage_instance() -> Route:
        return Route("POST", "/stage-instances")

    @staticmethod
    def get_stage_instance(channel_id: int) -> Route:
        return Route("GET", f"/stage-instances/{channel_id}", channel_id=channel_id)

    @staticmethod
    def edit_stage_instance(channel_id: int) -> Route:
        return Route("PATCH", f"/stage-instances/{channel_id}", channel_id=channel_id)

    @staticmethod
    def delete_stage_instance(channel_id: int) -> Route:
        return Route("DELETE", f"/stage-instances/{channel_id}", channel_id=channel_id)

    @staticmethod
    def join_thread(channel_id: int) -> Route:
        return Route("PUT", f"/channels/{channel_id}/thread-members/@me", channel_id=channel_id)

    @staticmethod
    def leave_thread(channel_id: int) -> Route:
        return Route("DELETE", f"/channels/{channel_id}/thread-members/@me", channel_id=channel_id)

    @staticmethod
    def add_thread_member(channel_id: int, user_id: int) -> Route:
        return Route("PUT", f"/channels/{channel_id}/thread-members/{user_id}", channel_id=channel_id)

    @staticmethod
    def remove_thread_member(channel_id: int, user_id: int) -> Route:
        return Route("DELETE", f"/channels/{channel_id}/thread-members/{user_id}", channel_id=channel_id)

    @staticmethod
    def list_thread_members(channel_id: int) -> Route:
        return Route("GET", f"/channels/{channel_id}/thread-members", channel_id=channel_id)

    @staticmethod
    def start_thread_from_message(channel_id: int, message_id: int) -> Route:
        return Route("POST", f"/channels/{channel_id}/messages/{message_id}/threads", channel_id=channel_id)

    @staticmethod
    def start_thread_without_message(channel_id: int) -> Route:
        return Route("POST", f"/channels/{channel_id}/threads", channel_id=channel_id)
