import json
import time
from numerize import numerize
import coc
import disnake
import pytz
from disnake.ext import commands
from datetime import datetime, timedelta
clan_tags = ["#2P0JJQGUJ"]
known_streak = []
count = 0
list_size = 0
import asyncio
from CustomClasses.CustomBot import CustomClient
from pymongo import UpdateOne
from PIL import Image, ImageDraw, ImageFont
import io
from io import BytesIO
#import chat_exporter
from ImageGen import WarEndResult as war_gen
from ImageGen import ClanCapitalResult as capital_gen
from utils.ClanCapital import gen_raid_weekend_datestrings, get_raidlog_entry
import aiohttp
from msgspec.json import decode
from msgspec import Struct
from coc.raid import RaidLogEntry
from collections import defaultdict
import operator
from Assets.thPicDictionary import thDictionary
import calendar
war_leagues = json.load(open(f"Assets/war_leagues.json"))
from Assets.emojiDictionary import emojiDictionary
from utils.discord_utils import interaction_handler
from utils.ClanCapital import calc_raid_medals


class OwnerCommands(commands.Cog):

    def __init__(self, bot: CustomClient):
        self.bot = bot
        #self.bot.coc_client.add_events(self.member_attack)
        self.count = 0

    @commands.Cog.listener()
    async def on_connect(self):
        print("connected")
        tags = await self.bot.clan_db.distinct("tag")
        #tags = tags[:500]
        self.bot.coc_client.add_raid_updates(*tags)

    @commands.slash_command(name="owner_anniversary", guild_ids=[923764211845312533])
    @commands.is_owner()
    async def anniversary(self, ctx: disnake.ApplicationCommandInteraction):
        guild = ctx.guild
        await ctx.send(content="Edited 0 members")
        x = 0
        twelve_month = disnake.utils.get(ctx.guild.roles, id=1029249316981833748)
        nine_month = disnake.utils.get(ctx.guild.roles, id=1029249365858062366)
        six_month = disnake.utils.get(ctx.guild.roles, id=1029249360178987018)
        three_month = disnake.utils.get(ctx.guild.roles, id=1029249480261906463)
        for member in guild.members:
            if member.bot:
                continue
            year = member.joined_at.year
            month = member.joined_at.month
            n_year = datetime.now().year
            n_month = datetime.now().month
            num_months = (n_year - year) * 12 + (n_month - month)
            if num_months >= 12:
                if twelve_month not in member.roles:
                    await member.add_roles(*[twelve_month])
                if nine_month in member.roles or six_month in member.roles or three_month in member.roles:
                    await member.remove_roles(*[nine_month, six_month, three_month])
            elif num_months >= 9:
                if nine_month not in member.roles:
                    await member.add_roles(*[nine_month])
                if twelve_month in member.roles or six_month in member.roles or three_month in member.roles:
                    await member.remove_roles(*[twelve_month, six_month, three_month])
            elif num_months >= 6:
                if six_month not in member.roles:
                    await member.add_roles(*[six_month])
                if twelve_month in member.roles or nine_month in member.roles or three_month in member.roles:
                    await member.remove_roles(*[twelve_month, nine_month, three_month])
            elif num_months >= 3:
                if three_month not in member.roles:
                    await member.add_roles(*[three_month])
                if twelve_month in member.roles or nine_month in member.roles or six_month in member.roles:
                    await member.remove_roles(*[twelve_month, nine_month, six_month])
            x += 1
        await ctx.edit_original_message(content="Done")


    @commands.command(name='leave')
    @commands.is_owner()
    async def leaveg(self,ctx, *, guild_name):
        guild = disnake.utils.get(self.bot.guilds, name=guild_name)  # Get the guild by name
        if guild is None:
            await ctx.send("No guild with that name found.")  # No guild found
            return
        await guild.leave()  # Guild found
        await ctx.send(f"I left: {guild.name}!")


    '''@commands.slash_command(name="raid", description="Image showing the current raid map")'''
    '''@coc.ClientEvents.raid_loop_start()
    async def raid_loop(self, iter_spot):
        print(iter_spot)'''

    @coc.RaidEvents.new_offensive_opponent()
    async def new_opponent(self, clan: coc.RaidClan, raid: RaidLogEntry):
        channel = await self.bot.getch_channel(1071566470137511966)
        district_text = ""
        for district in clan.districts:
            name = "District"
            if district.id == 70000000:
                name = "Capital"
            name = f"{name}_Hall{district.hall_level}"
            district_emoji = self.bot.fetch_emoji(name=name)
            district_text += f"{district_emoji}`Level {district.hall_level:<2}` - {district.name}\n"
        detailed_clan = await self.bot.getClan(clan.tag)
        embed = disnake.Embed(title=f"**New Opponent : {clan.name}**",
                             description=f"Raid Clan # {len(raid.attack_log)}\n"
                                         f"Location: {detailed_clan.location.name}\n"
                                         f"Get their own raid details & put some averages here",
                             color=disnake.Color.green())
        embed.add_field(name="Districts", value=district_text)
        embed.set_thumbnail(url=clan.badge.url)
        await channel.send(embed=embed)

    @coc.RaidEvents.raid_attack()
    async def member_attack(self, old_member: coc.RaidMember, member: coc.RaidMember, raid: RaidLogEntry):
        channel = await self.bot.getch_channel(1071566470137511966)
        previous_loot = old_member.capital_resources_looted if old_member is not None else 0
        looted_amount = member.capital_resources_looted - previous_loot
        if looted_amount == 0:
            return
        embed = disnake.Embed(
            description=f"[**{member.name}**]({member.share_link}) raided {self.bot.emoji.capital_gold}{looted_amount} | {self.bot.emoji.thick_sword} Attack #{member.attack_count}/{member.attack_limit + member.bonus_attack_limit}\n"
            , color=disnake.Color.green())
        clan_name = await self.bot.clan_db.find_one({"tag": raid.clan_tag})
        embed.set_author(name=f"{clan_name['name']}")
        off_medal_reward = calc_raid_medals(raid.attack_log)
        embed.set_footer(text=f"{numerize.numerize(raid.total_loot, 2)} Total CG | Calc Medals: {off_medal_reward}")
        await channel.send(embed=embed)


    @coc.RaidEvents.defense_district_destruction_change()
    async def district_destruction(self, previous_district: coc.RaidDistrict, district: coc.RaidDistrict):
        if self.count >= 20:
            return
        self.count += 1
        channel = await self.bot.getch_channel(1071566470137511966)
        #print(district.destruction)
        name = "District"
        if district.id == 70000000:
            name = "Capital"
        name = f"{name}_Hall{district.hall_level}"
        district_emoji = self.bot.fetch_emoji(name=name).partial_emoji
        color = disnake.Color.yellow()
        if district.destruction == 100:
            color = disnake.Color.red()

        if previous_district is None:
            previous_destr = 0
            previous_gold = 0
        else:
            previous_destr = previous_district.destruction
            previous_gold = previous_district.looted

        added = ""
        cg_added = ""
        if district.destruction-previous_destr != 0:
            added = f" (+{district.destruction-previous_destr}%)"
            cg_added = f" (+{district.looted-previous_gold})"

        embed = disnake.Embed(description=f"{self.bot.emoji.thick_sword}{district.destruction}%{added} | {self.bot.emoji.capital_gold}{district.looted}{cg_added} | Atk #{district.attack_count}\n"
                                          , color=color)
        clan_name = await self.bot.clan_db.find_one({"tag" : district.raid_clan.raid_log_entry.clan_tag})
        embed.set_author(icon_url=district_emoji.url, name=f"{district.name} Defense | {clan_name['name']}")
        embed.set_footer(icon_url=district.raid_clan.badge.url,
                         text=f"{district.raid_clan.name} | {district.raid_clan.destroyed_district_count}/{len(district.raid_clan.districts)} Districts Destroyed")
        await channel.send(embed=embed)

    @commands.slash_command(name="see-listeners")
    async def listen(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.send(self.bot.coc_client._listeners["raid"])

    @commands.slash_command(name="raid-map", description="See the live raid map")
    async def raid_map(self, ctx: disnake.ApplicationCommandInteraction, clan: str):
        await ctx.response.defer()
        clan = await self.bot.getClan(clan_tag=clan)
        weekend = gen_raid_weekend_datestrings(number_of_weeks=1)[0]
        weekend_raid_entry = await get_raidlog_entry(clan=clan, weekend=weekend, bot=self.bot, limit=1)
        current_clan = weekend_raid_entry.attack_log[-1]

        background = Image.open("ImageGen/RaidMap.png")
        draw = ImageDraw.Draw(background)

        capital_names = ImageFont.truetype("ImageGen/SCmagic.ttf", 27)
        league_name_font = ImageFont.truetype("ImageGen/SCmagic.ttf", 35)

        paste_spot = {"Capital Peak" : (1025, 225), "Barbarian Camp" : (1360, 500), "Wizard Valley" : (1025, 675),
                      "Balloon Lagoon" : (750, 920), "Builder's Workshop" : (1250, 970)}
        text_spot = {"Wizard Valley" : (1128, 655), "Balloon Lagoon" : (845, 900), "Builder's Workshop" : (1300, 920)}
        for spot, district in enumerate(current_clan.districts):
            name = "District_Hall"
            if district.id == 70000000:
                name = "Capital_Hall"
            if district.id not in [70000000, 70000001]:
                draw.text(text_spot.get(district.name, (100, 100)), district.name, anchor="mm", fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0), font=capital_names)

            name = f"{name}{district.hall_level}"
            district_image = Image.open(f"ImageGen/CapitalDistricts/{name}.png")
            size = 212, 200
            district_image = district_image.resize(size, Image.ANTIALIAS)
            area = paste_spot.get(district.name, (100, 106))
            background.paste(district_image, area, district_image.convert("RGBA"))

        def save_im(background):
            # background.show()
            temp = io.BytesIO()
            #background = background.resize((725, 471))
            # background = background.resize((1036, 673))
            background.save(temp, format="png", compress_level=1)
            temp.seek(0)
            file = disnake.File(fp=temp, filename="filename.png")
            temp.close()
            return file

        loop = asyncio.get_event_loop()
        file = await loop.run_in_executor(None, save_im, background)

        await ctx.send(file=file)





    @commands.slash_command(name="cwl-image", description="Image showing cwl rankings & th comps")
    async def testthis(self, ctx: disnake.ApplicationCommandInteraction, clan: str):
        await ctx.response.defer()
        tag = clan
        try:
            base_clan = await self.bot.getClan(clan_tag=tag)
            cwl: coc.ClanWarLeagueGroup = await self.bot.coc_client.get_league_group(clan_tag=base_clan.tag)
        except:
            return await ctx.send(content="Clan not in cwl")

        background = Image.open("ImageGen/cwlbk.png")
        clan_name = ImageFont.truetype("ImageGen/SCmagic.ttf", 30)
        league_name_font = ImageFont.truetype("ImageGen/SCmagic.ttf", 35)
        numbers = ImageFont.truetype("ImageGen/SCmagic.ttf", 35)
        small_numbers = ImageFont.truetype("ImageGen/SCmagic.ttf", 15)
        stat_numbers = ImageFont.truetype("ImageGen/SCmagic.ttf", 25)
        perc_numbers = ImageFont.truetype("ImageGen/SCmagic.ttf", 20)

        draw = ImageDraw.Draw(background)
        stroke = 4
        star_dict = defaultdict(int)
        dest_dict = defaultdict(int)
        tag_to_obj = defaultdict(str)

        for round in cwl.rounds:
            for war_tag in round:
                war = await self.bot.coc_client.get_league_war(war_tag)
                war: coc.ClanWar
                if str(war.status) == "won":
                    star_dict[war.clan.tag] += 10
                elif str(war.status) == "lost":
                    star_dict[war.opponent.tag] += 10
                tag_to_obj[war.clan.tag] = war.clan
                tag_to_obj[war.opponent.tag] = war.opponent
                star_dict[war.clan.tag] += war.clan.stars
                for attack in war.clan.attacks:
                    dest_dict[war.clan.tag] += attack.destruction
                star_dict[war.opponent.tag] += war.opponent.stars
                for attack in war.opponent.attacks:
                    dest_dict[war.opponent.tag] += attack.destruction

        star_list = []
        for tag, stars in star_dict.items():
            destruction = dest_dict[tag]
            clan_obj = tag_to_obj[tag]
            star_list.append([clan_obj, stars, destruction])

        sorted_clans = sorted(star_list, key=operator.itemgetter(1, 2), reverse=True)

        for count, _ in enumerate(sorted_clans):
            clan = _[0]
            stars = _[1]
            destruction = _[2]
            clan: coc.ClanWarLeagueClan
            async def fetch(url, session):
                async with session.get(url) as response:
                    image_data = BytesIO(await response.read())
                    return image_data

            tasks = []
            async with aiohttp.ClientSession() as session:
                tasks.append(fetch(clan.badge.medium, session))
                responses = await asyncio.gather(*tasks)
                await session.close()

            for image_data in responses:
                badge = Image.open(image_data)
                size = 100, 100
                badge.thumbnail(size, Image.ANTIALIAS)
                background.paste(badge, (200, 645 + (105* count)), badge.convert("RGBA"))
            if clan.tag == base_clan.tag:
                color = (136,193,229)
            else:
                color = (255, 255, 255)
            draw.text((315, 690 + (106 * count)), f"{clan.name[:17]}", anchor="lm", fill=color,stroke_width=stroke, stroke_fill=(0, 0, 0), font=clan_name)
            promo = [x["promo"] for x in war_leagues["items"] if x["name"] == base_clan.war_league.name][0]
            demo = [x["demote"] for x in war_leagues["items"] if x["name"] == base_clan.war_league.name][0]
            extra = 0
            if count + 1 <= promo:
                placement_img = Image.open("ImageGen/league_badges/2168_0.png")
                color = (166,217,112)
            elif count + 1 >= demo:
                placement_img = Image.open("ImageGen/league_badges/2170_0.png")
                color = (232,16,17)
            else:
                placement_img = Image.open("ImageGen/league_badges/2169_0.png")
                extra = 15
                color = (255, 255, 255)

            draw.text((100, 690 + (106 * count)), f"{count + 1}.", anchor="lm", fill=color, stroke_width=stroke, stroke_fill=(0, 0, 0), font=numbers)
            size = 100, 100
            placement_img.thumbnail(size, Image.ANTIALIAS)
            background.paste(placement_img, (30, 663 + (107 * count) + extra), placement_img.convert("RGBA"))

            thcount = defaultdict(int)

            for player in clan.members:
                thcount[player.town_hall] += 1
            spot = 0
            for th_level, th_count in sorted(thcount.items(), reverse=True):
                e_ = ""
                if th_level >= 13:
                    e_ = "-2"
                th_img = Image.open(f"Assets/th_pics/town-hall-{th_level}{e_}.png")
                size = 60, 60
                th_img.thumbnail(size, Image.ANTIALIAS)
                spot += 1
                background.paste(th_img, (635 + (80 * spot), 662 + (106 * count)), th_img.convert("RGBA"))
                draw.text((635 + (80 * spot), 662 + (106 * count)), f"{th_count}", anchor="mm", fill=(255, 255, 255), stroke_width=stroke,stroke_fill=(0, 0, 0), font=small_numbers)
                if spot >= 7:
                    break

            star_img = Image.open(f"ImageGen/league_badges/679_0.png")
            size = 45, 45
            star_img.thumbnail(size, Image.ANTIALIAS)
            #if 2 <=count < 7:

            background.paste(star_img, (1440, 665 + (106 * count)), star_img.convert("RGBA"))
            draw.text((1400, 685 + (107 * count)), f"{stars}", anchor="mm", fill=(255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0), font=stat_numbers)
            draw.text((1647, 685 + (107 * count)), f"{int(destruction)}%", anchor="mm", fill=(255, 255, 255), stroke_width=stroke,stroke_fill=(0, 0, 0), font=perc_numbers)


        league_name = f"War{base_clan.war_league.name.replace('League','').replace(' ','')}.png"
        league_img = Image.open(f"ImageGen/league_badges/{league_name}")
        size = 400, 400
        league_img = league_img.resize(size, Image.ANTIALIAS)
        background.paste(league_img, (785, 80), league_img.convert("RGBA"))

        draw.text((975, 520), f"{base_clan.war_league}", anchor="mm", fill=(255, 255, 255), stroke_width=stroke,stroke_fill=(0, 0, 0), font=league_name_font)
        draw.text((515, 135), f"{len(cwl.rounds)}/{len(cwl.clans) - 1}", anchor="mm", fill=(255, 255, 255), stroke_width=stroke,stroke_fill=(0, 0, 0), font=league_name_font)

        start = coc.utils.get_season_start().replace(tzinfo=pytz.utc).date()
        month = start.month
        if month == 12:
            month = 0
        month = calendar.month_name[month + 1]
        date_font = ImageFont.truetype("ImageGen/SCmagic.ttf", 24)
        draw.text((387, 75), f"{month} {start.year}", anchor="mm", fill=(237,191,33), stroke_width=3, stroke_fill=(0, 0, 0), font=date_font)

        def save_im(background):
            # background.show()
            temp = io.BytesIO()
            #background = background.resize((725, 471))
            # background = background.resize((1036, 673))
            background.save(temp, format="png", compress_level=1)
            temp.seek(0)
            file = disnake.File(fp=temp, filename="filename.png")
            temp.close()
            return file

        loop = asyncio.get_event_loop()
        file = await loop.run_in_executor(None, save_im, background)

        await ctx.send(file=file)

    @testthis.autocomplete("clan")
    @raid_map.autocomplete("clan")
    async def autocomp_clan(self, ctx: disnake.ApplicationCommandInteraction, query: str):
        tracked = self.bot.clan_db.find({"server": ctx.guild.id})
        limit = await self.bot.clan_db.count_documents(filter={"server": ctx.guild.id})
        clan_list = []
        for tClan in await tracked.to_list(length=limit):
            name = tClan.get("name")
            tag = tClan.get("tag")
            if query.lower() in name.lower():
                clan_list.append(f"{name} | {tag}")

        if clan_list == [] and len(query) >= 3:
            if coc.utils.is_valid_tag(query):
                clan = await self.bot.getClan(query)
            else:
                clan = None
            if clan is None:
                results = await self.bot.coc_client.search_clans(name=query, limit=5)
                for clan in results:
                    league = str(clan.war_league).replace("League ", "")
                    clan_list.append(
                        f"{clan.name} | {clan.member_count}/50 | LV{clan.level} | {league} | {clan.tag}")
            else:
                clan_list.append(f"{clan.name} | {clan.tag}")
                return clan_list
        return clan_list[0:25]

    async def testfwlog(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        await ctx.send("starting")
        tags = await self.bot.clan_db.distinct("tag")
        tasks = []

        weekend = gen_raid_weekend_datestrings(2)[1]
        clans: list[coc.Clan] = await self.bot.get_clans(tags=tags)
        clans = [clan for clan in clans if clan is not None]

        async def get_raid(tag):
            clan = coc.utils.get(clans, tag=tag)
            if clan is None:
                return (None, None)
            raid_log_entry = await get_raidlog_entry(clan=clan, weekend=weekend, bot=self.bot, limit=1)
            return (clan, raid_log_entry)

        for tag in tags:
            task = asyncio.ensure_future(get_raid(tag))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

        ti = time.time()
        print("here")
        tasks = []

        async def get_image(raid_entry, clan):
            file = await capital_gen.generate_raid_result_image(raid_entry=raid_entry, clan=clan)
            return file

        for clan, raid_log_entry in responses:
            if clan is not None and raid_log_entry is not None:
                task = asyncio.ensure_future(get_image(raid_entry=raid_log_entry, clan=clan))
                tasks.append(task)

        all_files = await asyncio.gather(*tasks)
        print(time.time() - ti)
        list_chunked = [all_files[i:i + 10] for i in range(0, len(all_files), 10)]
        tasks = []
        for files in list_chunked:
            task = asyncio.ensure_future(ctx.channel.send(files=files))
            tasks.append(task)
        await asyncio.gather(*tasks)







def setup(bot: CustomClient):
    bot.add_cog(OwnerCommands(bot))