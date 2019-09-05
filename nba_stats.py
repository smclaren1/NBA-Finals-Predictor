import re
import bs4
import csv
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import random
def parse_web(team_name):
    req = Request('https://www.2kratings.com/nba2k19-team/' + team_name, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = soup(webpage, "html.parser")
    table2 = page_soup.findAll("td",{"class": "roster-entry"})
    table = page_soup.findAll("span")
    wanted_players = []
    for name in table2:
        wanted_players.append(name.a.text)  
    return wanted_players
def team_rating(team, rates, num):
    score = 0;
    rated = []
    for name in team:
        #print(name, rates[name])
        rated.append(int(rates[name]))
    rated.sort(reverse = True)
    for i in range(num):
        score += rated[i]
    team_score = score
    #print()
    return team_score

def check_injured(team, overall_teams):
    req = Request('https://www.usatoday.com/sports/nba/injuries/', headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = soup(webpage, "html.parser")
    table = page_soup.findAll("td",{"class": "player_name"})
    table2 = page_soup.findAll("td",{"class": "injury_class"})
    injured = []
    for i in range(len(table)):
        injured.append((table[i].text.strip(), table2[i].text.strip()))
        #print(table[i].text.strip(), table2[i].text.strip())
    for player in injured:

        if player[1][0:4] == "Prob":
            overall_teams[player[0]] -=5
        elif player[1] =="Out indefinitely" or player[1] == "out for season":
            if player[0] in team:
                print(player[0], "is out due to injury")
                team.remove(player[0])

with open('Ratings.csv', 'r') as f:
    reader = csv.reader(f)
    rate_list = list(reader)
ratings = dict()
for rate in rate_list:
    if rate[2] == "ratings":
        continue
    
    ratings[rate[1]] = int(rate[2])
    

print("Who will win?")
#team1 = input("TEAM ONE: ")
team1 = "Houston Rockets"
print(team1)
team1 = team1.replace(' ','-').lower()

#team2 = input("TEAM TWO: ")
team2 = "Utah Jazz"
print(team2)
team2 = team2.replace(' ','-').lower()
'''
info[2] Away Team Name
info[3] Away Team Points
info[4] Home Team Name
info[5] Home Team Points
'''
filename = 'result.txt'
file = open(filename)
header = file.readline()
team = dict()
opp = dict()
stats= dict()
stats["Win"] = 0
stats["Loss"] = 0
stats["total"] = 0
header = header.strip().split(',')
counter = 0
for info in file:
    counter += 1
    info = info.strip().split(',')
    home_team = info[4].replace(" ", "-").lower()
    away_team = info[2].replace(" ", "-").lower()
    joint_word = home_team + '_'+ away_team
    if joint_word not in team.keys():
        team[joint_word] = dict(stats)
    if(int(info[5]) > int(info[3])):
        team[joint_word]["Win"] += 1
    else:
        team[joint_word]["Loss"] += 1

    team[joint_word]["total"] += 1

wanted_players1 = parse_web(team1)
wanted_players2 = parse_web(team2)
check_injured(wanted_players1,ratings)
check_injured(wanted_players2,ratings)
home_games = int(input("How many Home games does team1 have? "))
away_games = 7 - home_games
played_places = []

if home_games == 4:
    i= 0
    while i < home_games:
        played_places.append("Home")
        played_places.append("Away")
        i += 1    
    played_places.pop()
else:
    i= 0
    while i < home_games:
        played_places.append("Away")
        played_places.append("Home")
        i += 1    
    played_places.append("Away")

team1_wins = 0
team2_wins = 0
sim = 0
for game in played_places:  
    if team1_wins == 4:
        print(team1 , "Wins!")
        break
    if team2_wins == 4:
        print(team2 , "Wins!")
        break            
    sim += 1
    if game == "Home" and team[team1+"_"+team2]['total']  >= 2:
        #print("Home", team[team1+"_"+team2])
        winrate = float(team[team1+"_"+team2]['Win']/team[team1+"_"+team2]['total'])
        if winrate >= .65:
            team1_wins += 1
            
        else:
            score1 = team_rating(wanted_players1, ratings) 
            score2 = team_rating(wanted_players2, ratings) 
            if score1 > score2:
                team1_wins += 1
            elif score1 < score2:
                team2_wins += 1
            else:
                team1_wins += 1
            
        
    elif game == "Away" and team[team2+"_"+team1]['total']  >= 2:
        #print("Away", team[team2+"_"+team1])
        winrate = float(team[team2+"_"+team1]['Win']/team[team2+"_"+team1]['total'])
        if winrate >= .65:
            team2_wins += 1
            
        else:
            score1 = team_rating(wanted_players1, ratings,8) 
            score2 = team_rating(wanted_players2, ratings,8) 
            
            if score2 > score1:
                team2_wins += 1
            elif score2 < score1:
                team1_wins += 1
            else:
                team2_wins += 1   
            
    else:
        score1 = team_rating(wanted_players1, ratings,8) 
        score2 = team_rating(wanted_players2, ratings,8)
        if score2 > score1:
            team2_wins += 1
        elif score2 < score1:
            team1_wins += 1
        else:
            score1 = team_rating(wanted_players1, ratings,3) 
            score2 = team_rating(wanted_players2, ratings,3)
            if score2 > score1:
                team2_wins += 1
            elif score2 < score1:
                team1_wins += 1
            else:
                score1 = team_rating(wanted_players1, ratings,3)
                score2 = team_rating(wanted_players2, ratings,3)
                if score2 > score1:
                    team2_wins += 1
                elif score2 < score1:
                    team1_wins += 1
                else:
                    team1_wins +=1
               
    if sim != 0:
        print("Game: "  + str(sim))
        print(team1 + " = " + str(team1_wins))
        print(team2 + " = " + str(team2_wins))      
    if team1_wins == 4:
        print(team1 , "Wins!")
        break
    if team2_wins == 4:
        print(team2 , "Wins!")
        break         
            
