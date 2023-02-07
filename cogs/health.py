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


class CovidStatsView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_sources = "https://covid19.ddc.moph.go.th/"
        self.dashboard = (
            "https://www.arcgis.com/apps/dashboards/bda7594740fd40299423467b48e9ecf6"
        )
        self.build_buttons()

    def build_buttons(self) -> None:
        self.add_item(Button(label="แหล่งที่มา API", emoji="🔗", url=self.api_sources))
        self.add_item(Button(label="แดชบอร์ด", emoji="🔗", url=self.dashboard))


class DiseasesView(View):
    def __init__(self, source: str, picsource: str):
        super().__init__(timeout=None)
        self.source = source
        self.picsource = picsource
        self.build_buttons()

    def build_buttons(self) -> None:
        self.add_item(
            Button(emoji="ℹ️", label="Source", url=self.source, style=ButtonStyle.link)
        )
        self.add_item(
            Button(
                emoji="🖼️",
                label="Picture Source",
                url=self.picsource,
                style=ButtonStyle.link,
            )
        )


class RecordPaginator(View):
    def __init__(self, interaction: Interaction, embed_lists: list):
        super().__init__(timeout=30)
        self.interaction = interaction
        self.current_page = 0
        self.pages = embed_lists
        self.max_page = len(self.pages)
        self.initialize_page()

    async def start(self) -> InteractionMessage:
        self.initialize_view(0)
        await self.interaction.response.send_message(embed=self.pages[0], view=self)
        self.message = await self.interaction.original_response()

    async def show_page(
        self, interaction: Interaction, page: int
    ) -> InteractionMessage:
        self.current_page = page
        self.initialize_page()
        self.initialize_view(self.current_page)
        await interaction.response.edit_message(
            embed=self.pages[page % self.max_page], view=self
        )
        self.message = await interaction.original_response()

    @button(
        label="first",
        emoji="<:first_page_white:1058405780895842405>",
        style=ButtonStyle.secondary,
    )
    async def first_page(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        await self.show_page(interaction, 0)

    @button(
        label="prev",
        emoji="<:previous:999541041327775784>",
        style=ButtonStyle.secondary,
    )
    async def previous_page(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        await self.show_page(interaction, self.current_page - 1)

    @button(style=ButtonStyle.primary, disabled=True)
    async def page_indicator(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        ...

    @button(
        label="next",
        emoji="<:next:999541035304747120>",
        style=ButtonStyle.secondary,
    )
    async def next_page(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        await self.show_page(interaction, self.current_page + 1)

    @button(
        label="last",
        emoji="<:last_page_white:1058405905592500365>",
        style=ButtonStyle.secondary,
    )
    async def last_page(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        await self.show_page(interaction, self.max_page - 1)

    def extract(self, arg1: bool, arg2: bool) -> None:
        self.first_page.disabled = arg1
        self.previous_page.disabled = arg1
        self.next_page.disabled = arg2
        self.last_page.disabled = arg2

    def initialize_page(self) -> None:
        self.page_indicator: Button
        self.page_indicator.label = (
            f"{(self.current_page%self.max_page)+1}/{self.max_page}"
        )

    def initialize_view(self, page: int) -> None:
        if page == 0:
            self.extract(True, False)
        elif page == self.max_page - 1:
            self.extract(False, True)
        else:
            self.extract(False, False)

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self.interaction.user == interaction.user

    async def on_timeout(self) -> None:
        self.message: InteractionMessage
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


class RecordHealth(Modal):
    def __init__(
        self,
        bot: DiseasesBot,
        user: Union[Member, User],
        primary: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(title="Health Record", *args, **kwargs)
        self.bot = bot
        self.user = user
        self.primary = primary

    description = TextInput(label="รายงานผลสุขภาพประจำวันนี้", style=TextStyle.long)

    async def on_submit(self, interaction: Interaction) -> InteractionMessage:
        date = Formatter.unix_formatter(datetime.now(timezone.utc))
        embed = Embed(
            title="ยืนยันการรายงานหรือไม่",
            description=f"```{str(self.description)}```",
            color=Colour.yellow(),
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )
        view = ConfirmSend(
            bot=self.bot, user=interaction.user, time=date, reason=str(self.description)
        )
        if not self.primary:
            view.message = await self.message.edit(embed=embed, view=view)
            return await interaction.response.send_message(
                content=f"Edited to `{self.description}`", delete_after=5
            )

        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()


class ConfirmSend(View):
    def __init__(
        self,
        bot: DiseasesBot,
        user: Union[Member, User],
        time: int,
        reason: str,
        *args,
        **kwargs,
    ):
        super().__init__(timeout=30, *args, **kwargs)
        self.bot = bot
        self.user = user
        self.time = time
        self.reason = reason
        self.database = Database(self.bot)

    @button(label="confirm", style=ButtonStyle.success)
    async def confirm(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        self.disable_all_items()
        await self.database.health_info_entry(
            interaction.user.id, time=self.time, reason=self.reason
        )
        embed = Embed(
            title="รายงานผลสำเร็จ : ",
            description=f"```{self.reason}```",
            color=Colour.green(),
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @button(label="edit", style=ButtonStyle.danger)
    async def edit(
        self, interaction: Interaction, button: Button
    ) -> InteractionMessage:
        modal = RecordHealth(self.bot, interaction.user, primary=False)
        await interaction.response.send_modal(modal)
        modal.message = await interaction.original_response()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self.user == interaction.user

    def disable_all_items(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        self.disable_all_items()
        self.message: InteractionMessage
        with suppress(TypeError, errors.NotFound):
            await self.message.edit(view=self)
            await asyncio.sleep(5)
            await self.message.delete()


class Health(commands.Cog):
    """Commands สำหรับข้อมูลเกี่ยวกับสุขภาพ"""

    def __init__(self, bot: DiseasesBot):
        self.bot = bot
        self.database = Database(self.bot)

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self) -> None:
        self.disease = await self.database.fetch_diseases()
        print(f"{self.__class__.__name__.upper()} COG is activated")

    @app_commands.command(name="diseases")
    @app_commands.checks.cooldown(1, 10)
    @app_commands.describe(diseases_name="เลือกโรคที่ต้องการ")
    async def diseases(
        self, interaction: Interaction, diseases_name: str
    ) -> InteractionMessage:
        """ตรวจสอบรายละเอียดโรคระบาดแต่ละโรค"""
        info = None

        for index, value in enumerate(list(self.disease)):
            if self.disease[index]["name"] == diseases_name:
                info = self.disease[index]

        embed = Embed(
            title=info["name"],
            description=f"```{info['description']}```",
            color=Colour.dark_theme(),
        )

        embed.add_field(
            name="สาเหตุการเกิดโรค", value=f"> {info['cause']}", inline=False
        )
        embed.add_field(
            name="วิธีการป้องกัน", value=f"> {info['protection']}", inline=False
        )
        embed.add_field(
            name="วิธีการรักษา", value=f"> {info['treatment']}", inline=False
        )

        embed.set_footer(
            text=f"แหล่งที่มา : {info['source']}", icon_url=info["thumbnail"]
        )

        view = DiseasesView(source=info["source"], picsource=info["picsource"])
        await interaction.response.send_message(embed=embed, view=view)

    @diseases.autocomplete("diseases_name")
    async def diseases_autocomplete(
        self, interaction: Interaction, current: str
    ) -> list(app_commands.Choice[str]):
        choices = [self.disease[i]["name"] for i in list(self.disease)]

        return (
            app_commands.Choice(name=choice, value=choice)
            for choice in choices
            if current.lower() in choice.lower()
        )

    @app_commands.command(name="covid_stats")
    @app_commands.checks.cooldown(1, 15)
    async def covid_stats(self, interaction: Interaction) -> InteractionMessage:
        """รายงานสถิติโควิด-19 ในประเทศไทย"""
        data = await self.database.fetch_covid_data()
        embed = Embed(
            title="รายงานสถานการณ์โรคระบาดโควิด-19", color=Colour.dark_theme()
        )
        embed.description = ""

        for index, (name, value) in enumerate(data.items()):
            if index != len(data) - 1:
                embed.description += f"> {str(name)} : {value}\n"
            else:
                embed.description += f"\n**{name}** : {value}"

        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )
        embed.set_image(
            url="https://media.discordapp.net/attachments/780424031035457588/1023543726716493834/Pandemic.jpg"
        )

        view = CovidStatsView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="record")
    @app_commands.checks.cooldown(1, 30)
    async def record(self, interaction: Interaction) -> InteractionMessage:
        """บันทึกรายงานสุขภาพประจำวัน"""
        await interaction.response.send_modal(RecordHealth(self.bot, interaction.user))

    @app_commands.command(name="record_view")
    @app_commands.checks.cooldown(1, 15)
    async def view_record(self, interaction: Interaction) -> InteractionMessage:
        """ดูบันทึกการรายงาานสุขภาพของตนเอง"""
        data = await self.database.health_info_logs(user_id=interaction.user.id)
        if data == []:
            embed = Embed(
                description=f"{interaction.user.mention} ยังไม่เคยมีข้อมูลบันทึกรายงานสุขภาพของคุณ",
                color=Colour.red(),
            )
            return await interaction.response.send_message(embed=embed)

        health_report = data[1]
        times = data[2]
        embed_lists = []

        for index, value in enumerate(data):
            with suppress(IndexError):
                embed = Embed(
                    title=f"รายงานผลของ {interaction.user.name}",
                    color=Colour.green(),
                )
                embed.add_field(
                    name=f"ผลรายงานครั้งที่ {index+1}",
                    value=f"รายงานเมื่อวันที่ : <t:{times[index]}:f>```{health_report[index]}```",
                    inline=False,
                )
                embed.set_footer(
                    text=f"Requested by {interaction.user}",
                    icon_url=interaction.user.avatar.url,
                )
                embed_lists.append(embed)

        view = RecordPaginator(interaction, embed_lists)
        await view.start()

    @app_commands.command(name="record_delete")
    @app_commands.checks.cooldown(1, 30)
    @app_commands.describe(user="เลือก user ที่ต้องการจะลบข้อมูล")
    async def delete(
        self,
        interaction: Interaction,
        user: Union[User, Member] = None,
    ) -> InteractionMessage:
        """ลบฐานข้อมูลของ user ทั้งหมดหรือเฉพาะคน"""

        if interaction.user.id in [self.bot.owner.id, self.bot.partner_id]:
            if user:
                await self.database.delete(user_id=user.id)
                embed = Embed(
                    description=f"✅| Delete {user.mention} successfully!",
                    color=Colour.green(),
                )

            else:
                await self.database.delete()
                embed = Embed(
                    description="✅| Delete all info in database successfully!",
                    color=discord.Colour.green(),
                )

        else:
            embed = Embed(
                description="คุณไม่มีสิทธิ์ในการลบข้อมูล user ได้",
                color=Colour.red(),
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot: DiseasesBot):
    await bot.add_cog(Health(bot))
