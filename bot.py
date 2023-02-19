"""
MIT License

Copyright (c) 2023 Sodynoizz_TH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import aiohttp
import asyncpg
import discord
from discord.ext import commands
from pretty_help import AppMenu, PrettyHelp

from typing import Union

from config import secret
from utils.context import Context


async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(secret.default_prefix)(bot, message)

    prefix = await bot.db.fetch(
        'SELECT prefix FROM guilds WHERE "guild_id" = $1', message.guild.id
    )

    if len(prefix) == 0:
        await bot.db.execute(
            'INSERT INTO guilds ("guild_id", prefix) VALUES ($1, $2)',
            message.guild.id,
            secret.default_prefix,
        )
    else:
        prefix = prefix[0].get("prefix")

    return commands.when_mentioned_or(prefix)(bot, message)


class DiseasesBot(commands.AutoShardedBot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo

    def __init__(self, *args, **kwargs):
        command_prefix = get_prefix
        allowed_mentions = discord.AllowedMentions(
            roles=False, everyone=False, users=True
        )
        intents = discord.Intents.all()
        help_command = PrettyHelp(menu=AppMenu(timeout=30))

        super().__init__(
            command_prefix=command_prefix,
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=True,
            help_command=help_command,
            *args,
            **kwargs,
        )

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        self.bot_app_info = await self.application_info()

        for extension in secret.initial_extensions:
            await self.load_extension(extension)

        await self.create_db_pool()
        await self.tree.sync()

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    @property
    def partner_id(self) -> int:
        return secret.contributor_id

    @property
    def server_invite(self) -> str:
        return "https://discord.gg/v5jBXfnX"

    @property
    def bot_invite(self) -> str:
        return "https://discord.com/api/oauth2/authorize?client_id=1040974651247034418&permissions=8&scope=applications.commands%20bot"

    async def get_context(
        self, origin: Union[discord.Interaction, discord.Message], /, *, cls=Context
    ) -> Context:
        return await super().get_context(origin, cls=cls)

    async def create_db_pool(self) -> None:
        self.db = await asyncpg.create_pool(
            database=secret.database_name,
            user=secret.database_user,
            password=secret.database_password,
        )

    async def on_ready(self) -> None:
        print(f"{self.user} is ready")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return 
        await self.process_commands(message)
    
    async def close(self) -> None:
        await super().close()

    async def start(self) -> None:
        await super().start(secret.token, reconnect=True)
