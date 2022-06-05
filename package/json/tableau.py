from pandas import json_normalize
import requests
import pandas as pd

class Tableau:
    def __init__(self):
        req2 = requests.get('http://ddragon.leagueoflegends.com/cdn/12.8.1/data/en_US/champion.json')
        champ_ls = list(req2.json()['data'].keys())
        df1 = json_normalize(req2.json()['data'][champ_ls[0]])
        for i in range(1,len(champ_ls)):
            df2 = json_normalize(req2.json()['data'][champ_ls[i]])
            var = pd.concat([df1, df2])
            df1 = var
        self.champion_json = df1

    def sumid_to_Idchamp(self, tableau, id_joueur):
        for elem in tableau['participants']:
            if elem['summonerId'] == id_joueur:
                return elem['championId']


    def verif_requet(self,server, link, id, key):
        req = requests.get(f'https://{server}{link}{id}?api_key={key}')
        return str(req)

    def get_name_by_key(self, id):
        for i in range(len(self.champion_json)):
            ligne = self.champion_json.iloc[[i]]
            if int(ligne['key']) == id:
                champ = str(ligne['id'])
                pos = champ.find("Name")
                return champ[5:pos-1]

