# NHL XGS
Calculata xgs from nhl games shooting data using gradientboostingclassifier. Store results to strapi backend. Node fetch data from api and send it to python server to calculate results.

## INSTALL
Node 
```sh
node install
```
Python
Check libraries from requirements.txt. Using python 3.9 

### Details how xgs is calculated
Classifier model is trained 7 values. [More details from Distance and Angle](https://soccermatics.medium.com/should-you-write-about-real-goals-or-expected-goals-a-guide-for-journalists-2cf0c7ec6bb6)

1. Event distance from goal
2. Goal angle
3. Last event 
4. Last event distance
5. Shot 
6. Last Event proba to goal (pseudo)
7. Events time difference


## RUN PROJECT

Start python server
```sh
python3 xg.py
```
Run node this loads data from strapi backend calculate stats 
```sh
node index.js
```

