import disnake
import coc
from disnake.ext import commands
from CustomClasses.CustomBot import CustomClient
from CustomClasses.CustomServer import CustomServer, ServerClan
from main import check_commands
from typing import Union

class misc(commands.Cog, name="Settings"):

    def __init__(self, bot: CustomClient):
        self.bot = bot

    async def clan_converter(self, clan_tag: str):
        clan = await self.bot.getClan(clan_tag=clan_tag, raise_exceptions=True)
        if clan.member_count == 0:
            raise coc.errors.NotFound
        return clan

    @commands.slash_command(name="set")
    async def set(self, ctx):
        await ctx.response.defer()
        pass

    @set.sub_command(name="banlist-channel", description="Set channel to post banlist in")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def setbanlist(self, ctx: disnake.ApplicationCommandInteraction, channel:disnake.TextChannel):
        """
            Parameters
            ----------
            channel: channel to post & update banlist in when changes are made
        """
        await self.bot.server_db.update_one({"server": ctx.guild.id}, {'$set': {"banlist": channel.id}})
        await ctx.edit_original_message(f"Banlist channel switched to {channel.mention}")

    @set.sub_command(name="greeting", description="Set a custom clan greeting message")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def setgreeting(self, ctx: disnake.ApplicationCommandInteraction, greet):
        """
            Parameters
            ----------
            greet: text for custom new member clan greeting
        """

        await self.bot.server_db.update_one({"server": ctx.guild.id}, {'$set': {"greeting": greet}})

        await ctx.edit_original_message(f"Greeting is now:\n\n"
                        f"{ctx.author.mention}, welcome to {ctx.guild.name}! {greet}",
                         allowed_mentions=disnake.AllowedMentions.none())

    @set.sub_command(name="clan-channel", description="Set a new clan channel for a clan")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def channel(self, ctx: disnake.ApplicationCommandInteraction, clan: str, channel: disnake.TextChannel):
        """
            Parameters
            ----------
            clan: Use clan tag, alias, or select an option from the autocomplete
            channel: New channel to switch to
        """

        clan_search = clan.lower()
        first_clan = clan
        results = await self.bot.clan_db.find_one({"$and": [
            {"alias": clan_search},
            {"server": ctx.guild.id}
        ]})

        if results is not None:
            tag = results.get("tag")
            clan = await self.bot.getClan(tag)
        else:
            clan = await self.bot.getClan(clan)

        if clan is None:
            if "|" in first_clan:
                search = first_clan.split("|")
                tag = search[1]
                clan = await self.bot.getClan(tag)

        if clan is None:
            return await ctx.edit_original_message("Not a valid clan tag or alias.")

        results = await self.bot.clan_db.find_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]})
        if results is None:
            return await ctx.edit_original_message("This clan is not set up on this server. Use `/addclan` to get started.")

        await self.bot.clan_db.update_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]}, {'$set': {"clanChannel": channel.id}})

        await ctx.edit_original_message(f"Clan channel switched to {channel.mention}")

    @set.sub_command(name="member-role", description="Set a new member role for a clan")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def role(self, ctx: disnake.ApplicationCommandInteraction, clan: str, role: disnake.Role):
        """
            Parameters
            ----------
            clan: Use clan tag, alias, or select an option from the autocomplete
            role: New role to switch to
        """

        clan = await self.bot.getClan(clan_tag=clan)

        if clan is None:
            return await ctx.edit_original_message("Not a valid clan tag or alias.")

        results = await self.bot.clan_db.find_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]})
        if results is None:
            return await ctx.edit_original_message("This clan is not set up on this server. Use `/addclan` to get started.")

        await self.bot.clan_db.update_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]}, {'$set': {"generalRole": role.id}})

        embed = disnake.Embed(
            description=f"General role switched to {role.mention}",
            color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="leadership-role", description="Set a new leadership role for a clan")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def leaderrole(self, ctx: disnake.ApplicationCommandInteraction, clan: str, role: disnake.Role):
        """
            Parameters
            ----------
            clan: Use clan tag, alias, or select an option from the autocomplete
            role: New role to switch to
        """

        clan_search = clan.lower()
        first_clan = clan
        results = await self.bot.clan_db.find_one({"$and": [
            {"alias": clan_search},
            {"server": ctx.guild.id}
        ]})

        if results is not None:
            tag = results.get("tag")
            clan = await self.bot.getClan(tag)
        else:
            clan = await self.bot.getClan(clan)

        if clan is None:
            if "|" in first_clan:
                search = first_clan.split("|")
                tag = search[1]
                clan = await self.bot.getClan(tag)

        if clan is None:
            return await ctx.edit_original_message("Not a valid clan tag or alias.")

        results = await self.bot.clan_db.find_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]})
        if results is None:
            return await ctx.edit_original_message("This clan is not set up on this server. Use `/addclan` to get started.")

        await self.bot.clan_db.update_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]}, {'$set': {"leaderRole": role.id}})

        embed = disnake.Embed(
            description=f"Leader role switched to {role.mention}",
            color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="clan-category", description="Set a new category for a clan")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def category(self, ctx: disnake.ApplicationCommandInteraction, clan: str, new_category: str):
        """
            Parameters
            ----------
            clan: Use clan tag, alias, or select an option from the autocomplete
            new_category: new category to use for this clan (type one or choose from autocomplete)
        """

        clan_search = clan.lower()
        first_clan = clan
        results = await self.bot.clan_db.find_one({"$and": [
            {"alias": clan_search},
            {"server": ctx.guild.id}
        ]})

        if results is not None:
            tag = results.get("tag")
            clan = await self.bot.getClan(tag)
        else:
            clan = await self.bot.getClan(clan)

        if clan is None:
            if "|" in first_clan:
                search = first_clan.split("|")
                tag = search[1]
                clan = await self.bot.getClan(tag)

        if clan is None:
            return await ctx.edit_original_message("Not a valid clan tag or alias.")

        results = await self.bot.clan_db.find_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]})
        if results is None:
            return await ctx.edit_original_message("This clan is not set up on this server. Use `/addclan` to get started.")

        await self.bot.clan_db.update_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]}, {'$set': {"category": new_category}})

        embed = disnake.Embed(description=f"Category for {clan.name} changed to {new_category}.",
                              color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="ban-alert-channel", description="Set a new channel for ban alerts")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def ban_alert(self, ctx: disnake.ApplicationCommandInteraction, clan: str, channel: disnake.TextChannel):
        """
                    Parameters
                    ----------
                    clan: Use clan tag, alias, or select an option from the autocomplete
                    channel: New channel to switch to
                """

        clan = await self.bot.getClan(clan_tag=clan)

        if clan is None:
            return await ctx.edit_original_message("Not a valid clan tag or alias.")

        results = await self.bot.clan_db.find_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]})
        if results is None:
            return await ctx.edit_original_message("This clan is not set up on this server. Use `/addclan` to get started.")

        await self.bot.clan_db.update_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]}, {'$set': {"ban_alert_channel": channel.id}})

        await ctx.edit_original_message(f"Ban alert channel for {clan.tag} switched to {channel.mention}")

    @set.sub_command(name="category-role", description="Set a new category role for a server")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def category_role(self, ctx: disnake.ApplicationCommandInteraction, category: str, role: disnake.Role):
        """
            Parameters
            ----------
            category: category to set role for
            role: New role to switch to
        """

        results = await self.bot.clan_db.find_one({"$and": [
            {"category": category},
            {"server": ctx.guild.id}
        ]})

        if results is None:
            return await ctx.edit_original_message(f"No category - **{category}** - on this server")

        await self.bot.server_db.update_one({"server": ctx.guild.id}, {'$set': {f"category_roles.{category}": role.id}})

        embed = disnake.Embed(
            description=f"Category role set to {role.mention}",
            color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="nickname-labels", description="Set new abreviations for a clan or labels for family members (used for auto nicknames)")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def abbreviation(self, ctx: disnake.ApplicationCommandInteraction, type: str, new_label: str):
        """
            Parameters
            ----------
            type: clan or family
            new_label: label that goes after a player's nickname on discord
        """

        if type != "Family":
            clan = await self.bot.getClan(type)
            if clan is None:
                return await ctx.send("Not a valid clan tag or alias.")
            results = await self.bot.clan_db.find_one({"$and": [
                {"tag": clan.tag},
                {"server": ctx.guild.id}
            ]})
            if results is None:
                return await ctx.edit_original_message("This clan is not set up on this server. Use `/addclan` to get started.")
            if len(new_label) >= 16 or len(new_label) < 2:
                return await ctx.edit_original_message("Clan Abbreviation must be 2 to 15 characters (this is to minimize name length's being too long).")

            await self.bot.clan_db.update_one({"$and": [
                {"tag": clan.tag},
                {"server": ctx.guild.id}
            ]}, {'$set': {"abbreviation": new_label.upper()}})
            embed = disnake.Embed(description=f"Abbreviation for {clan.name} changed to {new_label.upper()}.",
                                  color=disnake.Color.green())
        else:
            server = CustomServer(guild=ctx.guild, bot=self.bot)
            await server.set_family_label(new_label)
            embed = disnake.Embed(description=f"Family label changed to {new_label}.",
                                  color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="strike-ban-buttons", description="Add strike ban buttons to a clan's join/leave log for easy management.")
    async def strike_ban_buttons(self, ctx: disnake.ApplicationCommandInteraction, clan: coc.Clan = commands.Param(converter=clan_converter), option = commands.Param(choices=["On", "Off"])):
        """
            Parameters
            ----------
            clan: Choose a clan from  the autocomplete
            option: Turn the buttons on/off
        """

        results = await self.bot.clan_db.find_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]})
        if results is None:
            return await ctx.edit_original_message("This clan is not set up on this server. Use `/addclan` to get started.")

        await self.bot.clan_db.update_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]}, {'$set': {"strike_ban_buttons": (option == "On")}})

        embed = disnake.Embed(
            description=f"Strike Ban Buttons for {clan.name} Join/Leave Log set to {option}",
            color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)



    """@set.sub_command(name="autoeval", description="Turn on/off auto role evaluation for a clan")
    async def set_autoeval(self, ctx: disnake.ApplicationCommandInteraction, clan: coc.Clan = commands.Param(converter=clan_converter), option = commands.Param(choices=["On", "Off"]),
                           role_mode = commands.Param(default=None, choices=["Normal (Add & Remove)", "Only Add Roles", "Only Remove Roles"])):
        if option == "On" and role_mode is None:
            return await ctx.send(content="If turning autoeval on, must select an option in `role_mode`", ephemeral=True)
        results = await self.bot.clan_db.find_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]})
        if results is None:
            return await ctx.send("This clan is not set up on this server. Use `/addclan` to get started.")

        if role_mode == "Only Add Roles":
            role_mode = ["Add"]
        elif role_mode == "Only Remove Roles":
            role_mode = ["Remove"]
        else:
            role_mode = "Normal (Add & Remove)"

        await self.bot.clan_db.update_one({"$and": [
            {"tag": clan.tag},
            {"server": ctx.guild.id}
        ]}, {'$set': {"auto_eval": (option == "On"), "role_mode" : role_mode}})

        embed = disnake.Embed(description=f"AutoEval for {clan.name} turned {option}.",
                              color=disnake.Color.green())
        await ctx.send(embed=embed)"""

    @set.sub_command(name="leadership-eval", description="Have eval assign leadership role to clan coleads & leads (on default)")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def leadership_eval(self, ctx: disnake.ApplicationCommandInteraction, option=commands.Param(choices=["On", "Off"])):
        server = CustomServer(guild=ctx.guild, bot=self.bot)
        await server.change_leadership_eval(option=(option == "On"))
        embed = disnake.Embed(description=f"Leadership Eval turned {option}.",
                              color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="nickname-label-type", description="Have linking change discord name to name | clan or name | family")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def auto_nickname(self, ctx: disnake.ApplicationCommandInteraction, type=commands.Param(choices=["Clan Abbreviations", "Family Name", "Off"])):
        server = CustomServer(guild=ctx.guild, bot=self.bot)
        await server.change_auto_nickname(type)
        embed = disnake.Embed(description=f"Auto Nickname set to {type}.",
                              color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="reddit-recruit-feed", description="Feed of searching for a clan posts on the recruiting subreddit")
    @commands.check_any(commands.has_permissions(manage_guild=True), check_commands())
    async def reddit_recruit(self, ctx: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, role_to_ping: disnake.Role = None, remove=commands.Param(default=None, choices=["Remove Feed"])):
        """
            Parameters
            ----------
            channel: channel to set the feed to
            role_to_ping: role to ping when a new recruit appears
            remove: option to remove this feed
        """
        if remove is None:
            role_id = None if role_to_ping is None else role_to_ping.id
            await self.bot.server_db.update_one({"server": ctx.guild.id}, {"$set": {"reddit_feed": channel.id, "reddit_role": role_id}})

            embed = disnake.Embed(description=f"**Reddit Recruit feed set to {channel.mention}**", color=disnake.Color.green())

        else:
            await self.bot.server_db.update_one({"server": ctx.guild.id}, {"$set": {"reddit_feed": None, "reddit_role": None}})

            embed = disnake.Embed(description="**Reddit Recruit feed removed**", color=disnake.Color.green())

        return await ctx.edit_original_message(embed=embed)

    @set.sub_command(name="category-order", description="Change the order family categories display on /family-clans")
    @commands.has_permissions(manage_guild=True)
    async def family_cat_order(self, ctx: disnake.ApplicationCommandInteraction):
        categories = await self.bot.clan_db.distinct("category", filter={"server": ctx.guild.id})
        select_options = []
        for category in categories:
            select_options.append(disnake.SelectOption(label=category, value=category))
        select = disnake.ui.Select(
            options=select_options,
            placeholder="Categories",  # the placeholder text to show when no options have been chosen
            min_values=len(select_options),  # the minimum number of options a user must select
            max_values=len(select_options),  # the maximum number of options a user can select
        )
        dropdown = [disnake.ui.ActionRow(select)]
        embed= disnake.Embed(description="**Select from the categories below in the order you would like them to be in**", color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed, components=dropdown)
        msg = await ctx.original_message()
        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        try:
            res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                      timeout=600)
        except:
            return await msg.edit(components=[])
        await res.response.defer()
        await self.bot.server_db.update_one({"server" : ctx.guild.id}, {"$set" : {"category_order" : res.values}})
        new_order = ", ".join(res.values)
        embed= disnake.Embed(description=f"New Category Order: `{new_order}`", color=disnake.Color.green())
        await res.edit_original_message(embed=embed)

    @commands.slash_command(name="server-settings", description="Complete list of channels & roles set up on server")
    async def server_info(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        server = CustomServer(guild=ctx.guild, bot=self.bot)
        await server.initialize_server()
        embed = disnake.Embed(title=f"{ctx.guild.name} Server Settings",
                              color=disnake.Color.green())
        embed.add_field(name="Banlist Channel:", value=f"{server.banlist_channel}", inline=True)
        embed.add_field(name="Reddit Feed:", value=f"{server.reddit_feed}", inline=True)
        embed.add_field(name="Leadership Eval:", value=f"{server.leadership_eval}", inline=True)
        embed.add_field(name="Clan Greeting Message:", value=f"{server.clan_greeting}", inline=False)

        if ctx.guild.icon is not None:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        embeds = [embed]
        clans = server.server_clans
        for clan in clans:
            clan: ServerClan
            ll_log = await clan.legend_log
            got_clan = await self.bot.getClan(clan.tag)
            embed = disnake.Embed(title=f"{clan.name}", color=disnake.Color.green())
            embed.set_thumbnail(url=got_clan.badge.url)
            embed.add_field(name="Member Role:", value=f"{clan.member_role}", inline=True)
            embed.add_field(name="Leadership Role:", value=f"{clan.leader_role}", inline=True)
            embed.add_field(name="Clan Channel:", value=f"{clan.clan_channel}", inline=True)
            embed.add_field(name="War Log:", value=f"{clan.war_log}", inline=True)
            embed.add_field(name="Join Log:", value=f"{clan.join_log}", inline=True)
            embed.add_field(name="Clan Capital Log:", value=f"{clan.capital_log}", inline=True)
            embed.add_field(name="Legend Log:", value=f"{ll_log}", inline=True)
            embeds.append(embed)

        chunk_embeds = [embeds[i:i + 10] for i in range(0, len(embeds), 10)]

        for embeds in chunk_embeds:
            if embeds == chunk_embeds[0]:
                await ctx.edit_original_message(embeds=embeds)
            else:
                await ctx.followup.send(embeds=embeds)


    @commands.slash_command(name="whitelist")
    async def whitelist(self, ctx):
        pass

    @whitelist.sub_command(name="add", description="Adds a role that can run a specific command.")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_add(self, ctx, ping: Union[disnake.Member, disnake.Role], command: str):

        list_commands = []
        for command_ in self.bot.slash_commands:
            base_command = command_.name
            children = command_.children
            if children != {}:
                for child in children:
                    command_l = children[child]
                    full_name = f"{base_command} {command_l.name}"
                    command_l = self.bot.get_slash_command(name=full_name)
                    if command_l.checks != []:
                        list_commands.append(full_name)
            else:
                full_name = base_command
                if command_.checks != []:
                    list_commands.append(full_name)

        is_command = command in list_commands

        if "whitelist" in command:
            is_command = False

        if is_command == False:
            return await ctx.reply("Not a valid command or command cannot be whitelisted.")

        results = await self.bot.whitelist.find_one({"$and": [
            {"command": command},
            {"server": ctx.guild.id},
            {"role_user": ping.id}
        ]})

        if results is not None:
            embed = disnake.Embed(description=f"{ping.mention} is already whitelisted for `{command}`.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await self.bot.whitelist.insert_one({
            "command": command,
            "server": ctx.guild.id,
            "role_user": ping.id,
            "is_role" : isinstance(ping, disnake.Role)
        })

        embed = disnake.Embed(
            description=f"{ping.mention} added to `{command}` whitelist.",
            color=disnake.Color.green())
        return await ctx.send(embed=embed)

    @whitelist.sub_command(name="remove", description="Deletes a role/user that can run a specific command")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_remove(self, ctx, ping: Union[disnake.Member, disnake.Role], command: str):

        list_commands = []
        for command_ in self.bot.slash_commands:
            base_command = command_.name
            children = command_.children
            if children != {}:
                for child in children:
                    command_l = children[child]
                    full_name = f"{base_command} {command_l.name}"
                    command_l = self.bot.get_slash_command(name=full_name)
                    if command_l.checks != []:
                        list_commands.append(full_name)
            else:
                full_name = base_command
                if command_.checks != []:
                    list_commands.append(full_name)

        is_command = command in list_commands

        if "whitelist" in command:
            is_command = False

        if is_command == False:
            return await ctx.reply("Not a valid command or command cannot be whitelisted.")

        results = await self.bot.whitelist.find_one({"$and": [
            {"command": command},
            {"server": ctx.guild.id},
            {"role_user": ping.id}
        ]})

        if results is None:
            embed = disnake.Embed(description=f"{ping.mention} has no active whitelist for `{command}`.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await self.bot.whitelist.find_one_and_delete({
            "command": command,
            "server": ctx.guild.id,
            "role_user": ping.id
        })

        embed = disnake.Embed(
            description=f"{ping.mention} removed from `{command}` whitelist.",
            color=disnake.Color.green())
        return await ctx.send(embed=embed)

    @whitelist.sub_command(name="list", description="Displays the list of commands that have whitelist overrides.")
    async def whitelist_list(self, ctx: disnake.ApplicationCommandInteraction):
        text = ""
        results = self.bot.whitelist.find({"server": ctx.guild.id})
        limit = await self.bot.whitelist.count_documents(filter={"server": ctx.guild.id})
        roles = await ctx.guild.fetch_roles()
        for role in await results.to_list(length=limit):
            r = role.get("role_user")
            command = role.get("command")
            if role.get("is_role") :
                r = ctx.guild.get_role(r)
                if r is None:
                    continue
                text += f"{r.mention} | `{command}`\n"
            else:
                text += f"<@{r}> | `{command}`\n"

        if text == "":
            text = "Whitelist is empty."

        embed = disnake.Embed(title=f"Command Whitelist",
                              description=text,
                              color=disnake.Color.green())

        await ctx.send(embed=embed)


    @channel.autocomplete("clan")
    @role.autocomplete("clan")
    @leaderrole.autocomplete("clan")
    @category.autocomplete("clan")
    @ban_alert.autocomplete("clan")
    @strike_ban_buttons.autocomplete("clan")
    async def autocomp_clan(self, ctx: disnake.ApplicationCommandInteraction, query: str):
        tracked = self.bot.clan_db.find({"server": ctx.guild.id})
        limit = await self.bot.clan_db.count_documents(filter={"server": ctx.guild.id})
        clan_list = []
        for tClan in await tracked.to_list(length=limit):
            name = tClan.get("name")
            tag = tClan.get("tag")
            if query.lower() in name.lower():
                clan_list.append(f"{name} | {tag}")
        return clan_list[:25]

    @abbreviation.autocomplete("type")
    async def autocomp_type(self, ctx: disnake.ApplicationCommandInteraction, query: str):
        tracked = self.bot.clan_db.find({"server": ctx.guild.id})
        limit = await self.bot.clan_db.count_documents(filter={"server": ctx.guild.id})
        clan_list = ["Family"]
        for tClan in await tracked.to_list(length=limit):
            name = tClan.get("name")
            tag = tClan.get("tag")
            if query.lower() in name.lower():
                clan_list.append(f"{name} | {tag}")
        return clan_list[:25]

    @category.autocomplete("new_category")
    @category_role.autocomplete("category")
    async def autocomp_category(self, ctx: disnake.ApplicationCommandInteraction, query: str):
        tracked = self.bot.clan_db.find({"server": ctx.guild.id})
        limit = await self.bot.clan_db.count_documents(filter={"server": ctx.guild.id})
        categories = []
        for tClan in await tracked.to_list(length=limit):
            category = tClan.get("category")
            if query.lower() in category.lower() and category not in categories:
                categories.append(category)
        return categories[:25]

    @whitelist_add.autocomplete("command")
    @whitelist_remove.autocomplete("command")
    async def autocomp_comamnds(self, ctx: disnake.ApplicationCommandInteraction, query: str):
        commands = []
        for command_ in self.bot.slash_commands:
            base_command = command_.name
            if "whitelist" in base_command:
                continue
            children = command_.children
            if children != {}:
                for child in children:
                    command = children[child]
                    full_name = f"{base_command} {command.name}"
                    command = self.bot.get_slash_command(name=full_name)
                    if query.lower() in full_name.lower() and command.checks != []:
                        commands.append(full_name)
            else:
                full_name = base_command
                if query.lower() in full_name.lower() and command_.checks != []:
                    commands.append(full_name)
        return commands[:25]


def setup(bot: CustomClient):
    bot.add_cog(misc(bot))