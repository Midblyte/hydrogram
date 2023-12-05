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

from collections.abc import AsyncGenerator
from typing import Optional, Union

import hydrogram
from hydrogram import raw, types, utils


class GetChatPhotos:
    async def get_chat_photos(
        self: "hydrogram.Client",
        chat_id: Union[int, str],
        limit: int = 0,
    ) -> Optional[AsyncGenerator["types.Photo", None]]:
        """Get a chat or a user profile photos sequentially.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            limit (``int``, *optional*):
                Limits the number of profile photos to be retrieved.
                By default, no limit is applied and all profile photos are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~hydrogram.types.Photo` objects.

        Example:
            .. code-block:: python

                async for photo in app.get_chat_photos("me"):
                    print(photo)
        """
        peer_id = await self.resolve_peer(chat_id)

        if isinstance(peer_id, raw.types.InputPeerChannel):
            r = await self.invoke(raw.functions.channels.GetFullChannel(channel=peer_id))

            current = types.Photo._parse(self, r.full_chat.chat_photo) or []

            r = await utils.parse_messages(
                self,
                await self.invoke(
                    raw.functions.messages.Search(
                        peer=peer_id,
                        q="",
                        filter=raw.types.InputMessagesFilterChatPhotos(),
                        min_date=0,
                        max_date=0,
                        offset_id=0,
                        add_offset=0,
                        limit=limit,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                ),
            )

            if extra := [message.new_chat_photo for message in r]:
                if current:
                    photos = ([current, *extra]) if current.file_id != extra[0].file_id else extra
                else:
                    photos = extra
            else:
                photos = [current] if current else []

            for current, photo in enumerate(photos, start=1):
                yield photo

                if current >= limit:
                    return
        else:
            current = 0
            total = limit or (1 << 31)
            limit = min(100, total)
            offset = 0

            while True:
                r = await self.invoke(
                    raw.functions.photos.GetUserPhotos(
                        user_id=peer_id, offset=offset, max_id=0, limit=limit
                    )
                )

                photos = [types.Photo._parse(self, photo) for photo in r.photos]

                if not photos:
                    return

                offset += len(photos)

                for photo in photos:
                    yield photo

                    current += 1

                    if current >= total:
                        return
