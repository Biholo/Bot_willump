from dis import disco
from operator import itemgetter
import os
import discord
from ..database.db import Database
from ..apiLol.lol import League

def set_num(nb):
    tab =  []
    classement =''

    for i in range(1,nb+1):
        tab.append(str(i))
    for i in range(len(tab)):
        classement += tab[i] + '\n'
    return classement

class Commandes(discord.ext.commands.Cog, name="Commandes module"):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.lol = League()
    
    @discord.ext.commands.command(name="register")
    async def register_summ(self, ctx, region,*inv_from_msg):
        inv_from_msg = " ".join(inv_from_msg)
        info = self.lol.info_compte(region, inv_from_msg)
        
        if info == None:
            embed = discord.Embed(title=f':x:  Account {inv_from_msg} does not exist on the server {region.upper()}', description='All commands with !commands', color=0x50b9b3)
        else:
            req_discord = self.db.fetch(f'SELECT * FROM membres WHERE iddiscord = {ctx.author.id}')
            if len(req_discord) != 0:
                ##deja un compte enregistré sur l'acc discord
                compte_existant = self.lol.info_compte_by_id(req_discord[0][4],req_discord[0][2])
                info_version = self.lol.version_ma_region(req_discord[0][4])
                embed = discord.Embed(description=':x:  You already have an account associated with your discord', color=0x50b9b3)
                embed.set_author(name=f"[{req_discord[0][4].upper()}] {compte_existant['name']}", icon_url=f"http://ddragon.leagueoflegends.com/cdn/{info_version['n']['profileicon']}/img/profileicon/{compte_existant['profileIconId']}.png")
            else:
                embed = discord.Embed(description=':white_check_mark:  You have successfully added your account', color=0x50b9b3)
                embed.set_author(name=f"[{region.upper()}] {info['name']}", icon_url=f"http://ddragon.leagueoflegends.com/cdn/{info_version['n']['profileicon']}/img/profileicon/{info['profileIconId']}.png")
        await ctx.send(embed = embed)
                    

    @discord.ext.commands.command(name="swap")
    async def new_register(self, ctx, region, *pseudo):
        pseudo = " ".join(pseudo)
        info = self.lol.info_compte(region, pseudo)
        req = self.db.fetch(f'SELECT * FROM membres WHERE iddiscord = {ctx.author.id}')
        info_version = self.lol.version_ma_region(req[0][4])
        #Si le pseudo lol n'existe pas
        if info['id'] == None:
            embed = discord.Embed(title=f':x:  Account {pseudo} does not exist on the server {region.upper()}', description='All commands with !commands', color=0x50b9b3)

        #Si le pseudo lol existe
        if info['id'] != None:
            if len(req) != 0:
                
                #Si le compte de remplacement est déjà enregistré
                if len(self.db.fetch(f'SELECT * FROM membres WHERE idlol = \'{info["id"]}\' AND iddiscord = {ctx.author.id}')) != 0:
                    embed = discord.Embed(description=f':x: **Account, {pseudo}, is already registered !**', color=0x50b9b3)
                    embed.set_author(name=f"[{region.upper()}] {info['name']}", icon_url=f"http://ddragon.leagueoflegends.com/cdn/{info_version['n']['profileicon']}/img/profileicon/{info['profileIconId']}.png")
                    

                #Si le compte de la demande n'est pas celui enregistré on le remplace
                else:
                    self.db.execute(f'UPDATE membres SET idlol = \'{info["id"]}\', summoner = \'{info["name"]}\', region = \'{region}\' WHERE iduser = {req[0][0]}')
                    embed = discord.Embed(description=f':white_check_mark: **Your account, {pseudo}, is successfully registered**', color=0x50b9b3)
                    embed.set_author(name=f"[{region.upper()}] {info['name']}", icon_url=f"http://ddragon.leagueoflegends.com/cdn/{info_version['n']['profileicon']}/img/profileicon/{info['profileIconId']}.png")
                    
                

            #Si aucun compte lol est enregistré
            else:
                embed = discord.Embed(title=f':x:  You have not yet registered an account', description='!register [pseudoLol] to register', color=0x50b9b3)

        await ctx.send(embed = embed)

    @discord.ext.commands.command(name="commands")
    async def help(self, ctx):
        embed = discord.Embed(title=f'LolRank commands :gear: :', description='All commands available are:', color=0x50b9b3)
        embed.add_field(name="!lol register [summonerName]", value=f':point_right: Adds your lol summoner yo your account.' , inline=False)
        embed.add_field(name="!lol swap [summonerName]", value=f':point_right: Remove and add your new lol summoner.' , inline=False)
        embed.add_field(name="!lol me", value=f':point_right: Summoner profile with ranks, champions, etc.', inline=False)
        embed.add_field(name="!lol profil [server] [summonerName]", value=f':point_right: Summoner profile with ranks, champions, etc.', inline=False)
        embed.add_field(name="!lol classement", value=f':point_right: Show the classement of register member in the server.', inline=False)

        await ctx.send(embed = embed)
        


    @discord.ext.commands.command(name="me")
    async def info_joueur_me(self, ctx):
        id = self.db.fetch(f'SELECT idlol, region FROM membres WHERE iddiscord = \'{ctx.author.id}\'')
        info = self.lol.info_compte_by_id(id[0][1], id[0][0])
        info_version = self.lol.version_ma_region(id[0][1])
        version_icon = info_version['n']['profileicon']
        pseudo = info['name']
        icon = info['profileIconId']
        soloQ = self.lol.stat_soloQ(id[0][1], id[0][0])
        embed = discord.Embed(title=f':cold_face: Profile: {pseudo}', description= f'This is the profile of {pseudo}', color=0x50b9b3)
        embed.set_thumbnail(url = f'http://ddragon.leagueoflegends.com/cdn/{version_icon}/img/profileicon/{icon}.png')
        embed.add_field(name="Level", value=info['summonerLevel'], inline= False)
        embed.add_field(name="Champion most played", value=self.lol.champion_most_played(id[0][1], id[0][0], 3), inline= True)
        embed.add_field(name="Ranked Stats:", value=f'**{soloQ[1]} {soloQ[2]}\n {soloQ[3]}Lp** / {soloQ[4]}W {soloQ[5]}L\nWinrate: {soloQ[6]}%', inline= True)
        embed.add_field(name="Last Game:", value= self.lol.last_game(id[0][1], info['puuid']), inline=False)
        embed.add_field(name="Live Game:", value= self.lol.live_game(id[0][1], id[0][0], pseudo), inline=False)
        await ctx.send(embed = embed)

    @discord.ext.commands.command(name="profil")
    async def info_joueur(self, ctx, region, *summonerName):
        summonerName = " ".join(summonerName)
        info = self.lol.info_compte(region, summonerName)
        info_version = self.lol.version_ma_region(region)
        if info == None or info_version ==None :
            embed = discord.Embed(title = f'**:x:  Account {summonerName} does not exist on the server [{region.upper()}]**', description = f'Verify the summoner name and server enter', color=0x50b9b3)
        else:
            icon = info['profileIconId']
            soloQ = self.lol.stat_soloQ(region, info['id'])
            embed = discord.Embed(title=f':cold_face: Profile: {summonerName}', description= f'This is the profile of {summonerName}', color=0x50b9b3)
            embed.set_thumbnail(url = f'http://ddragon.leagueoflegends.com/cdn/{info_version["n"]["profileicon"]}/img/profileicon/{icon}.png')
            embed.add_field(name="Level", value=info['summonerLevel'], inline= False)
            embed.add_field(name="Champion most played", value=self.lol.champion_most_played(region, info['id'], 3), inline= True)
            embed.add_field(name="Ranked Stats:", value=f'**{soloQ[1]} {soloQ[2]}\n {soloQ[3]}Lp** / {soloQ[4]}W {soloQ[5]}L\nWinrate: {soloQ[6]}%', inline= True)
            embed.add_field(name="Last Game:", value= self.lol.last_game(region, info['puuid']), inline=False)
            embed.add_field(name="Live Game:", value= self.lol.live_game(region, info['id'], summonerName), inline=False)
        await ctx.send(embed = embed)

    @discord.ext.commands.command(name="classement")
    async def classement(self, ctx):
        info, acc =  [], 0
        pseudo, rank = '', ''
        guild = self.bot.get_guild(ctx.message.guild.id)
        async for member in guild.fetch_members(limit=150):
   
            joueur_db =  self.db.fetch(f'SELECT * FROM membres WHERE iddiscord = \'{member.id}\'')
            if(len(joueur_db) != 0):
                acc+=1
                stat_Q = self.lol.stat_soloQ(joueur_db[0][4], joueur_db[0][2])
                info.append([member.display_name   + '\n', stat_Q[2] + " " + stat_Q[1] + " " + str(stat_Q[3]) + '\n', self.lol.global_lp(stat_Q)])
        for i in range(len(info)-1):
            for j in range(i + 1, len(info)):
                if info[i][2] <= info[j][2]:
                    info[i] , info[j] = info[j], info[i]
        
        for tab in info:
            pseudo += tab[0]
            rank += tab[1]
        embed = discord.Embed(title=f'**Ladder of {ctx.message.guild.name} server :**', color=0x50b9b3)
        embed.set_thumbnail(url = ctx.message.guild.icon_url)

        embed.add_field(name="Num", value=set_num(acc), inline= True)
        embed.add_field(name="Pseudo", value=pseudo, inline= True)
        embed.add_field(name="Rank", value=rank, inline= True)
        await ctx.send(embed = embed)
        
    @discord.ext.commands.command(name="invite")
    async def invite_bot(self, ctx):
        embed = discord.Embed(title=f':e_mail:  Bot Willump invite', description='There\'s the link to invite the bot to your own server!', color=0x50b9b3)
        #embed.add_field(name="**Please make sure you are logged in on your Discord account in your browser.**", value=' ', inline= False)
        embed.add_field(name="**Invite**", value='[**Click here!**](https://discord.com/api/oauth2/authorize?client_id=972468249218416711&permissions=8&scope=bot)', inline= True)
        embed.add_field(name="**Commands**", value='**http://127.0.0.1:5500/lolRank/site/index.html#commands** or `!commands`', inline= True)
        await ctx.send(embed = embed)

    @discord.ext.commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title=f'Bot Willump', color=0x50b9b3)
        embed.add_field(name="**Invite:**", value='If you want the bot on your server! You can get it [**here**](https://discord.com/api/oauth2/authorize?client_id=972468249218416711&permissions=8&scope=bot)!', inline=False)
        embed.add_field(name="**Commands:**", value="You can check **all available commands**, on the site http://127.0.0.1:5500/lolRank/site/index.html#commands\n or `!lol commands`", inline=False)
        embed.add_field(name="**Question:**", value="If you want to contact the developer in reason a submit bug or a suggestion you can contact me, on [**twitter**](https://twitter.com/Biholomorphisme).")
        await ctx.send(embed = embed)

class Table:
    def __init__(self):
        self.db = Database()
        self.lol = League()
    
    def inserer(self, name, discord):
        info = self.lol.info_compte(name)
        id_lol = info['id']

        if id_lol != None:
            if len(self.db.fetch(f'SELECT * FROM membres WHERE idlol = \'{id_lol}\'')) == 0:
                self.db.execute(f'INSERT INTO membres (iddiscord, idlol, summoner) VALUES ({discord}, \'{id_lol}\', \'{name}\')')
            else:
                print("deja enregistré")

        if id_lol == None:
            print("pas bon")

