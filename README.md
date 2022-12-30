# NHL XGS
Calculata xgs from nhl games shooting data using gradientboostingclassifier. Store results to strapi backend. Node fetch data from api and send it to python server to calculate results.

## INSTALL
Node 
```sh
node install
```
Python codes

1. pip install virtualenv
2. source env/bin/activate
3. pip install -r requirements.txt


### Method of xgs
Classifier model is trained 7 values.
[More deatials ftom Distance and Angle](https://soccermatics.medium.com/should-you-write-about-real-goals-or-expected-goals-a-guide-for-journalists-2cf0c7ec6bb6)
1. event distance from goal
2. goal angle to read more (
