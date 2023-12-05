#  Hydrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2023 Dan <https://github.com/delivrance>
#  Copyright (C) 2023-present Amano LLC <https://amanoteam.com>
#
#  This file is part of Hydrogram.
#
#  Hydrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Hydrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Hydrogram.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from typing import Optional, Union

import hydrogram
from hydrogram import enums, raw, types, utils
from hydrogram.types.object import Object


class ChatMember(Object):
    """Contains information about one member of a chat.

    Parameters:
        status (:obj:`~hydrogram.enums.ChatMemberStatus`):
            The member's status in the chat.

        user (:obj:`~hydrogram.types.User`, *optional*):
            Information about the user.

        chat (:obj:`~hydrogram.types.Chat`, *optional*):
            Information about the chat (useful in case of banned channel senders).

        joined_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the user joined.
            Not available for the owner.

        custom_title (``str``, *optional*):
            A custom title that will be shown to all members instead of "Owner" or "Admin".
            Creator (owner) and administrators only. Can be None in case there's no custom title set.

        until_date (:py:obj:`~datetime.datetime`, *optional*):
            Restricted and banned only.
            Date when restrictions will be lifted for this user.

        invited_by (:obj:`~hydrogram.types.User`, *optional*):
            Administrators and self member only. Information about the user who invited this member.
            In case the user joined by himself this will be the same as "user".

        promoted_by (:obj:`~hydrogram.types.User`, *optional*):
            Administrators only. Information about the user who promoted this member as administrator.

        restricted_by (:obj:`~hydrogram.types.User`, *optional*):
            Restricted and banned only. Information about the user who restricted or banned this member.

        is_member (``bool``, *optional*):
            Restricted only. True, if the user is a member of the chat at the moment of the request.

        can_be_edited (``bool``, *optional*):
            True, if the you are allowed to edit administrator privileges of the user.

        permissions (:obj:`~hydrogram.types.ChatPermissions`, *optional*):
            Restricted only. Restricted actions that a non-administrator user is allowed to take.

        privileges (:obj:`~hydrogram.types.ChatPrivileges`, *optional*):
            Administrators only. Privileged actions that an administrator is able to take.
    """

    def __init__(
        self,
        *,
        client: "hydrogram.Client" = None,
        status: "enums.ChatMemberStatus",
        user: "types.User" = None,
        chat: "types.Chat" = None,
        custom_title: Optional[str] = None,
        until_date: Optional[datetime] = None,
        joined_date: Optional[datetime] = None,
        invited_by: "types.User" = None,
        promoted_by: "types.User" = None,
        restricted_by: "types.User" = None,
        is_member: Optional[bool] = None,
        can_be_edited: Optional[bool] = None,
        permissions: "types.ChatPermissions" = None,
        privileges: "types.ChatPrivileges" = None,
    ):
        super().__init__(client)

        self.status = status
        self.user = user
        self.chat = chat
        self.custom_title = custom_title
        self.until_date = until_date
        self.joined_date = joined_date
        self.invited_by = invited_by
        self.promoted_by = promoted_by
        self.restricted_by = restricted_by
        self.is_member = is_member
        self.can_be_edited = can_be_edited
        self.permissions = permissions
        self.privileges = privileges

    @staticmethod
    def _parse(
        client: "hydrogram.Client",
        member: Union["raw.base.ChatParticipant", "raw.base.ChannelParticipant"],
        users: dict[int, "raw.base.User"],
        chats: dict[int, "raw.base.Chat"],
    ) -> "ChatMember":
        # Chat participants
        if isinstance(member, raw.types.ChatParticipant):
            return ChatMember(
                status=enums.ChatMemberStatus.MEMBER,
                user=types.User._parse(client, users[member.user_id]),
                joined_date=utils.timestamp_to_datetime(member.date),
                invited_by=types.User._parse(client, users[member.inviter_id]),
                client=client,
            )
        if isinstance(member, raw.types.ChatParticipantAdmin):
            return ChatMember(
                status=enums.ChatMemberStatus.ADMINISTRATOR,
                user=types.User._parse(client, users[member.user_id]),
                joined_date=utils.timestamp_to_datetime(member.date),
                invited_by=types.User._parse(client, users[member.inviter_id]),
                client=client,
            )
        if isinstance(member, raw.types.ChatParticipantCreator):
            return ChatMember(
                status=enums.ChatMemberStatus.OWNER,
                user=types.User._parse(client, users[member.user_id]),
                client=client,
            )

        # Channel participants
        if isinstance(member, raw.types.ChannelParticipant):
            return ChatMember(
                status=enums.ChatMemberStatus.MEMBER,
                user=types.User._parse(client, users[member.user_id]),
                joined_date=utils.timestamp_to_datetime(member.date),
                client=client,
            )
        if isinstance(member, raw.types.ChannelParticipantAdmin):
            return ChatMember(
                status=enums.ChatMemberStatus.ADMINISTRATOR,
                user=types.User._parse(client, users[member.user_id]),
                joined_date=utils.timestamp_to_datetime(member.date),
                promoted_by=types.User._parse(client, users[member.promoted_by]),
                invited_by=(
                    types.User._parse(client, users[member.inviter_id])
                    if member.inviter_id
                    else None
                ),
                custom_title=member.rank,
                can_be_edited=member.can_edit,
                privileges=types.ChatPrivileges._parse(member.admin_rights),
                client=client,
            )
        if isinstance(member, raw.types.ChannelParticipantBanned):
            peer = member.peer
            peer_id = utils.get_raw_peer_id(peer)

            user = (
                types.User._parse(client, users[peer_id])
                if isinstance(peer, raw.types.PeerUser)
                else None
            )

            chat = (
                None
                if isinstance(peer, raw.types.PeerUser)
                else types.Chat._parse_chat(client, chats[peer_id])
            )

            return ChatMember(
                status=(
                    enums.ChatMemberStatus.BANNED
                    if member.banned_rights.view_messages
                    else enums.ChatMemberStatus.RESTRICTED
                ),
                user=user,
                chat=chat,
                until_date=utils.timestamp_to_datetime(member.banned_rights.until_date),
                joined_date=utils.timestamp_to_datetime(member.date),
                is_member=not member.left,
                restricted_by=types.User._parse(client, users[member.kicked_by]),
                permissions=types.ChatPermissions._parse(member.banned_rights),
                client=client,
            )
        if isinstance(member, raw.types.ChannelParticipantCreator):
            return ChatMember(
                status=enums.ChatMemberStatus.OWNER,
                user=types.User._parse(client, users[member.user_id]),
                custom_title=member.rank,
                privileges=types.ChatPrivileges._parse(member.admin_rights),
                client=client,
            )
        if isinstance(member, raw.types.ChannelParticipantLeft):
            peer = member.peer
            peer_id = utils.get_raw_peer_id(peer)

            user = (
                types.User._parse(client, users[peer_id])
                if isinstance(peer, raw.types.PeerUser)
                else None
            )

            chat = (
                None
                if isinstance(peer, raw.types.PeerUser)
                else types.Chat._parse_chat(client, chats[peer_id])
            )

            return ChatMember(
                status=enums.ChatMemberStatus.LEFT, user=user, chat=chat, client=client
            )
        if isinstance(member, raw.types.ChannelParticipantSelf):
            return ChatMember(
                status=enums.ChatMemberStatus.MEMBER,
                user=types.User._parse(client, users[member.user_id]),
                joined_date=utils.timestamp_to_datetime(member.date),
                invited_by=types.User._parse(client, users[member.inviter_id]),
                client=client,
            )
        return None
