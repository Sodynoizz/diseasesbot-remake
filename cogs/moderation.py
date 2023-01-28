import contextlib
import discord
from discord import app_commands, utils
from discord.ext import commands
from discord.ui import Button,Modal, TextInput, View
from typing import Union

from bot import DiseasesBot
from config import secret

from utils.database import Database
from utils.formatter import Formatter


class PrefixModal(Modal):
    def __init__(self, bot: DiseasesBot, *args, **kwargs):
        super().__init__(title="Change Prefix", timeout=15, *args, **kwargs)
        self.bot = bot
    
    prefix = TextInput(label="ใส่ prefix ที่ต้องการ", placeholder="พิมพ์ที่นี่")
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Confirm", 
                              description="Are you sure to change guild prefix?", 
                              color=discord.Colour.green())
        view = ConfirmView(author=interaction.user, bot=self.bot, confirm_label="confirm_prefix", res=str(self.prefix))
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()


class ModerationModal(Modal):
    def __init__(self, bot: DiseasesBot, mod_type: str, *args, **kwargs):
        super().__init__(title="Moderation", timeout=15, *args, **kwargs)
        self.bot = bot
        self.mod_type = mod_type    
    
    answer = TextInput(label="ใส่ user id", placeholder="provide user id here")
    reason = TextInput(label="ใส่เหตุผล", placeholder="provide a reason")
    
    def build_embed(self, user: Union[discord.Member, discord.User]) -> discord.Embed: 
        return discord.Embed(description=f"Are you sure to {self.mod_type.replace('_', ' ')} {user.mention or user}?", 
                             color=discord.Colour.green())
    
    async def on_submit(self, interaction: discord.Interaction):
        if str(self.answer).isnumeric():   
            try:
                guild = interaction.guild
                
                user: discord.Member = guild.get_member(int(str(self.answer)))
                user2: discord.User = await self.bot.fetch_user(int(str(self.answer)))
                
                if self.mod_type == "unban":
                    embed = self.build_embed(user=user2)
                    view = ConfirmView(author=interaction.user, bot=self.bot, confirm_label="confirm_unban", res=user2, res2=str(self.reason))
                    await interaction.response.send_message(embed=embed, view=view)
                    view.message = await interaction.original_response()
                    
                else:
                    if guild.get_member(user.id):
                        embed = self.build_embed(user=user)
                        view = ConfirmView(author=interaction.user, bot=self.bot, confirm_label=f"confirm_{self.mod_type}", res=user, res2=str(self.reason))
                        await interaction.response.send_message(embed=embed, view=view)
                        view.message = await interaction.original_response()
                    else:
                        embed = discord.Embed(description="Member not found in this server", color=discord.Colour.red())
                        await interaction.response.send_message(embed=embed)
                    
            except ValueError:
                embed = discord.Embed(description="Please input a valid user id", color=discord.Colour.red())
                await interaction.response.send_message(embed=embed)          
        
        else:
            embed = discord.Embed(description="Please input a valid user id", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed)  
    
        self.stop()


class ConfirmView(View):
    def __init__(self, author: Union[discord.Member, discord.User], bot: DiseasesBot, confirm_label: str, res = None, res2 = None, *args, **kwargs):
        super().__init__(timeout=15, *args, **kwargs) 
        self.author = author
        self.bot = bot
        self.confirm_label = confirm_label
        self.res = res
        self.res2 = res2
        
    async def confirm_ban(self, interaction: discord.Interaction):
        if isinstance(self.res, discord.Member) and isinstance(self.res2, str):
            await self.res.ban(reason=self.res2)
            embed = discord.Embed(description=f"<:recommended:976850769426911343> | Banned {self.res.mention} with reason `{self.res2}` successfully",
                                  color=discord.Colour.red())
            self.disable_all_items()
            await interaction.response.edit_message(embed=embed, view=self, delete_after=10)
    
    async def confirm_unban(self, interaction: discord.Interaction):
        if isinstance(self.res, discord.User) and isinstance(self.res2, str):
            async for entry in interaction.guild.bans():
                if (entry.user.name, entry.user. discriminator) == (self.res.name, self.res.discriminator):
                    await interaction.guild.unban(self.res, reason=self.res2)
                
            embed = discord.Embed(description=f"<:recommended:976850769426911343> | Unbanned {self.res.mention} with reason `{self.res2}` successfully",
                                  color=discord.Colour.green())   
            
            self.disable_all_items()
            await interaction.response.edit_message(embed=embed, view=self, delete_after=10)
           
    async def confirm_prefix(self, interaction: discord.Interaction):
        embed = discord.Embed(description=f"<:recommended:976850769426911343> | Change prefix to `{self.res}` successfully",
                              color=discord.Colour.green())
        await self.bot.db.execute('UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2', self.res, interaction.guild.id)
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)
        
    async def reset_prefix(self, interaction: discord.Interaction):
        embed = discord.Embed(description=f"<:recommended:976850769426911343> | Change prefix to `{secret.default_prefix}` successfully",
                              color=discord.Colour.green())
        await self.bot.db.execute('UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2', secret.default_prefix, interaction.guild.id)
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)
    
    async def confirm_kick(self, interaction: discord.Interaction):
        if isinstance(self.res, discord.Member) and isinstance(self.res2, str):
            await self.res.kick(reason=self.res2)
            
        embed = discord.Embed(description=f"<:recommended:976850769426911343> | Kicked {self.res.mention} with reason `{self.res2}` successfully",
                              color=discord.Colour.green())
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)
        
    @discord.ui.button(label="CONFIRM", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        function = getattr(self, self.confirm_label)
        await function(interaction)
        
    @discord.ui.button(label="CANCEL", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(description="Canceled.", color=discord.Colour.red())
        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self, delete_after=10)
        self.stop()
    
    def disable_all_items(self) -> None:
        for child in self.children:
            child.disabled = True
            
    async def on_timeout(self):
        with contextlib.suppress(discord.errors.NotFound):
            self.message: Union[discord.Message, discord.InteractionMessage]
            self.disable_all_items()
            await self.message.edit(content="⏰| Timed Out...", view=self)
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.author == interaction.user
    
class ModPanelView(View):
    def __init__(self, author: Union[discord.Member, discord.User], bot: DiseasesBot, *args, **kwargs):
        super().__init__(timeout=30, *args, **kwargs)
        self.author = author
        self.bot = bot
        self._request()
        
    @discord.ui.button(label="Change Prefix", style=discord.ButtonStyle.primary, row=1)
    async def change_prefix(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(PrefixModal(self.bot))
        
    @discord.ui.button(label="Reset Prefix", style=discord.ButtonStyle.danger, row=1)
    async def reset_prefix(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(title="Confirm", description="Are you sure to reset prefix?", color=discord.Colour.green())
        view = ConfirmView(author=interaction.user, bot=self.bot, confirm_label="reset_prefix")
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
    
    @discord.ui.button(label="Ban User", style=discord.ButtonStyle.danger, row=1)
    async def ban_user(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ModerationModal(self.bot, "ban"))
    
    @discord.ui.button(label="Kick User", style=discord.ButtonStyle.danger, row=1)
    async def kick_user(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ModerationModal(self.bot, "kick"))
        
    @discord.ui.button(label="Unban User", style=discord.ButtonStyle.success, row=2)
    async def unban_user(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ModerationModal(self.bot, "unban"))
    
    @discord.ui.button(style=discord.ButtonStyle.secondary, disabled=True, row=2)
    async def request(self, interaction: discord.Interaction, button: Button):
        ...
    
    def _request(self) -> None:
        self.request : discord.ui.Button
        self.request.label = f"Requested by {self.author}"
        
    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
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
    def is_admin(author: Union[discord.Member, discord.User]) -> bool:
        return author.guild_permissions.administrator
    
    @staticmethod
    def no_permissions_embed() -> discord.Embed:
        return discord.Embed(description="You don't have `ADMINISTRATOR` permission to run this command",
                             color=discord.Colour.red())
        
    @app_commands.command(name="set_prefix")
    @app_commands.guild_only()
    @app_commands.describe(prefix="เลือก prefix ตามที่ต้องการ")
    @app_commands.checks.cooldown(1, 30)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_prefix(self, interaction: discord.Interaction, prefix: str) -> Union[discord.Message, discord.InteractionMessage]:
        """เปลี่ยน prefix ใน server นั้นๆ"""
        if self.is_admin(interaction.user):
            embed = discord.Embed(description=f"<:recommended:976850769426911343> | Change prefix to `{prefix}` successfully",
                                color=discord.Colour.green())
            await self.bot.db.execute('UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2', prefix, interaction.guild.id)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_essage(embed=self.no_permissions_embed())
    
    @app_commands.command(name="reset_prefix")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 30)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reset_prefix(self, interaction: discord.Interaction) -> discord.InteractionMessage:
        """รีเซ็ต prefix ใน server นั้นๆ"""
        if self.is_admin(interaction.user):
            embed = discord.Embed(description=f"<:recommended:976850769426911343> | Reset prefix to `{secret.default_prefix}` successfully",
                                color=discord.Colour.green())
            await self.bot.db.execute('UPDATE guilds SET prefix = $1 WHERE "guild_id" = $2', secret.default_prefix, interaction.guild.id)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_essage(embed=self.no_permissions_embed())
    
    @app_commands.command(name="moderation_panel")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 30)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def moderation_panel(self, interaction: discord.Interaction) -> discord.InteractionMessage:
        """หน้าค่าง Interface สำหรับ Admin"""
        if self.is_admin(interaction.user):
            embed = discord.Embed(title="Moderation Panel", color=discord.Colour.red())
            
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
            
            embed.set_thumbnail(url = interaction.guild.icon.url)
            view = ModPanelView(interaction.user, self.bot)
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()
            
        else:
            await interaction.response.send_message(embed=self.no_permissions_embed())
        
async def setup(bot: DiseasesBot):
    await bot.add_cog(Moderation(bot))
    