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

from bot import DiseasesBot

import asyncio
import contextlib
import discord
import click
import logging

from logging.handlers import RotatingFileHandler

class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name='discord.state')
    
    def filter(self, record: logging.LogRecord) -> bool:
        return (
            record.levelname != 'WARNING'
            or 'referencing an unknown' not in record.msg
        )

@contextlib.contextmanager
def setup_logging() -> None:
    log = logging.getLogger()
    
    try:
        discord.utils.setup_logging()

        max_bytes = 32 * 1024 * 1024
        
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())
        
        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename='sodynoizz.log', encoding='utf-8', mode='w', maxBytes=max_bytes, backupCount=5)
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)
            
        yield 
    
    finally:
        handlers = log.handlers[:]
        for handler in handlers:
            handler.close()
            log.removeHandler(handler)

async def run_bot() -> None:
    async with DiseasesBot() as bot:
        await bot.start()

@click.group(invoke_without_command=True, options_metavar='[options]')
@click.pass_context
def main(ctx) -> None:
    """Launches the bot."""
    if ctx.invoked_subcommand is None:
        with setup_logging():
            asyncio.run(run_bot())
    
if __name__ == '__main__':
    main()
            