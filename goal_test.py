import requests
import pandas as pd
from sklearn.metrics import mean_squared_error

api_url2 =  "http://0.0.0.0:1337/api/v1/nhl/season/upCominGames"  #"http://0.0.0.0:3083/api/v1/nhl/nhlUpComing"
reposne_games = requests.get(api_url2)
api_rs_json = reposne_games.json()
#df2 = pd.json_normalize(api_rs_json['data']['data'])
df2 = pd.json_normalize(api_rs_json['data'])

print(df2)

for index, row in df2.iterrows():
    print(row['homeTeam'])
    xgs_home = requests.get("http://0.0.0.0:1337/api/v1/nhl/xgs/home/" + row['homeTeam'] ) 
    xgs_away = requests.get("http://0.0.0.0:1337/api/v1/nhl/xgs/away/" + row['awayTeam'] ) 
    xgs_home_json = xgs_home.json()
    xgs_away_json = xgs_away.json()

    print(xgs_home_json)
    print(xgs_away_json)



    print(mean_squared_error(xgs_home_json['xgs'], xgs_home_json['score']))
    print(mean_squared_error(xgs_away_json['xgs'], xgs_away_json['score']))