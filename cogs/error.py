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

import discord
from discord import app_commands
from discord.ext import commands

from bot import DiseasesBot


class Error(commands.Cog):
    def __init__(self, bot: DiseasesBot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        print(f"{self.__class__.__name__.upper()} COG is activated")

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_app_command_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    def build_error_embed(self, error) -> discord.Embed:
        embed = discord.Embed(color=discord.Colour.red())
        embed.title = "❌ | Something went wrong internally."

        if isinstance(error, app_commands.CommandOnCooldown):
            embed.add_field(
                name="Error Message:",
                value=f"```⏰ | Command is cooldown. Please retry after {error.retry_after:.2f}s.```",
            )
        else:
            embed.add_field(name="Error Message: ", value=f"```{error}```")

        return embed

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if getattr(interaction, "handled", False):
            return

        await interaction.response.send_message(
            embed=self.build_error_embed(error), delete_after=5, ephemeral=True
        )

    @commands.Cog.listener(name="on_command_error")
    async def on_prefix_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        await ctx.reply(embed=self.build_error_embed(error), delete_after=5)


async def setup(bot: DiseasesBot):
    await bot.add_cog(Error(bot))
