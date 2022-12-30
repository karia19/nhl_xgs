import numpy as np
import pandas as pd
import json
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import statsmodels.formula.api as smf
import warnings
warnings.simplefilter("ignore", UserWarning)
import joblib
from sklearn.ensemble import RandomForestClassifier
from flask import Flask, send_file, make_response, render_template
from flask import request
from flask_cors import CORS


model_variables = ['distance', 'angle', 'lastEventNum', 'last_distance', 'shotNum', 'lastShot', 'timeDifferance' ]
model_variables2 = ['distance', 'angle', 'lastEventNum', 'last_distance', 'shotNum', 'lastShot','timeDifferance' ]

#model_variables = ['distance', 'angle','last_distance', 'lastShot' ,'timeDifferance' ]
#model_variables2 = ['distance', 'angle','last_distance', 'lastShot','timeDifferance' ]


hockey_gaol_wide = 1.80

def goal_angle(data):
    b = np.array([89, 0])
    for i, row in data.iterrows():
        try:
            """SHOT ANGLE """
            x=84-data.at[i,'eventCordX']    #*105/200
            y= data.at[i,'eventCordY'] 

            a = np.arctan(1.80 *x /(x**2 + y**2 - (1.80/2)**2))
            if a<0:
                a=np.pi+a
            data.at[i, "angle"] = a
        except:
            data.at[i, "angle"] = 100
            print("err in angle")

        try:
            """DISTANCE FROM GOAL"""
            a = np.array([abs(int(row['eventCordX'])), abs(int(row['eventCordY']))])
            #print(a)
            dist = np.sqrt(np.sum(np.square(a-b)))
            data.at[i, "distance"] = dist * 0.3048
        except:
            data.at[i, "distance"] = 100
            print("err in distnace")

        """DISTANCE FROM GOAL LAST EVENT"""
        try:
            a = np.array([abs(int(row['lastEventCordX'])), abs(int(row['lastEventCordY']))])
            #print(a)
            dist = np.sqrt(np.sum(np.square(a-b)))
            data.at[i, "last_distance"] = dist * 0.3048
        
        except:
            data.at[i, "last_distance"] = 0.00

        """LAST EVENT TEAM"""
        try: 
            if row['eventTeam'] == row['lastEventTeam']:
                data.at[i, 'lastTeamNum'] = 1
            else:
                data.at[i, 'lastTeamNum'] = 0
        
        except:
            data.at[i, 'lastTeamNum'] = 0



        """LAST EVENT STATS"""
        try:
            if row['lastEventType'] == "Shot":
                data.at[i, 'lastShot'] = 1
            elif row['lastEventType'] == "Missed Shot":
                data.at[i, 'lastShot'] = 0.8
            elif row['lastEventType'] == "Blocked Shot":
                data.at[i, 'lastShot'] = 0.7   
            elif row['lastEventType'] == "Takeaway":
                data.at[i, 'lastShot'] = 0.6   
            elif row['lastEventType'] == "Faceoff":
                data.at[i, 'lastShot'] = 0.5         
            else:
                data.at[i, 'lastShot'] = 0.0

        except:
                data.at[i, 'lastShot'] = 0.0


        """PENALTY ON"""
        if row['powerPlay'] == "Even":
            data.at[i, 'even'] = 1
        elif row['powerPlay'] == "Power Play":
            data.at[i, 'even'] = 2
        else:
            data.at[i, "even"] = 0     
        
    return data

def make_data_same_len(data):
    goan_len = data[data['eventNum'] == 1]
    no_goal = data[data['eventNum'] != 1]
    #print(no_goal, goan_len)
    goals = goan_len[0:len(goan_len)]
    no_goals = no_goal[0:len(goan_len) + 30000]

    data = pd.concat([goals, no_goals], ignore_index=True)

    return data

def gradient_xg(data):
    mod_data =  data.dropna()
    #print(mod_data)
    #mod_data =  make_data_same_len(data)
    #goals = (mod_data[mod_data['eventNum'] == 1])
    #goals_stats = (abs(goals['timeDifference']).describe())
    #print(goals_stats.mean)

    X = mod_data[model_variables].astype(float)
    y = mod_data['eventNum']
    X_train,X_test,y_train,y_test = train_test_split(X, y, test_size = 0.20 ,random_state = 0 )
    clf = GradientBoostingClassifier().fit(X_train, y_train)
    print("score", clf.score(X_test, y_test))
    joblib.dump(clf, 'gradient_xg.pk')

    clf2 = RandomForestClassifier(max_depth=2).fit(X_train, y_train)
    print("score", clf2.score(X_test, y_test))

    
    model = ''
    for v in model_variables2[: -1]:
       model = model + v + '+'
    model = model + model_variables2[-1]  
    print(model)
    #Fit the model
    test_model = smf.glm(formula="eventNum ~ " + model, data=mod_data, 
                           family=sm.families.Binomial()).fit()
   
    print(test_model.summary())  
    b=test_model.params
    joblib.dump(b, "xG.pkl")   

def make_xg_pred(data_to_pred):
    clf = joblib.load('gradient_xg.pk')
    b = joblib.load('./xG.pkl')

    teams = []
    name = list(data_to_pred['eventTeam'])
    teams.append(name[0])
    
    for i in range(len(data_to_pred)):
        if name[i] != name[0]:
            teams.append(name[i])
            break
    
    print(teams)
    for index, row in data_to_pred.iterrows():
        xg_data = row[model_variables].astype(float)
        #pred = clf.predict([xg_data])
        pred_proba = clf.predict_proba([xg_data])
        
        data_to_pred.at[index, "xgs"] = pred_proba[0][1]

    def calculate_xG(sh):    
        bsum=b[0]
        for i,v in enumerate(model_variables2):
           bsum=bsum+b[i+1]*sh[v]
        xG = 1/(1+np.exp(bsum)) 
        return 1.0 - xG   

    #Add an xG to my dataframe
    xG=data_to_pred.apply(calculate_xG, axis=1) 
    data_to_pred = data_to_pred.assign(xG=xG) 

    team_one = data_to_pred[data_to_pred['eventTeam'] == teams[0]]
    team_two = data_to_pred[data_to_pred['eventTeam'] == teams[1]]

    #print(data_to_pred)

    """
    print(teams[0])
    print(np.sum(list(team_one['xgs'])))
    #print(np.sum(list(team_one['xG'])))


    print(teams[1])
    print(np.sum(list(team_two['xgs'])))
    #print(np.sum(list(team_two['xG'])))
    """
    #print(data_to_pred[data_to_pred['eventNum'] == 1])

    #return data_to_pred
    try:
        high_scores = ((team_one[(team_one['xgs'] > 0.20)  & (team_one['eventNum'] != 1.0)]))
        high_scores2 = ((team_two[(team_two['xgs'] > 0.20)  & (team_two['eventNum'] != 1.0)]))

        goals1 = team_one[team_one['eventNum'] == 1.0 ]
        goals2 = team_two[team_two['eventNum'] == 1.0 ]

        return { "team1": teams[0], "team2": teams[1], 
                "team1xG": round(np.sum(list(team_one['xgs'])) , 3), 
                "team2xG": round(np.sum(list(team_two['xgs'])), 3),  
                "team1High": list(high_scores['xgs']),
                "team2High": list(high_scores2['xgs']),
                "team1Details": high_scores.to_json(orient='records'),
                "team2Details": high_scores2.to_json(orient='records'),
                "team1Goals": goals1.to_json(orient='records'),
                "team2Goals": goals2.to_json(orient='records')


                
            }

    except:
        return "err"


def main(train, ids):

    if train == True:
        with open('train_gxs.json') as f:
            data = json.loads(f.read())
            df = pd.json_normalize(data, record_path=['data'])
            df = df.fillna(0)
            df['timeDifferance'] = abs(df['timeDifference']) / 1000
            data_train = goal_angle(df)
            gradient_xg(data_train)
    else:
        with open('gxs.json') as f:
            data2 = json.loads(f.read())
            df2 = pd.json_normalize(data2, record_path=['data'])
            df2 = df2.fillna(0)
            df2['timeDifferance'] = abs(df2['timeDifference']) / 1000


        data_pred = goal_angle(df2)
        print(data_pred)

        for i in ids:

            #print(data_pred[data_pred['nhlIdStats'] == i])
            res_from_xgs = make_xg_pred(data_pred[data_pred['nhlIdStats'] == i])
            print(res_from_xgs)



app = Flask(__name__)
CORS(app)

@app.route("/api/python/v1/gx", methods=['GET', 'POST'])
def xgs():
    if request.method == 'GET':
        return "this is api for gxs ....  "
    
    if request.method == 'POST':
        res = request.get_json()
        df2 = pd.json_normalize(res, record_path=['data'])
       
        df2 = df2.fillna(0)
        df2['timeDifferance'] = abs(df2['timeDifference']) / 1000
        data_pred = goal_angle(df2)
        print(data_pred)

        res_from_xgs = make_xg_pred(data_pred)
        if res_from_xgs != "err":
            #print(res_from_xgs)
            return res_from_xgs

        else:

            return make_response(render_template('err.html', 500))

if __name__ == '__main__':
    app.run(debug=False, port=8098)


"""
#### Train model #####
main(True, [2])

##### Make prediction #####
idd = ["2022020357", "2022020358", "2022020359", "2022020360", "2022020361", "2022020362", "2022020363","2022020364"]
main(False, idd)

"""