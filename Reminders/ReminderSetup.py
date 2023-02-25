from main import check_commands
from disnake.ext import commands
from typing import Union
from .ReminderUtils import *
from CustomClasses.CustomBot import CustomClient

class ReminderCreation(commands.Cog, name="Reminders"):

    def __init__(self, bot: CustomClient):
        self.bot = bot

    async def clan_converter(self, clan_tag: str):
        clan = await self.bot.getClan(clan_tag=clan_tag, raise_exceptions=True)
        if clan.member_count == 0:
            raise coc.errors.NotFound
        return clan


    @commands.slash_command(name="reminders")
    async def reminder(self, ctx):
        pass


    @reminder.sub_command(name="queue", description="Reminders in queue to be sent (war only)")
    async def war_reminder_queue(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        all_reminders_tags = await self.bot.clan_db.distinct("tag", filter={"server": ctx.guild.id})
        all_jobs = scheduler.get_jobs()
        job_list = ""
        clans = {}
        for job in all_jobs:
            if job.name in all_reminders_tags:
                time = str(job.id).split("_")
                tag = time[1]
                if tag not in clans:
                    clan = await self.bot.getClan(clan_tag=tag)
                    clans[tag] = clan
                else:
                    clan = clans[tag]
                if clan is None:
                    continue
                run_time = job.next_run_time.timestamp()
                job_list += f"<t:{int(run_time)}:R> - {clan.name}\n"
        embed = disnake.Embed(title=f"{ctx.guild.name} War Reminder Queue", description=job_list)
        await ctx.edit_original_message(embed=embed)


    @reminder.sub_command(name="list", description="Get the list of reminders set up on the server")
    async def reminder_list(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        embed = disnake.Embed(title=f"**{ctx.guild.name} Reminders List**")
        all_reminders_tags = await self.bot.reminders.distinct("clan", filter={"$and": [{"server": ctx.guild.id}]})
        for tag in all_reminders_tags:
            clan = await self.bot.getClan(clan_tag=tag)
            if clan is None:
                continue
            reminder_text = ""
            clan_capital_reminders = self.bot.reminders.find(
                {"$and": [{"clan": tag}, {"type": "Clan Capital"}, {"server": ctx.guild.id}]})
            cc_reminder_text = []
            for reminder in await clan_capital_reminders.to_list(length=100):
                cc_reminder_text.append(f"`{reminder.get('time')}` - <#{reminder.get('channel')}>")
            if cc_reminder_text:
                reminder_text += "**Clan Capital:** \n" + "\n".join(cc_reminder_text) + "\n"

            clan_games_reminders = self.bot.reminders.find(
                {"$and": [{"clan": tag}, {"type": "Clan Games"}, {"server": ctx.guild.id}]})
            cg_reminder_text = []
            for reminder in await clan_games_reminders.to_list(length=100):
                cg_reminder_text.append(f"`{reminder.get('time')}` - <#{reminder.get('channel')}>")
            if cg_reminder_text:
                reminder_text += "**Clan Games:** \n" + "\n".join(cg_reminder_text) + "\n"

            inactivity_reminders = self.bot.reminders.find(
                {"$and": [{"clan": tag}, {"type": "inactivity"}, {"server": ctx.guild.id}]})
            ia_reminder_text = []
            for reminder in await inactivity_reminders.to_list(length=100):
                ia_reminder_text.append(f"`{reminder.get('time')}` - <#{reminder.get('channel')}>")
            if ia_reminder_text:
                reminder_text += "**Inactivity:** \n" + "\n".join(ia_reminder_text) + "\n"

            war_reminders = self.bot.reminders.find({"$and": [{"clan": tag}, {"type": "War"}, {"server": ctx.guild.id}]})
            war_reminder_text = []
            for reminder in await war_reminders.to_list(length=100):
                war_reminder_text.append(f"`{reminder.get('time')}` - <#{reminder.get('channel')}>")
            if war_reminder_text:
                reminder_text += "**War:** \n" + "\n".join(war_reminder_text) + "\n"
            emoji = await self.bot.create_new_badge_emoji(url=clan.badge.url)
            embed.add_field(name=f"{emoji}{clan.name}", value=reminder_text, inline=False)
        await ctx.edit_original_message(embed=embed)


def setup(bot: CustomClient):
    bot.add_cog(ReminderCreation(bot))
