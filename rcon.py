import os
from mcrcon import MCRcon
import discord
from discord.ext import commands

class Rcon(commands.Cog):
    """Permet d'interragir avec le serveur"""

    def __init__(self, bot) :
            self.bot = bot
            self.ip_locale = os.environ['IP_LOCALE']
            self.ip = os.environ['IP']

    @commands.command(name="serv", say=True)
    async def serv(self, ctx) :
        """Donne les infos du serveur à l'instant t"""
        with MCRcon(self.ip_locale, "rcon") as mcr :
            resp = mcr.command("/list")
        n = int(resp.split("here are ")[1].split(" of a max")[0])
        n_max = int(resp.split("of a max of ")[1].split(" players online")[0])
        l_user = resp.split(":")[1].split(", ")
        embed = discord.Embed(title=self.ip, description="\n".join(l_user), color=discord.Color.from_rgb(int(255*(n_max-n)/n_max), int(255*n/n_max), 0))
        embed.set_footer(text=f"{n}/{n_max}")
        await ctx.channel.send(embed=embed)

    @commands.command(name="gif", say=True)
    async def gif(self, ctx) :
        await ctx.channel.send("Tu m'as prise pour Eunuque sale fils de flûte ?")
        # On m'a forcé à mettre cette commande...

async def setup(bot) :
    await bot.add_cog(Rcon(bot))
