from __future__ import annotations

from typing import *

if TYPE_CHECKING:
    from bot import DiseasesBot
    from aiohttp import ClientSession
    
from datetime import datetime
import discord
from discord import *
from discord.ext import commands

from humanfriendly import parse_date
import io
from io import BytesIO
import json

from time import mktime

from .formatter import Formatter
from config.secret import *
