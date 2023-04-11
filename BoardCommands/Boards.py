import pytz
from disnake.ext import commands
import disnake
from typing import List, TYPE_CHECKING
import coc
import datetime
from CustomClasses.CustomPlayer import MyCustomPlayer
from collections import defaultdict
import datetime as dt
import pandas as pd
if TYPE_CHECKING:
    from BoardCommands.BoardCog import BoardCog
    cog_class = BoardCog
else:
    cog_class = commands.Cog

class BoardCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def donation_board(self, players: List[MyCustomPlayer], season: str, footer_icon: str, title_name: str, embed_color: disnake.Color = disnake.Color.green()) -> disnake.Embed:
        players.sort(key=lambda x: x.donos(date=season).donated, reverse=True)
        text = "`#   DON   REC    NAME      `\n"
        total_donated = 0
        total_received = 0
        for count, player in enumerate(players, 1):
            if count <= 50:
                text += f"{self.bot.get_number_emoji(color='gold', number=count)}`{player.donos(date=season).donated:5} {player.donos(date=season).received:5} {player.name[:13]:13}`\n"
            total_donated += player.donos(date=season).donated
            total_received += player.donos(date=season).received

        embed = disnake.Embed(title=f"**{title_name} Top {len(players)} Donated**", description=f"{text}", color=embed_color)
        if footer_icon is None:
            footer_icon = self.bot.user.avatar.url
        embed.set_footer(icon_url=footer_icon, text=f"Donations: {'{:,}'.format(total_donated)} | Received : {'{:,}'.format(total_received)} | {season}")
        embed.timestamp = datetime.datetime.now()
        return embed

    async def activity_board(self, players: List[MyCustomPlayer], season: str, footer_icon: str, title_name: str, embed_color: disnake.Color = disnake.Color.green()) -> disnake.Embed:
        players.sort(key=lambda x: len(x.season_last_online(season_date=season)), reverse=True)
        text = "`#  ACT   NAME      `\n"
        total_activities = 0
        for count, player in enumerate(players, 1):
            if count <= 50:
                text += f"{self.bot.get_number_emoji(color='gold', number=count)}`{len(player.season_last_online(season_date=season)):4} {player.name[:15]:15}`\n"
            total_activities += len(player.season_last_online(season_date=season))

        embed = disnake.Embed(title=f"**{title_name} Top {len(players)} Activities**", description=f"{text}",color=embed_color)
        if footer_icon is None:
            footer_icon = self.bot.user.avatar.url
        embed.set_footer(icon_url=footer_icon, text=f"Activities: {'{:,}'.format(total_activities)} | {season}")
        embed.timestamp = datetime.datetime.now()
        return embed

    async def activity_graph(self, players: List[MyCustomPlayer], season: str, title: str, granularity: str, time_zone: str) -> (disnake.File, disnake.ActionRow):
        list_ = []
        days = defaultdict(int)
        for player in players:
            all_lo = player.season_last_online(season_date=season)
            for time in all_lo:
                if granularity == "Day":
                    time = dt.datetime.fromtimestamp(time).replace(hour=0, minute=0, second=0)
                elif granularity == "Hour":
                    time = dt.datetime.fromtimestamp(time).replace(minute=0, second=0)
                elif granularity == "Quarter-Day":
                    time = dt.datetime.fromtimestamp(time)
                    time = time.replace(hour=(time.hour // 6) * 6, minute=0, second=0)
                if player.clan is None:
                    continue
                days[f"{int(time.timestamp())}_{player.clan.name}"] += 1
        for date_time, amount in days.items():
            list_.append([pd.to_datetime(int(date_time.split("_")[0]), unit="s", utc=True).tz_convert(time_zone), amount, date_time.split("_")[1]])
        df = pd.DataFrame(list_, columns=["Date", "Total Activity", "Clan"])
        df.sort_values(by="Date", inplace=True)
        print(df)
        board_cog: BoardCog = self.bot.get_cog("BoardCog")
        return (await board_cog.graph_creator(df=df, x="Date", y="Total Activity", title=title))





