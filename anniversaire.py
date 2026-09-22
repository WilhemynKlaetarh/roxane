import os
import pickle
import datetime
import discord
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo

class Anniversaire(commands.Cog) :
    
    def __init__(self, bot) :
        self.bot = bot
        self._id_wilhemyn = int(os.environ['ID_WILHEMYN'])
        if os.path.exists("save/birthdays.bin") :
            self.d_data = self._charger_data("birthdays")
        else :
            self.d_data = {
                int(os.environ['ID_GUILD_1']): {
                    self._id_wilhemyn: datetime.date(int(os.environ['BD_WILHEMYN_Y']), int(os.environ['BD_WILHEMYN_M']), int(os.environ['BD_WILHEMYN_D']))
                    }
                }
            self._sauvegarder_data("birthdays", self.d_data)
        self.d_channel = {
            int(os.environ['ID_GUILD_0']): int(os.environ['ID_CHANNEL_0']),
            int(os.environ['ID_GUILD_1']): int(os.environ['ID_CHANNEL_1'])
        }
        
    async def cog_load(self):
        self.checker_et_souhaiter_les_anniversaires.start()
        #print("task started:", self.checker_et_souhaiter_les_anniversaires.is_running())
        #print("next run:", self.checker_et_souhaiter_les_anniversaires.next_iteration)
    
    def cog_unload(self):
        self.checker_et_souhaiter_les_anniversaires.cancel()
    
    @commands.command(name="anniversaire", say=True)
    async def anniversaire(self, ctx) :
        """Configurer les anniversaires"""
        self.d_data = self._charger_data("birthdays")
        if "help" in ctx.message.content.lower() or "aide" in ctx.message.content.lower() :
            await ctx.channel.send("rox anniversaire ajouter id jour/mois/année\nrox anniversaire modifier id jour/mois/année\nrox anniversaire supprimer id")
        elif ("ajouter" in ctx.message.content or "modifier" in ctx.message.content) and ctx.guild.id in self.d_data :
            """rox anniversaire ajouter id j/m/a"""
            if len(ctx.message.content.split()) == 5 :
                id = int(ctx.message.content.split()[3])
                jour  = int(ctx.message.content.split()[4].split("/")[0])
                mois  = int(ctx.message.content.split()[4].split("/")[1])
                annee = int(ctx.message.content.split()[4].split("/")[2])
                self.d_data[ctx.guild.id][id] = datetime.date(annee, mois, jour)
                self._sauvegarder_data("birthdays", self.d_data)
                await ctx.message.add_reaction("👍")
            else :
                await ctx.message.add_reaction("👎")
        elif "supprimer" in ctx.message.content and ctx.author.id == self._id_wilhemyn and ctx.guild.id in self.d_data :
            """rox anniversaire supprimer id"""
            if len(ctx.message.content.split()) == 4 :
                id = int(ctx.message.content.split()[3])
                self.d_data[ctx.guild.id].pop(id)
                self._sauvegarder_data("birthdays", self.d_data)
                await ctx.message.add_reaction("👍")
            else :
                await ctx.message.add_reaction("👎")
        elif "afficher" in ctx.message.content and ctx.guild.id in self.d_data :
            today = datetime.date.today()
            def next_birthday(bday: datetime.date) -> datetime.date:
                """Retourne la prochaine date d'anniversaire à partir d'aujourd'hui"""
                this_year = bday.replace(year=today.year)
                if this_year < today:
                    return this_year.replace(year=today.year + 1)
                return this_year
            sorted_items = sorted(
                self.d_data[ctx.guild.id].items(),
                key=lambda x: (x[1].month, x[1].day)
            )
            next_user_id, next_date = min(
                self.d_data[ctx.guild.id].items(),
                key=lambda x: next_birthday(x[1])
            )
            tosend = ""
            for user_id, date in sorted_items:
                line = (
                    f"<@{user_id}> "
                    f"{str(date.day).zfill(2)}/{str(date.month).zfill(2)}/{date.year}"
                )
                if user_id == next_user_id:
                    line = f"**{line}**"  # gras Discord
                tosend += line + "\n"
            #for k, v in sorted(self.d_data[ctx.guild.id].items() , key=lambda x: x[1], reverse=True) :
            #    tosend += f"<@{k}> " + str(v.day).zfill(2) + "/" + str(v.month).zfill(2) + f"/{v.year}\n"
            embed = discord.Embed(
                    title = "Liste des anniversaire",
                    description = tosend)
            await ctx.channel.send(embed=embed)
        elif "ajouter_serveur" in ctx.message.content and ctx.author.id == self._id_wilhemyn :
            """rox anniversaire ajouter_serveur id"""
            if len(ctx.message.content.split()) == 4 :
                id = int(ctx.message.content.split()[3])
                self.d_data[id] = {self._id_wilhemyn: datetime.date(int(os.environ['BD_WILHEMYN_Y']), int(os.environ['BD_WILHEMYN_M']), int(os.environ['BD_WILHEMYN_D']))}
                self._sauvegarder_data("birthdays", self.d_data)
                await ctx.message.add_reaction("👍")
            else :
                await ctx.message.add_reaction("👎")
        elif ctx.guild.id not in self.d_data :
            await ctx.message.add_reaction("👎")
        else :
            await ctx.message.add_reaction("👎")
    
    @tasks.loop(time=datetime.time(hour=8, minute=0, tzinfo=ZoneInfo(key='Europe/Paris')))
    async def checker_et_souhaiter_les_anniversaires(self):
        aujourdhui = datetime.date.today()
        self.d_data = self._charger_data("birthdays")
        for guild, d_data_g in self.d_data.items() :
            for k, v in d_data_g.items() :
                if aujourdhui.month == v.month and aujourdhui.day == v.day :
                    if guild in self.d_channel :
                        channel = self.bot.get_channel(self.d_channel[guild])
                        await channel.send(f"Bon anniversaire <@{k}> !")
            
    @checker_et_souhaiter_les_anniversaires.error
    async def checker_error(self, error):
        print("TASK checker_et_souhaiter_les_anniversaires ERROR:", repr(error))
    
    @checker_et_souhaiter_les_anniversaires.before_loop
    async def before_tache(self):
        await self.bot.wait_until_ready()
    
    def _sauvegarder_data(self, nom_data, data) :
        with open(f"../roxane_data/{nom_data}.bin", "wb") as f :
            pickle.dump(data, f)

    def _charger_data(self, nom_data) :
        with open(f"../roxane_data/{nom_data}.bin", "rb") as f :
            return pickle.load(f)

async def setup(bot) :
    await bot.add_cog(Anniversaire(bot))
