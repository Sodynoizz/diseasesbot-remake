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
    
    # def cog_load(self):
    #     tree = self.bot.tree
    #     self._old_tree_error = tree.on_error
    #     tree.on_error = self.on_app_command_error

    # def cog_unload(self):
    #     tree = self.bot.tree
    #     tree.on_error = self._old_tree_error
        
    # async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    #     embed = discord.Embed(color=discord.Colour.red())
    #     if getattr(interaction, 'handled', False):
    #         return
    
    #     if isinstance(error, app_commands.CommandOnCooldown):
    #         embed.description = f"⏰ | Command is cooldown. Please retry after `{error.retry_after:.2f}s`."
    #     else:
    #         embed.description = "❌ | Something went wrong internally."
        
    #     await interaction.response.send_message(embed=embed, ephemeral=True)
        
    
async def setup(bot: DiseasesBot):
    await bot.add_cog(Error(bot))
    