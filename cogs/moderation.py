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

from .__init__ import *


class PrefixModal(Modal):
    def __init__(self, bot: DiseasesBot, *args, **kwargs):
        super().__init__(title="Change Prefix", timeout=15, *args, **kwargs)
        self.bot = bot

    prefix = TextInput(label="ใส่ prefix ที่ต้องการ", placeholder="พิมพ์ที่นี่")

    async def on_submit(self, interaction: Interaction) -> InteractionMessage:
        embed = Embed(
            title="Confirm",
            description="Are you sure to change guild prefix?",
            color=Colour.green(),
        )
        view = ConfirmView(
            author=interaction.user,
            bot=self.bot,
            confirm_label="confirm_prefix",
            res=str(self.prefix),
        )
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()


class ModerationModal(Modal):
    def __init__(self, bot: DiseasesBot, mod_type: str, *args, **kwargs):
        super().__init__(title="Moderation", timeout=15, *args, **kwargs)
        self.bot = bot
        self.mod_type = mod_type

    answer = TextInput(label="ใส่ user id", placeholder="provide user id here")
    reason = TextInput(label="ใส่เหตุผล", placeholder="provide a reason")

    def build_embed(self, user: Union[Member, User]) -> Embed:
        return Embed(
            description=f"Are you sure to {self.mod_type.replace('_', ' ')} {user.mention or user}?",
            color=Colour.green(),
        )

    async def on_submit(self, interaction: Interaction) -> InteractionMessage:
        if str(self.answer).isnumeric():
            try:
                guild = interaction.guild

                user: Member = guild.get_member(int(str(self.answer)))
                user2: User = await self.bot.fetch_user(int(str(self.answer)))

                if self.mod_type == "unban":
                    embed = self.build_embed(user=user2)
                    view = ConfirmView(
                        author=interaction.user,
                        bot=self.bot,
                        confirm_label="confirm_unban",
                        res=user2,
                        res2=str(self.reason),
                    )
                    await interaction.response.send_message(embed=embed, view=view)
                    view.message = await interaction.original_response()

                else:
                    if guild.get_member(user.id):
                        embed = self.build_embed(user=user)
                        view = ConfirmView(
                            author=interaction.user,
                            bot=self.bot,
                            confirm_label=f"confirm_{self.mod_type}",
                            res=user,
                            res2=str(self.reason),
                        )
                        await interaction.response.send_message(embed=embed, view=view)
                        view.message = await interaction.original_response()
                    else:
                        embed = Embed(
                            description="Member not found in this server",
                            color=Colour.red(),
                        )
                        await interaction.response.send_message(embed=embed)

            except ValueError:
                embed = Embed(
                    description="Please input a valid user id",
                    color=Colour.red(),
                )
                await interaction.response.send_message(embed=embed)

        else:
            embed = Embed(
                description="Please input a valid user id", color=Colour.red()
            )
            await interaction.response.send_message(embed=embed)

        self.stop()


class ConfirmView(View):
    def __init__(
        self,
        author: Union[Member, User],
        bot: DiseasesBot,
        confirm_label: str,
        res=None,
        res2=None,
        *args,
        **kwargs,
    ):
        super().__init__(timeout=15, *args, **kwargs)
        self.author = author
        self.bot = bot
        self.confirm_label = confirm_label
        self.res = res
        self.res2 = res2

    async def confirm_ban(self, interaction: Interaction) -> InteractionMessage:
        if isinstance(self.res, Member) and isinstance(self.res2, str):
            await self.res.ban(reason=self.res2)
            embed = Embed(
                description=f"<:recommended:976850769426911343> | Banned {self.res.mention} with reason `{self.res2}` successfully",
                color=Colour.red(),
            )
            self.disable_all_items()
            await interaction.response.edit_message(
                embed=embed, view=self, delete_after=10
            )

    async def confirm_unban(self, interaction: Interaction) -> InteractionMessage:
        if isinstance(self.res, User) and isinstance(self.res2, str):
            async for entry in interaction.guild.bans():
                if (entry.user.name, entry.user.discriminator) == (
                    self.res.name,
                    self.res.discriminator,
                ):
                    await interaction.guild.unban(self.res, reason=self.res2)

            embed = Embed(
                description=f"<:recommended:976850769426911343> | Unbanned {self.res.mention} with reason `{self.res2}` successfully",
                color=Colour.green(),
            )

            self.disable_all_items()
            await interaction.response.edit_message(
                embed=embed, view=self, delete_after=10
            )

    async def confirm_prefix(self, interaction: Interaction) -> InteractionMessage:
        embed = Embed(
            description=f"<:recommended:976850769426911343> | Change prefix to `{self.res}` successfully",
            color=Colour.green(),
        )
        await self.bot.db.execute(
            'UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2',
            self.res,
            interaction.guild.id,
        )
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)

    async def reset_prefix(self, interaction: Interaction) -> InteractionMessage:
        embed = Embed(
            description=f"<:recommended:976850769426911343> | Change prefix to `{default_prefix}` successfully",
            color=Colour.green(),
        )
        await self.bot.db.execute(
            'UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2',
            default_prefix,
            interaction.guild.id,
        )
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)

    async def confirm_kick(self, interaction: Interaction) -> InteractionMessage:
        if isinstance(self.res, Member) and isinstance(self.res2, str):
            await self.res.kick(reason=self.res2)

        embed = Embed(
            description=f"<:recommended:976850769426911343> | Kicked {self.res.mention} with reason `{self.res2}` successfully",
            color=Colour.green(),
        )
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)

    @button(label="CONFIRM", style=ButtonStyle.success)
    async def confirm(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        function = getattr(self, self.confirm_label)
        await function(interaction)

    @button(label="CANCEL", style=ButtonStyle.danger)
    async def cancel(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        embed = Embed(description="Canceled.", color=Colour.red())
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)
        self.stop()

    def disable_all_items(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        with suppress(errors.NotFound):
            self.message: InteractionMessage
            self.disable_all_items()
            await self.message.edit(content="⏰| Timed Out...", view=self)

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self.author == interaction.user


class ModPanelView(View):
    def __init__(
        self,
        author: Union[Member, User],
        bot: DiseasesBot,
        *args,
        **kwargs,
    ):
        super().__init__(timeout=30, *args, **kwargs)
        self.author = author
        self.bot = bot
        self._request()

    @button(label="Change Prefix", style=ButtonStyle.primary, row=1)
    async def change_prefix(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.send_modal(PrefixModal(self.bot))

    @button(label="Reset Prefix", style=ButtonStyle.danger, row=1)
    async def reset_prefix(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        embed = Embed(
            title="Confirm",
            description="Are you sure to reset prefix?",
            color=Colour.green(),
        )
        view = ConfirmView(
            author=interaction.user, bot=self.bot, confirm_label="reset_prefix"
        )
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @button(label="Ban User", style=ButtonStyle.danger, row=1)
    async def ban_user(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.send_modal(ModerationModal(self.bot, "ban"))

    @button(label="Kick User", style=ButtonStyle.danger, row=1)
    async def kick_user(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.send_modal(ModerationModal(self.bot, "kick"))

    @button(label="Unban User", style=ButtonStyle.success, row=2)
    async def unban_user(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.send_modal(ModerationModal(self.bot, "unban"))

    @button(style=ButtonStyle.secondary, disabled=True, row=2)
    async def request(self, interaction: Interaction, button: Button) -> None:
        ...

    def _request(self) -> None:
        self.request: Button
        self.request.label = f"Requested by {self.author}"

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self.author == interaction.user


class Moderation(commands.Cog):
    """Commands สำหรับควบคุมการทำงานของบอทใน server นั้นๆ"""

    def __init__(self, bot: DiseasesBot):
        self.bot = bot
        self.database = Database(self.bot)
        self.format = Formatter()

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self) -> None:
        print(f"{self.__class__.__name__.upper()} COG is activated")

    @staticmethod
    def is_admin(author: Union[Member, User]) -> bool:
        return author.guild_permissions.administrator

    @staticmethod
    def no_permissions_embed() -> Embed:
        return Embed(
            description="You don't have `ADMINISTRATOR` permission to run this command",
            color=Colour.red(),
        )

    @app_commands.command(name="set_prefix")
    @app_commands.guild_only()
    @app_commands.describe(prefix="เลือก prefix ตามที่ต้องการ")
    @app_commands.checks.cooldown(1, 30)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_prefix(
        self, interaction: Interaction, prefix: str
    ) -> InteractionMessage:
        """เปลี่ยน prefix ใน server นั้นๆ"""
        if self.is_admin(interaction.user):
            embed = Embed(
                description=f"<:recommended:976850769426911343> | Change prefix to `{prefix}` successfully",
                color=Colour.green(),
            )
            await self.bot.db.execute(
                'UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2',
                prefix,
                interaction.guild.id,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=self.no_permissions_embed())

    @app_commands.command(name="reset_prefix")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 30)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reset_prefix(self, interaction: Interaction) -> InteractionMessage:
        """รีเซ็ต prefix ใน server นั้นๆ"""
        if self.is_admin(interaction.user):
            embed = Embed(
                description=f"<:recommended:976850769426911343> | Reset prefix to `{default_prefix}` successfully",
                color=Colour.green(),
            )
            await self.bot.db.execute(
                'UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2',
                default_prefix,
                interaction.guild.id,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=self.no_permissions_embed())

    @app_commands.command(name="moderation_panel")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 30)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def moderation_panel(self, interaction: Interaction) -> InteractionMessage:
        """หน้าค่าง Interface สำหรับ Admin"""
        if self.is_admin(interaction.user):
            embed = Embed(title="Moderation Panel", color=Colour.red())

            embed.description = (
                "**Available Commands**\n"
                f"{self.format.prefix}yaml\n"
                "Set Prefix | Reset Prefix\n"
                "Ban User   | Unban User\n"
                "Kick User"
                f"{self.format.suffix}\n"
                f"**Server Info : {interaction.guild.name}**\n\n"
                f"🆔 Server ID : {interaction.guild.id}\n"
                f"📆 Created On : {interaction.guild.created_at.strftime('%b %d %Y')}\n"
                f"👑 Owner : {interaction.guild.owner.mention}\n"
                f"👥 Members : {interaction.guild.member_count} **|** 💬 Channels : {len(interaction.guild.channels)}\n"
            )

            embed.set_thumbnail(url=interaction.guild.icon.url)
            view = ModPanelView(interaction.user, self.bot)
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()

        else:
            await interaction.response.send_message(embed=self.no_permissions_embed())


async def setup(bot: DiseasesBot):
    await bot.add_cog(Moderation(bot))
