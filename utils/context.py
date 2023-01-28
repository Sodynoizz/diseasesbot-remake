from __future__ import annotations

from typing import Any, Union, TYPE_CHECKING
from discord.ext import commands
import discord
import io

if TYPE_CHECKING:
    from bot import DiseasesBot
    from aiohttp import ClientSession


class Context(commands.Context):
    bot: DiseasesBot
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self) -> str:
        return '<Context>'
    
    @property
    def session(self) -> ClientSession:
        return self.bot.session
    
    async def safe_send(self, content: str, *, escape_mentions: bool = True, **kwargs) -> discord.Message:
        if escape_mentions:
            content = discord.utils.escape_mentions(content)
        
        if len(content) > 2000:
            fp = io.BytesIO(content.encode())
            kwargs.pop('file', None)
            return await self.send(file=discord.File(fp, filename='message.txt'), **kwargs)
        
        await self.send(content)