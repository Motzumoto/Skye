import os
from typing import Optional
import discord

from discord.ext import commands

from discord import app_commands

import datetime

import pkg_resources
import psutil
import inspect


# local imports
from core.bot import SkyeBot
from utils.context import Context
from utils import default, time
from utils import constants


start_time = datetime.datetime.utcnow().timestamp()


class info_view(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Website",
                url="https://skyebot.dev/",
                emoji=constants.WEBSITE,
            )
        )
        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Support Server",
                url="https://discord.gg/Zwn7D78pDw",
                emoji=constants.INVITE,
            )
        )


class bot_info(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    def get_bot_uptime(self, *, brief: bool = False) -> str:
        return time.human_timedelta(
            self.bot.uptime, accuracy=None, brief=brief, suffix=False
        )

    @app_commands.command()
    async def uptime(self, interaction: discord.Interaction):
        """Tells you how long the bot has been up for."""
        await interaction.response.send_message(
            f"I have been running since: **{self.get_bot_uptime()}** ago"
        )

    @app_commands.command()
    async def botinfo(self, itr: discord.Interaction):
        """Provides info about the bot"""

        process = psutil.Process(os.getpid())
        ramUsage = process.memory_full_info().rss / 1024**2

        version = pkg_resources.get_distribution("discord.py").version

        embed = discord.Embed(
            title="Hi! im Skye! I'm a multipurpose open source Discord Bot!",
            description=f"Source Code: {constants.GITHUB} [source](https://github.com/SkyeBot/Skye/tree/rewrite) | "
            f"Invite Link: {constants.INVITE} [invite me](https://discord.com/api/oauth2/authorize?client_id=932462085516968027&permissions=8&scope=bot%20applications.commands) | "
            f"Top.gg Link: {constants.TOP_GG} [top.gg](https://top.gg/bot/932462085516968027) | ",
            color=self.bot.color,
        )

        embed.set_author(
            name="I was made by: Sawsha#0598!",
            icon_url="https://cdn.discordapp.com/avatars/894794517079793704/02fc9ee15032b33756ba9829f00449d9.png?size=1024",
        )

        # statistics
        total_members = 0
        total_unique = len(self.bot.users)

        text = 0
        voice = 0
        total = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable is True:
                continue

            total_members += guild.member_count
            for channel in guild.channels:
                total += 1
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1

            avg = [
                (len([m for m in g.members if not m.bot]) / g.member_count) * 100
                for g in self.bot.guilds
            ]

        embed.add_field(name="Library", value=f"**discord.py {version}**")
        embed.add_field(
            name="Date Created", value=default.date(self.bot.user.created_at, ago=True)
        )
        embed.add_field(
            name="Bot servers",
            value=f"**servers:** {guilds}\n**avg bot/human:** {round(sum(avg) / len(avg), 2)}%\n**Currently serving over {total_members} People!**",
        )

        embed.add_field(
            name="Channels", value=f"{total:,} total\n{text:,} text\n{voice:,} voice"
        )
        embed.add_field(
            name="Cogs loaded",
            value=len([x for x in self.bot.cogs]),
        )
        embed.add_field(name="RAM Usage", value=f"{ramUsage:.2f} MB")

        embed.set_footer(
            text=f"Made with love ❤️ by Sawsha#0598 :))",
        )
        embed.timestamp = discord.utils.utcnow()

        await itr.response.send_message(embed=embed, view=info_view())

    @commands.command()
    async def source(self, ctx: Context, *, command: Optional[str]):
        """Displays my full source code or for a specific command.
        Parameters
        ----------
        command: Optional[str]
            The command to display the source code for.
        """
        source_url = "https://github.com/SkyeBot/Skye"
        branch = "rewrite"
        if command is None:
            return await ctx.send(f"<{source_url}>")

        if command == "help":
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.tree.get_command(command.replace(".", " "))
            if obj is None:
                return await ctx.send("Could not find command.")
            elif obj.module.__class__.__name__ in ("Jishaku"):
                return await ctx.send(
                    "<:jsk:984549118129111060> Jishaku, a debugging and utility extension for discord.py bots:"
                    "\nSee the full source here: <https://github.com/Gorialis/jishaku>"
                )

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        try:
            lines, firstlineno = inspect.getsourcelines(src)
        except Exception as e:
            await ctx.send(
                f"**Could not retrieve source:**\n{e.__class__.__name__}:{e}"
            )
            return
        if not module.startswith("discord"):
            # not a built-in command
            if filename is None:
                return await ctx.send("Could not find source for command.")

            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = "https://github.com/Rapptz/discord.py"
            branch = "master"

        final_url = f"<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)
