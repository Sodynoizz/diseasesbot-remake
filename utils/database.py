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

import aiohttp
from discord.ext import commands
import json
from typing import Optional

from config import secret 
from .formatter import Formatter

class Database:
    """
        คลาสสำหรับการสร้าง DATABASE เพื่อใช้ในการเก็บข้อมูลดังนี้
        1.) Rates -> คะแนนความพึงพอใจของการใช้บอทตัวนี้
        2.) Members -> สมาชิกผู้จัดทำ
        3.) Diseases -> รายละเอียดข้อมูลโรคระบาด
        4.) Prefixes -> Prefix ของบอทในแต่ละ server
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.format = Formatter()
    
    async def fetch_rates(self) -> list:
        scores = await self.bot.db.fetch('SELECT scores FROM rates WHERE scores = "scores"')
        clients = await self.bot.db.fetch('SELECT clients FROM rates WHERE clients = "clients"')
        
        res = [int(score["scores"]) for score in scores]
        res.extend(int(client["clients"]) for client in clients)
        return res
        
    async def reset_rates(self) -> None:
        await self.bot.db.execute('TRUNCATE TABLE rates')
        await self.bot.db.execute('INSERT INTO rates (clients, scores) VALUES (0, 0)')
    
    async def update_rates(self, clients:int, scores:int) -> None:
        await self.bot.db.execute('UPDATE rates SET clients = $1, scores = $2', clients, scores)

    async def health_info_logs(self, user_id: int) -> list:
        data = await self.bot.db.fetchrow('SELECT * FROM health WHERE user_id = $1', user_id)
        return data or []
    
    async def health_info_entry(self, user_id: int, time: int, reason: str) -> None:
        data = await self.health_info_logs(user_id)
        if data == []:
            new_user = [reason]
            new_user_time = [time]
            await self.bot.db.execute('INSERT INTO health (user_id, health_report, time) VALUES ($1, $2, $3)', user_id, new_user, new_user_time)
            return
        
        health_report = data[1]
        times = data[2]
        health_report.append(reason)
        times.append(time)
        await self.bot.db.execute('UPDATE health SET health_report = $1, time = $2 WHERE user_id = $3', health_report, times, user_id)
    
    async def delete(self, user_id: int = None) -> None:
        if user_id is None:
            await self.bot.db.execute('DELETE FROM health')
        else:
            await self.bot.db.execute('DELETE FROM health WHERE user_id = $1', user_id)
        
    @staticmethod
    async def fetch_members() -> dict:
        mapping = {}
        with open("databases/member.json", "r", encoding="utf-8") as member:
            data = json.load(member)
            for index, value in enumerate(list(data)):
                mapping[index] = dict(
                    name = data[f"{index+1}"]["name"],
                    nickname = data[f"{index+1}"]["nickname"],
                    number = data[f"{index+1}"]["number"],
                    instagram = data[f"{index+1}"]["instagram"],
                    thumbnail = data[f"{index+1}"]["thumbnail"]
                )
                
            return mapping
    
    @staticmethod
    async def fetch_diseases() -> dict:
        mapping = {}
        with open("databases/diseases.json", "r", encoding="utf-8") as diseases:
            data = json.load(diseases)
            for index, value in enumerate(list(data)):
                mapping[index] = dict(
                    name = data[str(index+1)]["name"],
                    description = data[str(index+1)]["description"],
                    cause = data[str(index+1)]["cause"],
                    protection = data[str(index+1)]["protection"],
                    treatment = data[str(index+1)]["treatment"],
                    thumbnail = data[str(index+1)]["thumbnail"],
                    source = data[str(index+1)]["source"],
                    picsource = data[str(index+1)]["picsource"],   
                )
                
            return mapping

    async def fetch_covid_data(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(secret.covid_api) as response:
                res = await response.json()
                result = res[0]
                
                unix_time = Formatter.unix_formatter(result["update_date"])
                
                return dict(
                    ปีพุทธศักราช = f"`{int(result['year']) + 543}`",
                    สัปดาห์ที่ = f"`{result['weeknum']}`",
                    จำนวนผู้ป่วยรายใหม่ = f"`{result['new_case']}` คน",
                    จำนวนผู้ป่วยสะสม = f"`{result['total_case']}` คน",
                    จำนวนผู้ป่วยรายใหม่ไม่รวมผู้ป่วยต่างชาติ = f"`{result['new_case_excludeabroad']}` คน",
                    จำนวนผู้ป่วยสะสมไม่รวมผู้ป่วยต่างชาติ = f"`{result['total_case_excludeabroad']}` คน",
                    จำนวนผู้ป่วยรักษาหายเเล้ววันนี้ = f"`{result['new_recovered']}` คน",
                    จำนวนผู้ป่วยรักษาหายเเล้วสะสม = f"`{result['total_recovered']}` คน",
                    จำนวนผู้เสียชีวิตวันนี้ = f"`{result['new_death']}` คน",
                    จำนวนผู้เสียชีวิตสะสม = f"`{result['total_death']}` คน",
                    อัพเดทเมื่อวันที่ = f'<t:{unix_time}:F>'
                )
                
                
                