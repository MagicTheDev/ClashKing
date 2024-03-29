import disnake
from disnake.ext import commands
from discord import convert, autocomplete, options
from .utils import *


class FamilyCommands(commands.Cog, name="Family Commands"):

    def __init__(self, bot: CustomClient):
        self.bot = bot


    @commands.slash_command(name="family")
    async def family(self, ctx: disnake.ApplicationCommandInteraction):
        result = await self.bot.user_settings.find_one({"discord_user" : ctx.author.id})
        ephemeral = False
        if result is not None:
            ephemeral = result.get("private_mode", False)
        if "board" in ctx.filled_options.keys():
            ephemeral = True
        await ctx.response.defer(ephemeral=ephemeral)


    @family.sub_command(name="compo", description="Composition of values in a family")
    async def compo(self, ctx: disnake.ApplicationCommandInteraction,
                         type_: str = commands.Param(name="type", default="Townhall", choices=["Townhall", "Trophies", "Location", "Role",  "League"]),
                         server: disnake.Guild = options.optional_family):
        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild.id)
        embed = await family_composition(bot=self.bot, server=server, type=type_, embed_color=embed_color)
        buttons = disnake.ui.ActionRow(disnake.ui.Button(label="", emoji=self.bot.emoji.refresh.partial_emoji, style=disnake.ButtonStyle.grey, custom_id=f"familycompo:{server.id}:{type_}"))
        await ctx.edit_original_response(embed=embed, components=[buttons])


    @family.sub_command(name="overview", description="Board showing a family stats overview")
    async def overview(self, ctx: disnake.ApplicationCommandInteraction, server: disnake.Guild = options.optional_family):
        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild.id)
        embed = await family_overview(bot=self.bot, server=server, embed_color=embed_color)
        buttons = disnake.ui.ActionRow(
            disnake.ui.Button(label="", emoji=self.bot.emoji.refresh.partial_emoji, style=disnake.ButtonStyle.grey, custom_id=f"familyoverview:{server.id}"))
        await ctx.edit_original_response(embed=embed, components=[buttons])


    @family.sub_command(name="progress", description="Progress in various areas for the family")
    async def progress(self, ctx: disnake.ApplicationCommandInteraction,
                       type=commands.Param(choices=["Heroes & Pets", "Troops, Spells, & Sieges"]),
                       season: str = options.optional_season,
                       limit: int = commands.Param(default=50, min_value=1, max_value=50),
                       server: disnake.Guild = options.optional_family):

        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild.id)
        if type == "Heroes & Pets":
            custom_id = f"familyheroprogress:{server.id}:{season}:{limit}"
            embeds = await family_hero_progress(bot=self.bot, server=server, season=season, limit=limit, embed_color=embed_color)
        elif type == "Troops, Spells, & Sieges":
            custom_id = f"familytroopprogress:{server.id}:{season}:{limit}"
            embeds = await family_troop_progress(bot=self.bot, server=server, season=season, limit=limit, embed_color=embed_color)

        buttons = disnake.ui.ActionRow(
            disnake.ui.Button(label="", emoji=self.bot.emoji.refresh.partial_emoji, style=disnake.ButtonStyle.grey, custom_id=custom_id),
        )
        await ctx.edit_original_message(embeds=embeds, components=[buttons])


    @family.sub_command(name="summary", description="Summary of stats for a family")
    async def summary(self, ctx: disnake.ApplicationCommandInteraction,
                      season: str = options.optional_season,
                      limit: int = commands.Param(default=5, min_value=1, max_value=15),
                      server: disnake.Guild = options.optional_family
                      ):

        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild.id)
        embeds = await family_summary(bot=self.bot, server=server, limit=limit, season=season, embed_color=embed_color)
        buttons = disnake.ui.ActionRow()
        buttons.add_button(
            label="", emoji=self.bot.emoji.refresh.partial_emoji,
            style=disnake.ButtonStyle.grey,
            custom_id=f"familysummary:{server.id}:{season}:{limit}")
        await ctx.edit_original_message(embeds=embeds, components=[buttons])


    @family.sub_command(name="sorted", description="List of family members, sorted by any attribute")
    async def sorted(self, ctx: disnake.ApplicationCommandInteraction,
                     sort_by: str = commands.Param(choices=sorted(item_to_name.keys())),
                     townhall: int = None,
                     limit: int = commands.Param(default=50, min_value=1, max_value=50),
                     server: disnake.Guild = options.optional_family
                     ):
        """
            Parameters
            ----------
            sort_by: Sort by any attribute
            limit: change amount of results shown
        """
        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild_id)
        embed = await family_sorted(bot=self.bot, server=server, sort_by=sort_by, limit=limit, townhall=townhall, embed_color=embed_color)

        buttons = disnake.ui.ActionRow()
        buttons.append_item(disnake.ui.Button(
            label="", emoji=self.bot.emoji.refresh.partial_emoji,
            style=disnake.ButtonStyle.grey,
            custom_id=f"familysorted:{server.id}:{sort_by}:{limit}:{townhall}"))
        await ctx.edit_original_message(embed=embed, components=[buttons])


    @family.sub_command(name="donations", description="Donation stats for a family")
    async def donations(self, ctx: disnake.ApplicationCommandInteraction,
                        season: str = options.optional_season,
                        townhall: int = None,
                        limit: int = commands.Param(default=50, min_value=1, max_value=50),
                        sort_by: str = commands.Param(default="Donations", choices=["Donations", "Received"]),
                        sort_order: str = commands.Param(default="Descending", choices=["Ascending", "Descending"]),
                        server: disnake.Guild = options.optional_family
                        ):
        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild_id)
        embed = await family_donations(bot=self.bot, server=server, season=season, townhall=townhall, limit=limit, sort_by=sort_by, sort_order=sort_order, embed_color=embed_color)
        buttons = disnake.ui.ActionRow()
        buttons.append_item(disnake.ui.Button(
            label="", emoji=self.bot.emoji.refresh.partial_emoji,
            style=disnake.ButtonStyle.grey,
            custom_id=f"familydonos:{server.id}:{season}:{townhall}:{limit}:{sort_by}:{sort_order}"))
        await ctx.edit_original_message(embed=embed, components=[buttons])

    @family.sub_command(name="games", description="Clan Games stats for a family")
    async def games(self, ctx: disnake.ApplicationCommandInteraction,
                    season: str = options.optional_season,
                    limit: int = commands.Param(default=50, min_value=1, max_value=50),
                    sort_by: str = commands.Param(default="Points", choices=["Points", "Time"]),
                    sort_order: str = commands.Param(default="Descending", choices=["Ascending", "Descending"]),
                    server: disnake.Guild = options.optional_family
                    ):
        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild_id)
        buttons = disnake.ui.ActionRow()
        embed = await family_clan_games(bot=self.bot, server=server, season=season, sort_by=sort_by.lower(), sort_order=sort_order.lower(), limit=limit, embed_color=embed_color)
        buttons.append_item(disnake.ui.Button(
            label="", emoji=self.bot.emoji.refresh.partial_emoji,
            style=disnake.ButtonStyle.grey,
            custom_id=f"familygames:{server.id}:{season}:{sort_by.lower()}:{sort_order.lower()}:{limit}"))
        await ctx.edit_original_message(embed=embed, components=[buttons])


    @family.sub_command(name="activity", description="Activity related stats for a family - last online, activity")
    async def activity(self, ctx: disnake.ApplicationCommandInteraction,
                       season: str = options.optional_season,
                       limit: int = commands.Param(default=50, min_value=1, max_value=50),
                       sort_by: str = commands.Param(default="Activity", choices=["Activity", "Last Online"]),
                       sort_order: str = commands.Param(default="Descending", choices=["Ascending", "Descending"]),
                       server: disnake.Guild = options.optional_family):
        server = server or ctx.guild
        embed_color = await self.bot.ck_client.get_server_embed_color(server_id=ctx.guild_id)
        embed = await family_activity(bot=self.bot, server=server, limit=limit, season=season,
                                    sort_by=sort_by.lower().replace(" ", ""), sort_order=sort_order, embed_color=embed_color)
        buttons = disnake.ui.ActionRow()
        buttons.add_button(
            label="", emoji=self.bot.emoji.refresh.partial_emoji,
            style=disnake.ButtonStyle.grey,
            custom_id=f"familyactivity:{server.id}:{season}:{limit}:{sort_by.lower().replace(' ', '')}:{sort_order}")
        await ctx.edit_original_message(embed=embed, components=[buttons])


def setup(bot):
    bot.add_cog(FamilyCommands(bot))

