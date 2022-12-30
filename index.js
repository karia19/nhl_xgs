const axios  = require('axios');
const moment = require('moment');

const re = ':'

const App = async (id) => {
    const allData = []
    const collectData = []

    const res = await axios.get(`https://statsapi.web.nhl.com/api/v1/game/${id}/feed/live`)
    const gameData = res.data['liveData']['plays']['allPlays'];

    const boxScore = await axios.get(`https://statsapi.web.nhl.com/api/v1/game/${id}/boxscore`)
    const details = {
        nhlId: id,
        home: boxScore.data['teams']['home']['team']['name'],
        away: boxScore.data['teams']['away']['team']['name'],
        homeStats: boxScore.data['teams']['home']['teamStats']['teamSkaterStats'],
        awayStats: boxScore.data['teams']['away']['teamStats']['teamSkaterStats'],
    }

    for (let i = 0; i < gameData.length; i++){
        if (gameData[i]['result']['event'] == "Shot"){
            //console.log(gameData[i -1])
            //console.log(gameData[i])
            try {
            
                collectData.push({
                    nhlIdStats: id,
                    eventTeam: gameData[i]['team']['name'],
                    lastEventTeam: gameData[i -1]['team']['name'],
                    period: gameData[i]['about']['period'],
                    time: gameData[i]['about']['periodTime'].replace(re, ""),
                    timeDifference: (moment(gameData[i]['about']['dateTime']).diff(moment(gameData[i-1]['about']['dateTime']))) / 1000,
                    lastEventTime: gameData[i -1]['about']['periodTime'].replace(re, ""),
                    lastEventType: gameData[i -1]['result']['event'],
                    lastEventNum: await lastEvenytNumber(gameData[i -1]['result']['event']),
                    lastEventCordX: gameData[i-1]['coordinates']['x'],
                    lastEventCordY: gameData[i-1]['coordinates']['y'],
                    eventType: 'Shot',
                    eventNum: 0,
                    shotNum: await checkShotType(gameData[i]['result']['secondaryType']),
                    shotType: gameData[i]['result']['secondaryType'],
                    shooterName: gameData[i]['players'][0]['player']['fullName'],
                    eventCordX: gameData[i]['coordinates']['x'],
                    eventCordY: gameData[i]['coordinates']['y'],
                    powerPlay: "No Data"


                })
            } catch(err){
                console.log("")
            }

        } else if (gameData[i]['result']['event'] == "Goal") {
        
            try {
                collectData.push({
                    nhlIdStats: id,
                    eventTeam: gameData[i]['team']['name'],
                    lastEventTeam: gameData[i -1]['team']['name'],
                    period: gameData[i]['about']['period'],
                    time: gameData[i]['about']['periodTime'].replace(re, ""),
                    timeDifference: (moment(gameData[i]['about']['dateTime']).diff(moment(gameData[i-1]['about']['dateTime']))) / 1000,
                    lastEventTime: gameData[i -1]['about']['periodTime'].replace(re, ""),
                    lastEventType: gameData[i -1]['result']['event'],
                    lastEventNum: await lastEvenytNumber(gameData[i -1]['result']['event']),
                    lastEventCordX: gameData[i-1]['coordinates']['x'],
                    lastEventCordY: gameData[i-1]['coordinates']['y'],
                    eventType: 'Goal',
                    eventNum: 1,
                    shotNum: await checkShotType(gameData[i]['result']['secondaryType']),
                    shotType: gameData[i]['result']['secondaryType'],
                    shooterName: gameData[i]['players'][0]['player']['fullName'],
                    eventCordX: gameData[i]['coordinates']['x'],
                    eventCordY: gameData[i]['coordinates']['y'],
                    powerPlay: gameData[i]['result']['strength']['name']
                

                })
            } catch(err){
                console.log("")
            }

        }
       

    }
    details['data'] = collectData
    allData.push(details)
    //console.log(collectData)
    return allData
}
const checkShotType = async (data) => {
    /*
    SHOT TYPES BY NUMBERS
    1 = Wrist Shot 2 = Snap Shot
    3 = Backhand  4 = Slap Shot 5 = Tip-In 6 = Deflected
    */
    if (data == "Wrist Shot") {
        return 1
    } else if (data == "Snap Shot" ) {
        return 2
    } else if (data == "Backhand") {
        return 3
    } else if (data == "Slap Shot") {
        return 4
    } else if (data == "Tip-In") {
        return 5
    } else {
        return 6
    }
}
const lastEvenytNumber = async (data) => {
    /*
    SHot = 1 , Missed Shot = 2, Faceoff = 3, Hit = 4, Blocked Shot=5, Hit=6, Stoppage=7
    Penalty=8, Takeaway=9, Giveaway=10
    */
    if (data == "Shot") {
        return 1
    } else if (data == "Missed Shot" ) {
        return 2
    } else if (data == "Faceoff") {
        return 3
    } else if (data == "Hit") {
        return 4
    } else if (data == "Blocked Shor") {
        return 5
    } else if (data == "Hit") {
        return 6
    } else if (data == "Stoppage") {
        return 7
    } else if (data == "Panalty") {
        return 8
    } else if (data == "Takeaway") {
        return 9
    } else if (data == "Giveaway") {
        return 10
    } else {
        return 11
    }
}


async function  makeDays(){
    const ids = []
    for (let i = 1; i < 1200; i++){
        if (i < 10){
            ids.push(`000${i}`)
        } else if (i < 100) {
            //console.log(`00${i}`)
            ids.push(`00${i}`)
        } else if (i >= 100){
            //console.log(`0${i}`)
            ids.push(`0${i}`)
        } else if ( i >= 1000){
            ids.push(`${i}`)
        }
    }
    return ids
}

async function main(ids){
    const object = {}

    const dataFromXgs = await App(ids)

    try{
        
        const fromPython = await axios.post("http://127.0.0.1:8098/api/python/v1/gx", dataFromXgs)
        //console.log(fromPython.data);

        if (fromPython.status != 500){

                
                //console.log(fromPython.data)
                object['nhlId'] = dataFromXgs[0]['nhlId']
                object['season'] = "2022-2023"
                object['home'] = dataFromXgs[0]['home']
                object['away'] = dataFromXgs[0]['away']
                object['homeScore'] = dataFromXgs[0]['homeStats']['goals']
                object['awayScore'] = dataFromXgs[0]['awayStats']['goals']

                if (dataFromXgs[0]['home'] == fromPython.data['team1']){
                    object['homeXgs'] = fromPython.data['team1xG']
                    object['homeMissedHighChanges'] = fromPython.data['team1High'].length
                    object['awayXgs'] = fromPython.data['team2xG']
                    object['awayMissedHighChanges'] = fromPython.data['team2High'].length
                    object['homeDetails'] =  JSON.parse(fromPython.data['team1Details'])
                    object['awayDetails'] = JSON.parse(fromPython.data['team2Details'])
                    object['homeGoals'] =  JSON.parse(fromPython.data['team1Goals'])
                    object['awayGoals'] = JSON.parse(fromPython.data['team2Goals'])

                } else {
                    object['homeXgs'] = fromPython.data['team2xG']
                    object['awayXgs'] = fromPython.data['team1xG']
                    object['homeMissedHighChanges'] = fromPython.data['team2High'].length
                    object['awayMissedHighChanges'] = fromPython.data['team1High'].length
                    object['homeDetails'] = JSON.parse(fromPython.data['team2Details'])
                    object['awayDetails'] = JSON.parse(fromPython.data['team1Details'])
                    object['homeGoals'] =  JSON.parse(fromPython.data['team2Goals'])
                    object['awayGoals'] = JSON.parse(fromPython.data['team1Goals'])
                }
            
            
                
                //console.log(object);
                try{

                    const response = await axios.post("http://0.0.0.0:1337/api/xg-nhls", { data: object})
                    console.log(response.status);
                    if (response.status != 200){
                        console.log("error from update strapi ....")
                        return 200
                    }

                } catch(err){
                    console.log("err -from gxs");
                    return err
                }
            }
            else {
                console.log("error from xgs");
            }
        
    } catch(err){
        console.log("err message");
    }


    /*
    /// FOR TRAINING DATA ///
    const idNum = await makeDays()
    for (let i = 0; i < 700; i++) {
         await App(`201802${idNum[i]}`)
    }
    for (let i = 0; i < 600; i++) {
        await App(`201902${idNum[i]}`)
    }
    for (let i = 0; i < 500; i++) {
        await App(`202002${idNum[i]}`)
    }

    console.log(allData)
    dataToJson = JSON.stringify(allData)
    fs.writeFileSync("train_gxs.json",  dataToJson);
    //fs.writeFileSync("gxs.json",  dataToJson);
    */
    
}

const collectDataFromStarpi = async () => {
    const dataFromStrapi = await axios.get("http://0.0.0.0:1337/api/v1/nhl/season/stats/2022-2023")
    const gameIds = dataFromStrapi.data.map(x => x['nhlId']) 


    /// IF MAKING UPDATES TO DATABASE USE THIS METHOD ///
    /// REMEBER TO UPDATE STATSNHL FIRST AND PUT SERVER RUNNING xg.py ///
    const lastDataXgs = await axios.get("http://0.0.0.0:1337/api/v1/nhl/xgs")
    const lastIds = lastDataXgs.data.map(x => x['nhlId']);


    for (let i = lastIds.length; i < gameIds.length; i++){
        console.log(gameIds[i]);
        main(gameIds[i])
    }
    
    /*
    /// IF DATABASE IS EMPTY USE THIS METHOD TO FILL... ///
    let index = -1
    setInterval(() => {
        index += 1
        if (index < gameIds.length){
            main(gameIds[index])
            //console.log(gameIds[index]);
        } else {
            console.log("Stop process");
        }

    }, 1000)
    */
   
 
}

collectDataFromStarpi()
//main("2022020389")