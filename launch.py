from bot import DiseasesBot

import asyncpg
import asyncio
import contextlib
import discord
import click
import logging
import sys

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
    
async def create_pool() -> asyncpg.Pool:
    ...       

async def run_bot() -> None:
    log = logging.getLogger()
    
    try:
        pool = await create_pool()
        
    except Exception:
        click.echo('Could not set up PostgresSQL. Exiting.', file=sys.stderr)
        log.exception('Could not set up PostgresSQL. Exiting.')
        return 

    async with DiseasesBot() as bot:
        bot.pool = pool
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
            