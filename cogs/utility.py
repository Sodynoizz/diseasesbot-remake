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


class FindPage(Modal):
    def __init__(self, pages: list, view: View):
        super().__init__(title="Goto page")
        self.pages = pages
        self.view = view
        self.add_item(
            TextInput(label="ใส่เลขหน้าที่ต้องการเปิด", style=TextStyle.short)
        )

    async def display(
        self, interaction: Interaction, number: int
    ) -> Union[InteractionMessage, Message]:
        self.indicator_page: Button
        self.view.current_page = number
        self.view.indicator_page.label = (
            f"{self.view.current_page + 1} / {self.view.len_pages}"
        )

        view = await self.view.update_state(self.view.current_page)
        await interaction.response.edit_message(
            embed=self.view._pages[number % self.view.len_pages], view=view
        )

    async def on_submit(self, interaction: Interaction):
        value = str(self.children[0].value)
        if value.isnumeric and int(value) in range(1, 6):
            await self.display(interaction, number=int(value) - 1)
        else:
            await interaction.response.send_message(
                content="**❌ | Please input a valid page number**",
                ephemeral=True,
                delete_after=5,
            )

        self.stop()


class MemberView(View):
    def __init__(self, pages: list):
        super().__init__(timeout=30)
        self._pages = pages
        self.len_pages = len(self._pages)
        self.current_page = 0
        self.interaction = None
        self.message = None

        self.indicator()

    async def start(self, interaction: Interaction):
        self.interaction = interaction
        await self.update_state(self.current_page)
        await self.interaction.response.send_message(embed=self._pages[0], view=self)
        self.message = await self.interaction.original_response()

    @button(
        label="first",
        emoji="<:first_page_white:1058405780895842405>",
        style=ButtonStyle.secondary,
    )
    async def first_page(self, interaction: Interaction, button: Button):
        await self.show_page(interaction, 0)

    @button(
        label="prev",
        emoji="<:previous:999541041327775784>",
        style=ButtonStyle.secondary,
    )
    async def before_page(self, interaction: Interaction, button: Button):
        await self.show_page(interaction, self.current_page - 1)

    @button(emoji="🔍", style=ButtonStyle.primary, disabled=True)
    async def indicator_page(self, interaction: Interaction, button: Button):
        modal = FindPage(self._pages, view=self)
        await interaction.response.send_modal(modal)

    @button(
        label="next",
        emoji="<:next:999541035304747120>",
        style=ButtonStyle.secondary,
    )
    async def next_page(self, interaction: Interaction, button: Button):
        await self.show_page(interaction, self.current_page + 1)

    @button(
        label="last",
        emoji="<:last_page_white:1058405905592500365>",
        style=ButtonStyle.secondary,
    )
    async def last_page(self, interaction: Interaction, button: Button):
        await self.show_page(interaction, self.len_pages - 1)

    def refresh_state(self, is_disabled: bool = False) -> None:
        for child in self.children:
            child.disabled = is_disabled

    def indicator(self) -> None:
        self.indicator_page: Button
        self.indicator_page.label = f"{self.current_page + 1} / {self.len_pages}"

    async def show_page(
        self, interaction: Interaction, number: int
    ) -> Union[InteractionMessage, Message]:
        self.indicator_page: Button
        self.current_page = number
        self.indicator_page.label = f"{self.current_page + 1} / {self.len_pages}"

        view = await self.update_state(self.current_page)
        await interaction.response.edit_message(
            embed=self._pages[number % self.len_pages], view=view
        )

    async def update_state(self, page: int) -> Self:
        self.refresh_state()

        if page == 0:
            self.first_page.disabled = True
            self.before_page.disabled = True

        elif page == self.len_pages - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True

        return self

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self.interaction.user == interaction.user

    async def on_timeout(self) -> None:
        self.indicator_page: Button
        self.refresh_state(is_disabled=True)
        self.indicator_page.label = f"1/{self.len_pages}"
        await self.message.edit(embed=self._pages[0], view=self)
        self.stop()


class InviteView(View):
    def __init__(self, bot: DiseasesBot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.build_button()

    def build_button(self) -> None:
        self.add_item(Button(label="Discord Server", url=self.bot.server_invite))
        self.add_item(Button(label="Invite this bot", url=self.bot.bot_invite))


class Utility(commands.Cog):
    """Commands ทั่วไปเช่นสถานะบอท หรือสมาชิกผู้จัดทำเป็นต้น"""

    def __init__(self, bot: DiseasesBot):
        self.bot = bot
        self.database = Database(self.bot)

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self) -> None:
        print(f"{self.__class__.__name__.upper()} COG is activated")

    @property
    async def database_ping(self) -> list:
        await self.database.fetch_rates()

    @staticmethod
    def build_pages(member: dict) -> list:

        description = "รายชื่อ**สมาชิกผู้จัดทำ**โครงงาน\n```"
        for index in range(5):
            description += f"{index+1}.) {member[index]['name']} เลขที่ {member[index]['number']}\n"
        description += "```"

        homeembed = Embed(
            title="สมาชิกผู้จัดทำโครงงาน Diseases Bot",
            description=description,
            color=Colour.green(),
        )
        homeembed.set_image(
            url="https://media.discordapp.net/attachments/780424031035457588/1023543726716493834/Pandemic.jpg"
        )
        members = [homeembed]

        for index in range(5):
            embed = Embed(
                title="รายชื่อสมาชิกผู้จัดทำโครงงาน", color=Colour.dark_theme()
            )
            embed.description = (
                f"```ชื่อ-นามสกุล : {member[index]['name']}\nชื่อเล่น : {member[index]['nickname']}\n"
                f"เลขที่  : {member[index]['number']}\nIG    : {member[index]['instagram']}```"
            )
            embed.set_thumbnail(url=member[index]["thumbnail"])
            embed.set_footer(text=f"Page {index+2}/6")
            members.append(embed)

        return members

    @app_commands.command(name="member")
    @app_commands.checks.cooldown(1, 15)
    async def member(self, interaction: Interaction) -> InteractionMessage:
        """สมาชิกผู้จัดทำโครงงาน"""
        member = await self.database.fetch_members()
        pages = self.build_pages(member)

        menu = MemberView(pages)
        await menu.start(interaction)

    @app_commands.command(name="invite")
    @app_commands.checks.cooldown(1, 10)
    async def invite(self, interaction: Interaction) -> InteractionMessage:
        """เชิญบอทเข้า server"""
        description = f"Discord Server : [`click here`]({self.bot.server_invite})\n"
        description += f"Invite this bot : [`click here`]({self.bot.bot_invite})"

        embed = Embed(title="Invite", color=Colour.dark_purple())
        embed.description = description
        embed.set_image(
            url="https://media.discordapp.net/attachments/780424031035457588/1023543726716493834/Pandemic.jpg"
        )
        # embed.set_thumbnail(url=self.bot.user.display_avatar())
        await interaction.response.send_message(embed=embed, view=InviteView(self.bot))

    @app_commands.command(name="ping")
    @app_commands.checks.cooldown(1, 10)
    async def ping(self, interaction: Interaction) -> InteractionMessage:
        """เช็คความหน่วงของบอท"""
        # Bot Ping
        bot_ping = round(self.bot.latency * 1000)

        # Database Ping
        before = time.monotonic()
        _ = await self.database_ping
        database_ping = round((time.monotonic() - before) * 1000)

        # API Ping
        before = time.monotonic()
        await interaction.response.send_message(
            content="Sending ping...", delete_after=0.25
        )
        api_ping = round((time.monotonic() - before) * 1000)

        description = (
            f"<:database:1060915738715631716> **Database Ping** ( __PostgreSQL__ ) : `{database_ping}` ms\n"
            f"<:DiscordBot:965606603774652446> **Bot Ping** : `{bot_ping}` ms\n"
            f"<a:latency:1022733012464582746> **API Ping** : `{api_ping}` ms"
        )

        embed = Embed(title="Ping", description=description, color=Colour.dark_theme())
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )
        await interaction.channel.send(embed=embed)


async def setup(bot: DiseasesBot):
    await bot.add_cog(Utility(bot))
