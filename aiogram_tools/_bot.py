from __future__ import annotations

import asyncio
import os
from typing import Optional, Union

from aiogram import Bot as _Bot
from aiogram.bot.base import TelegramAPIServer, aiohttp, TELEGRAM_PRODUCTION
from aiogram.types import base
from pyrogram import Client, raw


class Userbot:

    def __init__(self, api_id: int, api_hash: str, session_name='aiogram_data/bound_userbot'):
        for folder in ['aiogram_data']:
            if not os.path.exists(folder):
                os.mkdir(folder)

        self._client = Client(session_name, api_id, api_hash)

    @property
    async def client(self) -> Client:
        if not self._client.is_connected:
            await self._client.start()
        return self._client

    async def stop_client(self):
        if self._client.is_connected:
            await self._client.stop()

    async def create_group(
            self,
            title: str,
            bound_bot: Union[int, str],
            other_users: Union[Union[int, str], list[Union[int, str]]]
    ):
        client = await self.client

        if not isinstance(other_users, list):
            other_users = [other_users]

        other_users.append(bound_bot)
        new_group = await client.create_group(title, other_users)

        peer = await client.resolve_peer(new_group.id)

        await client.send(
            raw.functions.messages.EditChatAdmin(
                chat_id=peer.chat_id,
                user_id=await client.resolve_peer(bound_bot),
                is_admin=True
            )
        )


class Bot(_Bot):

    def __init__(
            self,
            token: base.String,
            loop: Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop, None] = None,
            connections_limit: Optional[base.Integer] = None,
            proxy: Optional[base.String] = None,
            proxy_auth: Optional[aiohttp.BasicAuth] = None,
            validate_token: Optional[base.Boolean] = True,
            parse_mode: Optional[base.String] = None,
            timeout: Union[base.Integer, base.Float, aiohttp.ClientTimeout, None] = None,
            server: TelegramAPIServer = TELEGRAM_PRODUCTION,
            bound_userbot_api_id: Optional[int] = None,
            bound_userbot_api_hash: Optional[str] = None,
    ):
        super().__init__(
            token=token,
            loop=loop,
            connections_limit=connections_limit,
            proxy=proxy,
            proxy_auth=proxy_auth,
            validate_token=validate_token,
            parse_mode=parse_mode,
            timeout=timeout,
            server=server,
        )

        self.bound_userbot = Userbot(bound_userbot_api_id, bound_userbot_api_hash)

    async def create_group(self, title: str, users: Union[Union[int, str], list[Union[int, str]]] = None):
        users = users or []
        bound_bot_username = (await self.me).username
        await self.bound_userbot.create_group(title, bound_bot_username, users)
