import os
import pickle
import discord
from discord.ext import commands


class Reddit(commands.Cog) :
    
    def __init__(self, bot) :
        self._guild = int(os.environ['ID_GUILD_1'])
        self._id_wilhemyn = int(os.environ['ID_WILHEMYN'])
        self.l_towatch = "reddit.com rxddit.com".split()
        if os.path.exists("save/users_reddit.bin") :
            self.d_users = self._charger_data("users_reddit")
        else :
            self.d_users = {self._id_wilhemyn:0}
            self._sauvegarder_data("users_reddit", self.d_users)

    @commands.command(name="reddit", say=True)
    async def reddit(self, ctx) :
        """Afficher la liste des meilleurs redditeurs"""
        if ctx.guild.id != self._guild :
            await ctx.channel.send("Feur.")
            return False
        self.d_users = self._charger_data("users_reddit")
        tosend = ""
        for k, v in sorted(self.d_users.items() , key=lambda x: x[1], reverse=True) :
            tosend += f"<@{k}> {v}\n"
        embed = discord.Embed(
                title = "Les plus gros redditeurs",
                url = "https://reddit.com",
                description = tosend)
        await ctx.channel.send(embed=embed)

    @commands.Cog.listener('on_message') 
    async def chercher_lien_reddit(self, message) :
        if message.guild.id == self._guild :
            if message.author.id == self._id_wilhemyn and "reddit set" in message.content.lower() :
                if int(message.content.lower().split()[2]) in self.d_users :
                    self.d_users = self._charger_data("users_reddit")
                    self.d_users[int(message.content.lower().split()[2])] = int(message.content.lower().split()[3])
                    self._sauvegarder_data("users_reddit", self.d_users)
            for lien in self.l_towatch :
                if lien in message.content.lower() :
                    self.d_users = self._charger_data("users_reddit")
                    if message.author.id not in self.d_users :
                        self.d_users[message.author.id] = 0
                    self.d_users[message.author.id] += 1
                    self._sauvegarder_data("users_reddit", self.d_users)
                    await message.add_reaction("🍅")

    def _sauvegarder_data(self, nom_data, data) :
        with open(f"../roxane_data/{nom_data}.bin", "wb") as f :
            pickle.dump(data, f)

    def _charger_data(self, nom_data) :
        with open(f"../roxane_data/{nom_data}.bin", "rb") as f :
            return pickle.load(f)

async def setup(bot) :
    await bot.add_cog(Reddit(bot))
