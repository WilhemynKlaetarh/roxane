import io
import os
import datetime
import requests
import json
import discord
from discord.ext import commands
import matplotlib.pyplot as plt

class Parc(commands.Cog):
    """Permet de récupérer les données du parc"""

    def __init__(self, bot) :
        self.bot = bot
        self.oauth2_token_prod = os.environ['RTE_PROD_TOKEN']
        #self.oauth2_token_indispo = os.environ['RTE_INDISPO_TOKEN']
        self.oauth2_token_indispo = os.environ['RTE_PROD_TOKEN']
        self.nb_reacteur = 57 # À changer en 2024 !!!!!
        self.d_puissance = { # Source : https://pris.iaea.org/PRIS/CountryStatistics/CountryDetails.aspx?current=FR
            "BELLEVILLE 1": 1310,
            "BELLEVILLE 2": 1310,
            "BLAYAIS 1": 910,
            "BLAYAIS 2": 910,
            "BLAYAIS 3": 910,
            "BLAYAIS 4": 910,
            "BUGEY 2": 910,
            "BUGEY 3": 910,
            "BUGEY 4": 880,
            "BUGEY 5": 880,
            "CATTENOM 1": 1300,
            "CATTENOM 2": 1300,
            "CATTENOM 3": 1300,
            "CATTENOM 4": 1300,
            "CHINON 1": 905,
            "CHINON 2": 905,
            "CHINON 3": 905,
            "CHINON 4": 905,
            "CHOOZ 1": 1500,
            "CHOOZ 2": 1500,
            "CIVAUX 1": 1495,
            "CIVAUX 2": 1495,
            "CRUAS 1": 915,
            "CRUAS 2": 915,
            "CRUAS 3": 915,
            "CRUAS 4": 915,
            "DAMPIERRE 1": 890,
            "DAMPIERRE 2": 890,
            "DAMPIERRE 3": 890,
            "DAMPIERRE 4": 890,
            "FLAMANVILLE 1": 1330,
            "FLAMANVILLE 2": 1330,
            "FLAMANVILLE 3": 1630,
            "GOLFECH 1": 1310,
            "GOLFECH 2": 1310,
            "GRAVELINES 1": 910,
            "GRAVELINES 2": 910,
            "GRAVELINES 3": 910,
            "GRAVELINES 4": 910,
            "GRAVELINES 5": 910,
            "GRAVELINES 6": 910,
            "NOGENT 1": 1310,
            "NOGENT 2": 1310,
            "PALUEL 1": 1330,
            "PALUEL 2": 1330,
            "PALUEL 3": 1330,
            "PALUEL 4": 1330,
            "PENLY 1": 1330,
            "PENLY 2": 1330,
            "ST ALBAN 1": 1335,
            "ST ALBAN 2": 1335,
            "ST LAURENT 1": 915,
            "ST LAURENT 2": 915,
            "TRICASTIN 1": 915,
            "TRICASTIN 2": 915,
            "TRICASTIN 3": 915,
            "TRICASTIN 4": 915
        }
        self.d_positions_gps = { # Source : https://www.data.gouv.fr/fr/datasets/centrales-de-production-nucleaire-dedf-sa/
            "BELLEVILLE": [47.508946, 2.875676],
            "BLAYAIS": [45.257605, -0.690606],
            "BUGEY": [45.801148, 5.266072],
            "CATTENOM": [49.415953, 6.218271],
            "CHINON": [47.228727, 0.168307],
            "CHOOZ": [50.090344, 4.789588],
            "CIVAUX": [46.46218, 0.648879],
            "CRUAS": [44.63283, 4.750824],
            "DAMPIERRE": [47.732638, 2.517824],
            "FLAMANVILLE": [49.535986, -1.883342],
            "GOLFECH": [44.105751, 0.84572],
            "GRAVELINES": [51.012846, 2.139287],
            "NOGENT": [48.514581, 3.524182],
            "PALUEL": [49.858754, 0.634759],
            "PENLY": [49.976144, 1.210236],
            "ST ALBAN": [45.405445, 4.755573],
            "ST LAURENT": [47.720248, 1.580217],
            "TRICASTIN": [44.326355, 4.731541]
        }
        self.d_offset = {
            "BELLEVILLE": [80, 0],
            "BLAYAIS": [0, 0],
            "BUGEY": [120, 0],
            "CATTENOM": [0, 0],
            "CHINON": [0, 0],
            "CHOOZ": [0, 0],
            "CIVAUX": [0, 40],
            "CRUAS": [0, 0],
            "DAMPIERRE": [-80, 0],
            "FLAMANVILLE": [0, 0],
            "GOLFECH": [0, 0],
            "GRAVELINES": [80, 0],
            "NOGENT": [0, 0],
            "PALUEL": [0, 80],
            "PENLY": [0, 0],
            "ST ALBAN": [0, 0],
            "ST LAURENT": [0, -80],
            "TRICASTIN": [0, 120]
        }

    def recupererData(self, api_url, oauth2_token) :
        auth_url = "https://digital.iservices.rte-france.com/token/oauth/"

        headers_auth = {
            "Authorization": f"Basic {oauth2_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.get(auth_url, headers=headers_auth)
            print(f"{response.json() = }")
            if response.status_code == 200:
                access_token = response.json()["access_token"]
            else:
                print(f"Erreur de requête: {response.status_code}")
                print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Une erreur s'est produite lors de la requête : {e}")

        headers_api = {
            "Authorization": f"Bearer {access_token}",
            "Host": "digital.iservices.rte-france.com"
        }

        try:
            response = requests.get(api_url, headers=headers_api)
            if response.status_code == 200:
                #print(api_url.split("/")[4], json.loads(response.text))
                #print(response.text)
                data = response.json()
            else:
                print(f"{api_url = }, {response = }")
                print(f"Erreur de requête: {response.status_code}")
                print(response.text)
                data = {"generation_unavailabilities":[{"production_type":"toto"}]}
        except requests.exceptions.RequestException as e:
            print(f"Une erreur s'est produite lors de la requête : {e}")
            data = {"generation_unavailabilities":[{"production_type":"toto"}]}

        return data

    @commands.command(name="parc", say=True)
    async def parc(self, message) :
        """Donne la liste des réacteurs et de leur puissance"""
        aujourdhui = datetime.date.today()
        hier = aujourdhui - datetime.timedelta(days = 1);
        demain = aujourdhui + datetime.timedelta(days = 1);
        start_date = f"{hier.isoformat()}T00:00:00+01:00"
        end_date   = f"{demain.isoformat()}T00:00:00+01:00"
        api_url_prod = f"https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_unit?start_date={start_date}&end_date={end_date}"
        dataProd = self.recupererData(api_url_prod, self.oauth2_token_prod)
        tosend = ""
        for i in range(len(dataProd["actual_generations_per_unit"])) :
            if dataProd["actual_generations_per_unit"][i]["unit"]["production_type"] == "NUCLEAR" :
                tosend += str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]) + " : " + str(dataProd["actual_generations_per_unit"][i]["values"][-1]["value"]) + " MW\n"
        await message.channel.send(tosend)
        
    @commands.command(name="indispo", say=True)
    async def indispo(self, message) :
        """Donne la liste des réacteurs, leur puissance et leur indisponibilité"""
        aujourdhui = datetime.date.today()
        hier = aujourdhui - datetime.timedelta(days = 1);
        demain = aujourdhui + datetime.timedelta(days = 1);
        start_date = f"{hier.isoformat()}T00:00:00+01:00"
        end_date   = f"{demain.isoformat()}T00:00:00+01:00"
        api_url_prod = f"https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_unit?start_date={start_date}&end_date={end_date}"
        api_url_indispo = f"https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v6/generation_unavailabilities?start_date={start_date}&end_date={end_date}&last_version=true"
        dataProd = self.recupererData(api_url_prod, self.oauth2_token_prod)
        dataIndispo = self.recupererData(api_url_indispo, self.oauth2_token_indispo)
        l_tosend = []
        d_reacteurs = {}
        """
        for i in range(len(dataProd["actual_generations_per_unit"])) :
            if dataProd["actual_generations_per_unit"][i]["unit"]["production_type"] == "NUCLEAR" :
                for j in range(len(dataIndispo["generation_unavailabilities"])) :
                    if dataIndispo["generation_unavailabilities"][j]["production_type"] == "NUCLEAR" :
                        ajd = datetime.datetime.fromisoformat(datetime.datetime.fromisoformat(aujourdhui.isoformat()).isoformat()+"+01:00")
                        if datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][j]["start_date"]) < ajd and ajd < datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][j]["end_date"]) and not "FESSENHEIM" in dataIndispo["generation_unavailabilities"][j]["unit"]["name"] and str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]) not in d_reacteurs :
                                d_reacteurs[str(dataProd["actual_generations_per_unit"][i]["unit"]["name"])] = {
                                    "nom":str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]),
                                    "centrale":" ".join(str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]).split()[:-1]),
                                    "puissance":float(dataProd["actual_generations_per_unit"][i]["values"][-1]["value"])}
        """
                            #l_reacteurs.append(str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]))
                            #l_tosend.append(str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]) + " : " + str(dataProd["actual_generations_per_unit"][i]["values"][-1]["value"]) + " MW")
        for i in range(len(dataProd["actual_generations_per_unit"])) :
            if dataProd["actual_generations_per_unit"][i]["unit"]["production_type"] == "NUCLEAR" :
                d_reacteurs[str(dataProd["actual_generations_per_unit"][i]["unit"]["name"])] = {
                                    "nom":str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]),
                                    "centrale":" ".join(str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]).split()[:-1]),
                                    "puissance":float(dataProd["actual_generations_per_unit"][i]["values"][-1]["value"])}
        for i in range(len(dataIndispo["generation_unavailabilities"])) :
            if dataIndispo["generation_unavailabilities"][i]["production_type"] == "NUCLEAR" :
                ajd = datetime.datetime.fromisoformat(datetime.datetime.fromisoformat(aujourdhui.isoformat()).isoformat()+"+01:00")
                if datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["start_date"]) < ajd and ajd < datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["end_date"]) and dataIndispo["generation_unavailabilities"][i]["unit"]["name"] in d_reacteurs and dataIndispo["generation_unavailabilities"][i]["status"] == "ACTIVE" :
                    d_reacteurs[dataIndispo["generation_unavailabilities"][i]["unit"]["name"]]["capacite disponible"] = dataIndispo["generation_unavailabilities"][i]["values"][-1]["available_capacity"]
                    d_reacteurs[dataIndispo["generation_unavailabilities"][i]["unit"]["name"]]["capacite totale"] = dataIndispo["generation_unavailabilities"][i]["unit"]["installed_capacity"]
        for reacteur in d_reacteurs :
            s = f"{d_reacteurs[reacteur]['nom']} : {d_reacteurs[reacteur]['puissance']} MW"
            if "capacite disponible" in d_reacteurs[reacteur] :
                s += f" ({d_reacteurs[reacteur]['capacite disponible']} disponibles sur {d_reacteurs[reacteur]['capacite totale']} installés)"
            l_tosend.append(s)
        await message.channel.send("\n".join(l_tosend))
        """
        tosend = ""
        for i in l_tosend :
            if len(tosend+i+"\n") < 2000 :
                tosend += i + "\n"
            else :
                await message.channel.send(tosend)
                tosend = i + "\n"
        """
    
    @commands.command(name="carte", say=True)
    async def carte(self, ctx, *args) :
        """Affiche la carte des réacteurs en temps réel"""
        
        d_posimage = {"CHOOZ": [2*564, 2*104], "BLAYAIS": [2*246, 2*508]}
        aujourdhui = datetime.date.today()
        hier = aujourdhui - datetime.timedelta(days = 1);
        demain = aujourdhui + datetime.timedelta(days = 1);
        start_date = f"{hier.isoformat()}T00:00:00"#+01:00"
        end_date   = f"{demain.isoformat()}T00:00:00"#+01:00"
        api_url_prod = f"https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_unit?start_date={start_date}+01:00&end_date={end_date}+01:00"
        api_url_indispo = f"https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v6/generation_unavailabilities"
        api_url_indispo += f"?date_type=EVENT_DATE"
        api_url_indispo += f"&start_date={start_date}Z"
        api_url_indispo += f"&end_date={end_date}Z"
        api_url_indispo += f"&last_version=true"
        api_url_indispo += f"&fuel_type=NUCLEAR"
        dataProd = self.recupererData(api_url_prod, self.oauth2_token_prod)
        dataIndispo = self.recupererData(api_url_indispo, self.oauth2_token_indispo)
        l_tosend = []
        d_reacteurs = {i:{'puissance':"-"} for i in self.d_puissance}
        heure_begin, heure_end, nb_allume = "", "", 0
        print(len(dataProd["actual_generations_per_unit"]))
        print(len(dataIndispo["generation_unavailabilities"]))
        for i in range(len(dataProd["actual_generations_per_unit"])) :
            if dataProd["actual_generations_per_unit"][i]["unit"]["production_type"] == "NUCLEAR" :
                d_reacteurs[str(dataProd["actual_generations_per_unit"][i]["unit"]["name"])] = {
                                    "nom":str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]),
                                    "centrale":" ".join(str(dataProd["actual_generations_per_unit"][i]["unit"]["name"]).split()[:-1]),
                                    "puissance":float(dataProd["actual_generations_per_unit"][i]["values"][-1]["value"]),
                                    "puissance precedente":float(dataProd["actual_generations_per_unit"][i]["values"][-2]["value"]),
                                    "fleche":""}
        for i in range(len(dataIndispo["generation_unavailabilities"])) :
            if True : #dataIndispo["generation_unavailabilities"][i]["production_type"] == "NUCLEAR" :
                heure_begin = dataProd["actual_generations_per_unit"][i]["values"][-1]["start_date"].split("T")[1].split(":")[0]
                heure_end = dataProd["actual_generations_per_unit"][i]["values"][-1]["end_date"].split("T")[1].split(":")[0]
                ajd = datetime.datetime.fromisoformat(datetime.datetime.fromisoformat(aujourdhui.isoformat()).isoformat()+"+01:00")
                if datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["start_date"]) < ajd and ajd < datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["end_date"]) and dataIndispo["generation_unavailabilities"][i]["affected_asset_or_unit_name"] in d_reacteurs and dataIndispo["generation_unavailabilities"][i]["event_status"] == "ACTIVE" :
                    d_reacteurs[dataIndispo["generation_unavailabilities"][i]["affected_asset_or_unit_name"]]["capacite disponible"] = dataIndispo["generation_unavailabilities"][i]["values"][-1]["available_capacity"]
                    d_reacteurs[dataIndispo["generation_unavailabilities"][i]["affected_asset_or_unit_name"]]["capacite totale"] = dataIndispo["generation_unavailabilities"][i]["affected_asset_or_unit_installed_capacity"]
        data_stream = io.BytesIO()
        img = plt.imread("../roxane_data/France.png")
        plt.imshow(img)
        plt.axis('off')
        for centrale in self.d_positions_gps :
            l_s = []
            X = self.d_offset[centrale][0] + d_posimage["BLAYAIS"][0] - (self.d_positions_gps["BLAYAIS"][1] - self.d_positions_gps[centrale][1])/(self.d_positions_gps["BLAYAIS"][1] - self.d_positions_gps["CHOOZ"][1]) * (d_posimage["BLAYAIS"][0] - d_posimage["CHOOZ"][0])
            Y = self.d_offset[centrale][1] + d_posimage["BLAYAIS"][1] - (self.d_positions_gps["BLAYAIS"][0] - self.d_positions_gps[centrale][0])/(self.d_positions_gps["BLAYAIS"][0] - self.d_positions_gps["CHOOZ"][0]) * (d_posimage["BLAYAIS"][1] - d_posimage["CHOOZ"][1])
            for reacteur in d_reacteurs :
                if 'puissance precedente' not in d_reacteurs[reacteur] :
                    d_reacteurs[reacteur]['fleche'] = ""
                elif (d_reacteurs[reacteur]['puissance'] - d_reacteurs[reacteur]['puissance precedente'])/self.d_puissance[reacteur] > 0.05 :
                    d_reacteurs[reacteur]['fleche'] = "⬈"
                elif (d_reacteurs[reacteur]['puissance'] - d_reacteurs[reacteur]['puissance precedente'])/self.d_puissance[reacteur] < -0.05 :
                    d_reacteurs[reacteur]['fleche'] = "⬊"
                if centrale in reacteur :
                    l_s.append(centrale)
                    plt.text(X, Y+40*(len(l_s)-1), f"{d_reacteurs[reacteur]['fleche']} {d_reacteurs[reacteur]['puissance']} MW", fontsize = 5, horizontalalignment = 'center', verticalalignment = 'center', alpha = 0.5, color = 'white', backgroundcolor = 'white')
        for centrale in self.d_positions_gps :
            l_s = []
            X = self.d_offset[centrale][0] + d_posimage["BLAYAIS"][0] - (self.d_positions_gps["BLAYAIS"][1] - self.d_positions_gps[centrale][1])/(self.d_positions_gps["BLAYAIS"][1] - self.d_positions_gps["CHOOZ"][1]) * (d_posimage["BLAYAIS"][0] - d_posimage["CHOOZ"][0])
            Y = self.d_offset[centrale][1] + d_posimage["BLAYAIS"][1] - (self.d_positions_gps["BLAYAIS"][0] - self.d_positions_gps[centrale][0])/(self.d_positions_gps["BLAYAIS"][0] - self.d_positions_gps["CHOOZ"][0]) * (d_posimage["BLAYAIS"][1] - d_posimage["CHOOZ"][1])
            for reacteur in d_reacteurs :
                if centrale in reacteur :
                    if "capacite disponible" in d_reacteurs[reacteur] :
                        if d_reacteurs[reacteur]['capacite disponible'] != 0 :
                            color = 'orange'
                            nb_allume += 1
                        else :
                            color = 'red'
                    elif d_reacteurs[reacteur]['puissance'] == "-" :
                        color = 'black'
                    else :
                        color = 'green'
                        nb_allume += 1
                    l_s.append(centrale)
                    plt.text(X, Y+40*(len(l_s)-1), f"{d_reacteurs[reacteur]['fleche']} {d_reacteurs[reacteur]['puissance']} MW", fontsize = 5, horizontalalignment = 'center', verticalalignment = 'center', alpha = 0.5, color = color)#backgroundcolor = 'white', )
            
            
            #plt.text(X, Y, centrale, fontsize = 5, horizontalalignment = 'center', verticalalignment = 'center', alpha = 0.5, backgroundcolor = 'white', color = 'green')
            
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 300)
        plt.close()
        data_stream.seek(0)
        chart = discord.File(data_stream,filename="save/france_nucleaire.png")
        embed = discord.Embed(title=f"Situation du parc le <t:{int(datetime.datetime(aujourdhui.year, aujourdhui.month, aujourdhui.day, int(heure_begin), 0).timestamp())}:D> entre {heure_begin}h et {heure_end}h", url="https://energygraph.info/d/q7IpAJHVz", color=discord.Color.from_rgb(int(255*(self.nb_reacteur-nb_allume)/self.nb_reacteur), int(255*nb_allume/self.nb_reacteur), 0))
        embed.set_image(url="attachment://save/france_nucleaire.png")
        embed.set_footer(text=f"{nb_allume} on / {self.nb_reacteur-nb_allume} off")
        await ctx.channel.send(embed=embed, file=chart)
    
    @commands.command(name="old_carte", say=True)
    async def old_carte(self, ctx, *args) :
        """Affiche la carte ASCII des réacteurs en temps réel"""
        #print(" ")
        #print(ctx.message)
        #print(ctx.command)
        #print(ctx.current_argument)
        #print(args)
        if ctx.current_argument == None :
            aujourdhui = datetime.date.today()
            hier = aujourdhui - datetime.timedelta(days = 1);
            demain = aujourdhui + datetime.timedelta(days = 1);
            start_date = f"{hier.isoformat()}T00:00:00+01:00"
            end_date   = f"{demain.isoformat()}T00:00:00+01:00"
            iTemps = -1
        else :
            start_date = (datetime.datetime.fromisoformat(ctx.current_argument) - datetime.timedelta(days = 2)).isoformat() + "+01:00"
            end_date = (datetime.datetime.fromisoformat(ctx.current_argument) + datetime.timedelta(days = 2)).isoformat() + "+01:00"
            aujourdhui = datetime.datetime.fromisoformat(ctx.current_argument)
            iTemps = 0
            #print(start_date, end_date)
        api_url_prod = f"https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_unit?start_date={start_date}&end_date={end_date}"
        api_url_indispo = f"https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v6/generation_unavailabilities?start_date={start_date}&end_date={end_date}&last_version=true"
        #api_url_indispo = f"https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v6/additional_informations?start_date={start_date_indispo}&end_date={end_date}"
        #api_url_indispo = f"https://digital.iservices.rte-france.com/open_api/unavailability_additional_information/v6/additional_informations?start_date={start_date}&end_date={end_date}&status=INACTIVE&date_type=APPLICATION_DATA&last_version=true"
        dataProd = self.recupererData(api_url_prod, self.oauth2_token_prod)
        dataIndispo = self.recupererData(api_url_indispo, self.oauth2_token_indispo)
        
        d_indispo = {}
        tosendata = ""
        for i in range(len(dataIndispo["generation_unavailabilities"])) :
            if dataIndispo["generation_unavailabilities"][i]["production_type"] == "NUCLEAR" :
                ajd = datetime.datetime.fromisoformat(datetime.datetime.fromisoformat(aujourdhui.isoformat()).isoformat()+"+01:00")
                if datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["start_date"]) < ajd and ajd < datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["end_date"]) and not "FESSENHEIM" in dataIndispo["generation_unavailabilities"][i]["unit"]["name"] :
                    if (name :=dataIndispo["generation_unavailabilities"][i]["unit"]["name"]) not in d_indispo :
                        d_indispo[name] = dataIndispo["generation_unavailabilities"][i]
                    elif datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["updated_date"]) > datetime.datetime.fromisoformat(d_indispo[name]["updated_date"]) :
                        d_indispo[name] = dataIndispo["generation_unavailabilities"][i]
                    #print(dataIndispo["generation_unavailabilities"][i])
                    print(dataIndispo["generation_unavailabilities"][i]["unit"]["name"], dataIndispo["generation_unavailabilities"][i]["type"], dataIndispo["generation_unavailabilities"][i]["status"], dataIndispo["generation_unavailabilities"][i]["values"][-1]["start_date"], dataIndispo["generation_unavailabilities"][i]["values"][-1]["end_date"], dataIndispo["generation_unavailabilities"][i]["updated_date"], dataIndispo["generation_unavailabilities"][i]["values"][-1]["available_capacity"], dataIndispo["generation_unavailabilities"][i]["values"][-1]["unavailable_capacity"], dataIndispo["generation_unavailabilities"][i]["unit"]["installed_capacity"])
                    #tosendata += f"{dataIndispo['generation_unavailabilities'][i]['unit']['name'] = }, {dataIndispo['generation_unavailabilities'][i]['type'] = }, {dataIndispo['generation_unavailabilities'][i]['status'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['start_date'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['end_date'] = }, {dataIndispo['generation_unavailabilities'][i]['updated_date'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['available_capacity'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['unavailable_capacity'] = }, {dataIndispo['generation_unavailabilities'][i]['unit']['installed_capacity'] = }\n"
        #print("Data indispo :")
        #print(dataIndispo)
        
        
        for i in d_indispo :
            print(f"====={i}=====")
            for j in d_indispo[i] :
                print(f"{j} : {d_indispo[i][j]}")
            for k in range(len(dataProd["actual_generations_per_unit"])) :
                if dataProd["actual_generations_per_unit"][k]["unit"]["name"] == i :
                    print(f"{dataProd['actual_generations_per_unit'][k]['values'][-2]['value']} -> {dataProd['actual_generations_per_unit'][k]['values'][-1]['value']}")
                    l_var = [100*(int(dataProd['actual_generations_per_unit'][k]['values'][-5+l]['value'])-int(dataProd['actual_generations_per_unit'][k]['values'][-6+l]['value']))/int(d_indispo[i]['unit']['installed_capacity']) for l in range(5)]
                    print(l_var)
                    #print(f"[{dataProd['actual_generations_per_unit'][k]['values'][-5]['value']-dataProd['actual_generations_per_unit'][k]['values'][-6]['value']}, {dataProd['actual_generations_per_unit'][k]['values'][-4]['value']-dataProd['actual_generations_per_unit'][k]['values'][-5]['value']}, {dataProd['actual_generations_per_unit'][k]['values'][-3]['value']-dataProd['actual_generations_per_unit'][k]['values'][-4]['value']}, {dataProd['actual_generations_per_unit'][k]['values'][-2]['value']-dataProd['actual_generations_per_unit'][k]['values'][-3]['value']}, {dataProd['actual_generations_per_unit'][k]['values'][-1]['value']-dataProd['actual_generations_per_unit'][k]['values'][-2]['value']}]")
            print("\n")
        
        
        
        toprint = {}
        heure_begin, heure_end, nb_allume = "", "", 0
        for i in range(len(dataProd["actual_generations_per_unit"])) :
            if dataProd["actual_generations_per_unit"][i]["unit"]["production_type"] == "NUCLEAR" :
                if dataProd["actual_generations_per_unit"][i]["unit"]["name"] == "BELLEVILLE 1" :
                    if iTemps == 0 :
                        for j in range(len(dataProd["actual_generations_per_unit"][i]["values"])) :
                            #print(dataProd["actual_generations_per_unit"][i]["values"][j]["end_date"].split("+")[0], aujourdhui.isoformat())
                            if dataProd["actual_generations_per_unit"][i]["values"][j]["end_date"].split("+")[0] == aujourdhui.isoformat() :
                                iTemps = j
                    heure_begin = dataProd["actual_generations_per_unit"][i]["values"][iTemps]["start_date"].split("T")[1].split(":")[0]
                    heure_end = dataProd["actual_generations_per_unit"][i]["values"][iTemps]["end_date"].split("T")[1].split(":")[0]
                if dataProd["actual_generations_per_unit"][i]["values"][iTemps]["value"] > 10 :
                    toprint[dataProd["actual_generations_per_unit"][i]["unit"]["name"]] = "🟩"
                    nb_allume += 1
                else :
                    toprint[dataProd["actual_generations_per_unit"][i]["unit"]["name"]] = "🟥"
        tosend = "```\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{toprint['GRAVELINES 1']}{toprint['GRAVELINES 2']}{toprint['GRAVELINES 3']}⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{toprint['GRAVELINES 4']}{toprint['GRAVELINES 5']}{toprint['GRAVELINES 6']}⣿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀{toprint['FLAMANVILLE 1']}⣤⠀⠀⠀⣀{toprint['PENLY 1']}{toprint['PENLY 2']}⣿⣿⣿⣿⣿⣷{toprint['CHOOZ 1']}{toprint['CHOOZ 2']}⡀⠀⠀⠀⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀{toprint['FLAMANVILLE 2']}⣿⣷⣾⣿{toprint['PALUEL 1']}{toprint['PALUEL 2']}{toprint['PALUEL 3']}{toprint['PALUEL 4']}⣿⣿⣿⣿⣿⣿{toprint['CATTENOM 1']}{toprint['CATTENOM 2']}{toprint['CATTENOM 3']}{toprint['CATTENOM 4']}⠀\n"
        tosend += f"⠀⢰⣶⣶⣶⣶⣦⬛️⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{toprint['NOGENT 1']}{toprint['NOGENT 2']}⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀\n"
        tosend += f"⠀⠀⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿{toprint['ST LAURENT 1']}{toprint['ST LAURENT 2']}⣿⣿⣿{toprint['DAMPIERRE 1']}{toprint['DAMPIERRE 2']}{toprint['DAMPIERRE 3']}{toprint['DAMPIERRE 4']}⣿⣿⣿⣿⣿⡿⠋⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠈⢻⣿{toprint['CHINON 1']}{toprint['CHINON 2']}{toprint['CHINON 3']}{toprint['CHINON 4']}⣿⣿⣿⣿⣿⣿{toprint['BELLEVILLE 1']}{toprint['BELLEVILLE 2']}⣿⣿⣿⣟⣁⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿{toprint['CIVAUX 1']}{toprint['CIVAUX 2']}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{toprint['BUGEY 2']}{toprint['BUGEY 3']}{toprint['BUGEY 4']}{toprint['BUGEY 5']}\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{toprint['ST ALBAN 1']}{toprint['ST ALBAN 2']}⣿⣿⣿⣿⡄⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⠀⣿{toprint['BLAYAIS 1']}{toprint['BLAYAIS 2']}{toprint['BLAYAIS 3']}{toprint['BLAYAIS 4']}⣿⣿⣿⣿⣿⣿⣿{toprint['CRUAS 1']}{toprint['CRUAS 2']}{toprint['CRUAS 3']}{toprint['CRUAS 4']}⣿⣷⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿{toprint['GOLFECH 1']}{toprint['GOLFECH 2']}⣿⣿⣿⣿⣿{toprint['TRICASTIN 1']}{toprint['TRICASTIN 2']}{toprint['TRICASTIN 3']}{toprint['TRICASTIN 4']}⣿⣿⠇⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⣿⣿⡿⠁⠀⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        tosend += f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        tosend += "```" 

        embed = discord.Embed(title=f"Situation du parc le {aujourdhui.strftime('%d/%m/%Y')} entre {heure_begin}h et {heure_end}h", url="https://energygraph.info/d/q7IpAJHVz", description=tosend, color=discord.Color.from_rgb(int(255*(self.nb_reacteur-nb_allume)/self.nb_reacteur), int(255*nb_allume/self.nb_reacteur), 0))
        embed.set_footer(text=f"{nb_allume} on / {self.nb_reacteur-nb_allume} off")

        await ctx.channel.send(embed=embed)

        """
        for i in range(len(dataIndispo["generation_unavailabilities"])) :
            if dataIndispo["generation_unavailabilities"][i]["production_type"] == "NUCLEAR" :
                ajd = datetime.datetime.fromisoformat(datetime.datetime.fromisoformat(aujourdhui.isoformat()).isoformat()+"+01:00")
                if datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["start_date"]) < ajd and ajd < datetime.datetime.fromisoformat(dataIndispo["generation_unavailabilities"][i]["end_date"]) and not "FESSENHEIM" in dataIndispo["generation_unavailabilities"][i]["unit"]["name"] :
                    #await ctx.channel.send(f"{dataIndispo['generation_unavailabilities'][i]['unit']['name'] = }, {dataIndispo['generation_unavailabilities'][i]['type'] = }, {dataIndispo['generation_unavailabilities'][i]['status'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['start_date'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['end_date'] = }, {dataIndispo['generation_unavailabilities'][i]['updated_date'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['available_capacity'] = }, {dataIndispo['generation_unavailabilities'][i]['values'][-1]['unavailable_capacity'] = }, {dataIndispo['generation_unavailabilities'][i]['unit']['installed_capacity'] = }")
                    #await ctx.channel.send(f"Name = {dataIndispo['generation_unavailabilities'][i]['unit']['name']}, type = {dataIndispo['generation_unavailabilities'][i]['type']}, status = {dataIndispo['generation_unavailabilities'][i]['status']}, start_date = {dataIndispo['generation_unavailabilities'][i]['values'][-1]['start_date']}, end_date = {dataIndispo['generation_unavailabilities'][i]['values'][-1]['end_date']}, updated_date = {dataIndispo['generation_unavailabilities'][i]['updated_date']}, available_capacity = {dataIndispo['generation_unavailabilities'][i]['values'][-1]['available_capacity']}, unavailable_capacity = {dataIndispo['generation_unavailabilities'][i]['values'][-1]['unavailable_capacity']}, installed_capacity = {dataIndispo['generation_unavailabilities'][i]['unit']['installed_capacity']}")
        """
        
async def setup(bot) :
    await bot.add_cog(Parc(bot))
