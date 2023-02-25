import disnake
from disnake.ext import commands
from Assets.thPicDictionary import thDictionary
from utils.troop_methods import heros, heroPets
from CustomClasses.CustomBot import CustomClient

class LinkParsing(commands.Cog):

    def __init__(self, bot: CustomClient):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message : disnake.Message):
        if "https://link.clashofclans.com/en?action=OpenPlayerProfile&tag=" in message.content:
            m = message.content.replace("\n", " ")
            spots = m.split(" ")
            s = ""
            for spot in spots:
                if "https://link.clashofclans.com/en?action=OpenPlayerProfile&tag=" in spot:
                    s = spot
                    break
            tag = s.replace("https://link.clashofclans.com/en?action=OpenPlayerProfile&tag=", "")
            if "%23" in tag:
                tag = tag.replace("%23", "")
            player = await self.bot.getPlayer(tag)

            try:
                clan = player.clan.name
                clan = f"{clan}"
            except:
                clan = "None"
            hero = heros(bot=self.bot, player=player)
            pets = heroPets(bot=self.bot, player=player)
            if hero is None:
                hero = ""
            else:
                hero = f"**Heroes:**\n{hero}\n"

            if pets is None:
                pets = ""
            else:
                pets = f"**Pets:**\n{pets}\n"

            embed = disnake.Embed(title=f"**Invite {player.name} to your clan:**",
                                  description=f"{player.name} - TH{player.town_hall}\n" +
                                              f"Tag: {player.tag}\n" +
                                              f"Clan: {clan}\n" +
                                              f"Trophies: {player.trophies}\n"
                                              f"War Stars: {player.war_stars}\n"
                                              f"{hero}{pets}",
                                  color=disnake.Color.green())

            embed.set_thumbnail(url=thDictionary(player.town_hall))

            stat_buttons = [
                disnake.ui.Button(label=f"Open In-Game",
                                  url=player.share_link),
                disnake.ui.Button(label=f"Clash of Stats",
                                  url=f"https://www.clashofstats.com/players/{player.tag.strip('#')}/summary"),
                disnake.ui.Button(label=f"Clash Ninja",
                                  url=f"https://www.clash.ninja/stats-tracker/player/{player.tag.strip('#')}")]
            buttons = disnake.ui.ActionRow()
            for button in stat_buttons:
                buttons.append_item(button)
            await message.channel.send(embed=embed, components=[buttons])


def setup(bot: CustomClient):
    bot.add_cog(LinkParsing(bot))