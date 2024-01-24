import disnake
import coc

from disnake.ext import commands
from typing import List
from classes.bot import CustomClient
from discord.converters import Convert as convert
from discord.autocomplete import Autocomplete as autocomplete
from datetime import datetime
from commands.board_generation import activity_board

class Activity(commands.Cog, name="Activity"):
    def __init__(self, bot: CustomClient):
        self.bot = bot

    @commands.slash_command(name="activity")
    async def donations(self, ctx: disnake.ApplicationCommandInteraction,
                        user: disnake.Member = None,
                        clan: coc.Clan = commands.Param(default=None, converter=convert.clan, autocomplete=autocomplete.clan),
                        family: disnake.Guild = commands.Param(converter=convert.server, default=None, autocomplete=autocomplete.server),
                        limit: int = commands.Param(default=50, max_value=50),
                        townhalls: List[int] = commands.Param(default=None, convert_defaults=False, converter=convert.townhall),
                        season: str = commands.Param(default=None, converter=convert.season, autocomplete=autocomplete.season),
                        sort_by: str = commands.Param(default="Donations", choices=["Name", "Townhall", "Activity", "Last Online"]),
                        sort_order: str = commands.Param(default="Descending", choices=["Ascending", "Descending"])):
        await ctx.response.defer()
        key_switch = {"Name" : "name", "Townhall" : "townhall", "Activity" : "activity", "Last Online" : "last_online"}
        players = None
        if user is not None:
            players = await self.bot.get_tags(user.id)
        if user == clan == family == None:
            family = ctx.guild
        as_dict = {
            "players" : players,
            "clans" : [clan.tag] if clan else None,
            "server" : family.id if family else None,
            "limit" : limit,
            "sort_field" : key_switch.get(sort_by),
            "townhalls" : townhalls,
            "season" : season,
            "descending" : (sort_order=="Descending")
        }
        server_result = await self.bot.server_db.find_one({"server" : ctx.guild_id})
        result = await self.bot.ck_client.get_activity(as_dict = (as_dict | {"tied_only" : server_result.get("tied", True)}))
        name, icon = await self.bot.parse_to_name_icon(discord_user=user, clan=clan, server=family)
        embed = activity_board(bot=self.bot, result=result, title_name=name, footer_icon=icon, embed_color=disnake.Color(server_result.get("embed_color", 0x2ECC71)))
        t = f"{ctx.user.id}{int(datetime.now().timestamp())}"
        buttons = disnake.ui.ActionRow(disnake.ui.Button(label="", emoji=self.bot.emoji.refresh.partial_emoji,style=disnake.ButtonStyle.grey, custom_id=t))
        await ctx.edit_original_response(embed=embed, components=[buttons])
        as_dict["button_id"] = t
        as_dict["type"] = "activity"
        as_dict["user"] = user.id if user is not None else None
        await self.bot.button_store.insert_one(as_dict)



def setup(bot: CustomClient):
    bot.add_cog(Activity(bot))
