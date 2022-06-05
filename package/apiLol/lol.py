from doctest import DocTestSuite
from riotwatcher import LolWatcher, ApiError
import os
from dotenv import load_dotenv
from ..json.tableau import Tableau
from datetime import datetime



def int_comma(number):
    return ("{:,}".format(number))

class League:
    def __init__(self):
        self.lol_watcher = LolWatcher(os.getenv("KEY_API"))
        self.json = Tableau()
    
    def add_region(self, name):
        if name == "br": return "br1"
        if name == "eune": return "eun1"
        if name == "euw": return "euw1"
        if name == "jp": return "jp1"
        if name == "kr": return "kr"
        if name == "na": return "na1"
        if name == "oce": return "oc1"
        if name == "tr": return "tr1"
        if name == "ru": return "ru"
        return None

    def info_compte(self, region, name):
        try:
            return self.lol_watcher.summoner.by_name(self.add_region(region), name)
        except:
            return None

    def info_compte_by_id(self, region, id):
        return self.lol_watcher.summoner.by_id(self.add_region(region), id)

    def info_compte_by_puuid(self, region, puuid):
        return self.lol_watcher.summoner.by_puuid(self.add_region(region), puuid)

    def  info_sum(self,region, sum_id):
        return  self.lol_watcher.league.by_summoner(self.add_region(region), sum_id)

    def  info_sum_by_name(self,region, name):
        sum_id = self.info_compte(region, name)
        if sum_id == None: return None
        try:
            return self.lol_watcher.league.by_summoner(self.add_region(region), sum_id['id'])
        except:
            return None
        
    def info_live_game(self,region, id):
        try:
            return self.lol_watcher.spectator.by_summoner(self.add_region(region), id)
        except:
            return None
            
            

    def champion_du_joueur(self,region, sum_id):
        return self.lol_watcher.champion_mastery.by_summoner(self.add_region(region), sum_id)

    def score_champ_by_joueur(self,region, sum_id, champ_id):
        return self.lol_watcher.champion_mastery.by_summoner_by_champion(self.add_region(region), sum_id, champ_id)


    def match_list_puuid(self,region, puuid):
        return self.lol_watcher.match.matchlist_by_puuid(self.add_region(region), puuid)
    
    def info_match(self,region, match_id):
        return self.lol_watcher.match.by_id(self.add_region(region), match_id)

    def version_ma_region(self,  region):
        try:
            return self.lol_watcher.data_dragon.versions_for_region(self.add_region(region))
        except: return None

    def stat_soloQ(self, region, id):
        stat = []
        info = self.info_sum(region, id)

        for elem in info:
            if elem['queueType'] != 'RANKED_SOLO_5x5':
                pass
            if elem['queueType'] == 'RANKED_SOLO_5x5':
                wr = round((elem['wins']/(elem['losses']+elem['wins']))*100, 1)
                stat.append([elem['summonerName'],elem['tier'], elem['rank'], elem['leaguePoints'], elem['wins'], elem['losses'],wr])
        
        if len(stat) == 0 :
                    pass
        return stat[0]

    
    def stat_flexQ(self, region, pseudo):
        stat = []
        info = self.info_sum_by_name(region , pseudo)
        if len(info) == 0 :
            stat.append([pseudo , '', "Unranked", 0, 0, 0])
        else : 
            for elem in info:
                if elem['queueType'] != 'RANKED_FLEX_SR':
                    pass
                if elem['queueType'] == 'RANKED_FLEX_SR':
                    wr = round((elem['wins']/(elem['losses']+elem['wins']))*100, 1)
                    stat.append([elem['summonerName'],elem['tier'], elem['rank'], elem['leaguePoints'], elem['wins'], elem['losses'],wr])
                if len(stat) == 0 :
                    stat.append([pseudo , '', "Unranked", 0, 0, 0])
        return stat[0]

    def global_lp(self, stat_Q):
        lp = stat_Q[3]
        if stat_Q[1] == "FER": lp+=1000
        if stat_Q[1] == "BRONZE": lp+=2000
        if stat_Q[1] == "SILVER": lp+=3000
        if stat_Q[1] == "GOLD": lp+=4000
        if stat_Q[1] == "PLATINUM": lp+=5000 
        if stat_Q[1] == "DIAMOND": lp+=6000
        if stat_Q[1] == "MASTER" or stat_Q[1] ==  "CHALLENGER": lp+=7000
        
        if stat_Q[2] == "I": lp+=400
        if stat_Q[2] == "II": lp+=300
        if stat_Q[2] == "III": lp+=200
        if stat_Q[2] == "IV": lp+=100

        return lp 

    def champion_most_played(self, region, id_joueur, nb):
        medailles = [':first_place:', ':second_place:', ':third_place:','4','5','6','7','8','9','10']
        lst_champ = self.champion_du_joueur(region, id_joueur)
        envoie = ""
        for i in range(nb):
            nameChampion = str(self.json.get_name_by_key(int(lst_champ[i]['championId'])))
            envoie+= medailles[i] + " M[" + str(lst_champ[i]['championLevel']) + "]. **" + nameChampion + "**: " + int_comma(lst_champ[i]['championPoints']) + " pts\n"
        return envoie

    def type_queue(self, number: int):
        typeGame=''
        if number == 420: typeGame = 'Ranked Solo/Duo'
        if number == 400: typeGame = 'Draft 5v5'
        if number == 430: typeGame = 'Blind Pick 5v5'
        if number == 440: typeGame = 'Ranked Flex'
        if number == 450: typeGame = 'ARAM '
        if number == 700: typeGame = 'Clash'
        return typeGame
        

    def live_game(self, region, id_joueur, pseudo):
        game = self.info_live_game(region, id_joueur)
        if game != None:
            champ_id = self.json.sumid_to_Idchamp(game, id_joueur)
            typeGame = self.type_queue(game['gameQueueConfigId'])

            return f':green_circle:  {pseudo} is currentlt playing a **{typeGame}** game as **{self.json.get_name_by_key(champ_id)}**'
        else:
            return ":red_circle: Not currently playing."

    def last_game(self, region, puuid):
        matchs = self.match_list_puuid(region, puuid)
        last_match = self.info_match(region, matchs[0])
        typeGame = self.type_queue(last_match['info']['queueId'])
        for elem in last_match['info']['participants']:
            if elem['puuid'] == puuid:
                champ, k, d, a, minions, minutes, secondes = elem['championName'],elem['kills'], elem['deaths'], elem['assists'],elem['totalMinionsKilled'] + elem['neutralMinionsKilled'], elem['timePlayed']//60, 0.6 * (elem['timePlayed']%60) 
                if elem['win'] == True:
                    return f':green_circle: **{typeGame}** game as **{champ}** | **{k}/{d}/{a}**, **{minions}Cs**.\n{minutes}min {int(secondes)}s'
                else:
                    return f':red_circle: **{typeGame}** game as **{champ}** | **{k}/{d}/{a}**, **{minions}Cs**. \n{minutes}min {int(secondes)}s'

print('oui')
