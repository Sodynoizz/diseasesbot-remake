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
from discord.ui import Button, Modal, Select, TextInput, View
from typing import Union

from bot import DiseasesBot
from utils.database import Database
from config import secret


class ReportModal(Modal):
    def __init__(self, bot: DiseasesBot, *args, **kwargs):
        super().__init__(title="รายงานปัญหา / ข้อเสนอแนะ", timeout=30, *args, **kwargs)
        self.bot = bot

    name = TextInput(
        label="ชื่อปัญหา / ข้อเสนอแนะ",
        placeholder="ระบุชื่อปัญหาที่นี่",
        style=discord.TextStyle.short,
    )
    description = TextInput(
        label="อธิบายปัญหา",
        placeholder="อธิบายปัญหาที่นี่",
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        channel = self.bot.get_channel(secret.report_channel)

        embed = discord.Embed(
            title=f"{str(self.name).title()}",
            description=f"```{self.description}```",
            color=discord.Colour.red(),
        )
        embed.set_footer(text=f"Requested by {user}", icon_url=user.avatar.url)

        message = await channel.send(embed=embed)

        await interaction.response.send_message(
            content="<:recommended:976850769426911343> | **Report Success!**",
            delete_after=5,
            ephemeral=True,
        )
        await user.send(
            content=f"<:recommended:976850769426911343> | คุณได้ทำการแจ้งปัญหาไปที่ {channel.mention} เรียบร้อยแล้ว",
            embed=embed,
            view=ReportView(url=message.jump_url, user=user),
        )


class ReportView(View):
    def __init__(
        self, url: str, user: Union[discord.Member, discord.User], *args, **kwargs
    ):
        super().__init__(timeout=None, *args, **kwargs)
        self.url = url
        self.user = user
        self.add_item(
            Button(
                label="Jump to message",
                emoji="<a:messages:1059126380723437589>",
                url=self.url,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.user == interaction.user


class RateView(View):
    def __init__(
        self,
        bot: DiseasesBot,
        user: Union[discord.Member, discord.User],
        *args,
        **kwargs,
    ):
        super().__init__(timeout=15, *args, **kwargs)
        self.bot = bot
        self.user = user
        self.database = Database(self.bot)
        self.build_select()

    def build_select(self) -> None:
        self.callback: Select
        for i in range(1, 6):
            if i == 1:
                self.callback.add_option(label="⭐", description="Give a star", value=i)
            else:
                self.callback.add_option(
                    label="⭐" * i, description=f"Give {i} stars", value=i
                )

    @discord.ui.select(placeholder="Rate Here")
    async def callback(self, interaction: discord.Interaction, select: Select):
        rates = await self.database.fetch_rates()
        rates[0] += 1
        rates[1] += int(select.values[0])

        try:
            average = rates[1] / rates[0]
        except ZeroDivisionError:
            average = 0

        description = (
            f"You rate this bot for `{select.values[0]}`\nCurrent rating is {average}/5"
        )

        await self.database.update_rate(clients=rates[0], scores=rates[1])

        embed = discord.Embed(
            title="Rate Successful",
            description=description,
            color=discord.Colour.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.user == interaction.user

    async def on_timeout(self) -> None:
        self.message: Union[discord.Message, discord.InteractionMessage]
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


class Report(commands.Cog):
    """Commands รายงานปัญหาต่างๆ รวมไปถึงข้อเสนอแนะเกี่ยวกับบอท"""

    def __init__(self, bot: DiseasesBot):
        self.bot = bot
        self.database = Database(self.bot)

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self) -> None:
        print(f"{self.__class__.__name__.upper()} COG is activated")

    @app_commands.command(name="report")
    @app_commands.checks.cooldown(1, 30)
    async def report(
        self, ctx: commands.Context
    ) -> Union[discord.Message, discord.InteractionMessage]:
        """รายงานปัญหาเกี่ยวกับบอท"""
        await ctx.interaction.response.send_modal(ReportModal(self.bot))

    @app_commands.command(name="vote")
    @app_commands.checks.cooldown(1, 30)
    async def vote(
        self, interaction: discord.Interaction
    ) -> Union[discord.Message, discord.InteractionMessage]:
        """โหวตให้คะแนนบอท"""
        view = RateView(bot=self.bot, user=interaction.user)

        embed = discord.Embed(
            title="Vote Command",
            description="ให้คะแนนบอท <@1040974651247034418>",
            color=discord.Colour.blurple(),
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )

        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @app_commands.command(name="rating")
    @app_commands.checks.cooldown(1, 30)
    async def rating(
        self, interaction: discord.Interaction
    ) -> discord.InteractionMessage:
        """เช็คเรตติ้งของบอท"""
        rates = await self.database.fetch_rates()

        try:
            average = rates[1] / rates[0]
        except ZeroDivisionError:
            average = 0

        description = f"**Current rating of this bot is** `{average}/5`\n```yaml\nTOTAL SCORES : {rates[1]}\nTOTAL VOTES  : {rates[0]}```"
        embed = discord.Embed(description=description, color=discord.Colour.yellow())
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: DiseasesBot):
    await bot.add_cog(Report(bot))
