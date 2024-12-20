from flask import Flask,request,render_template, Response
import pyrebase
import requests
import joblib

app = Flask(__name__)

#add configuration from firebase using SDK
config = {
  "apiKey": "",
  "authDomain": "",
  "projectId": "",
  "storageBucket": "",
  "messagingSenderId": "",
  "appId": "",
  "databaseURL":"",
  "measurementId": ""
};
firebase=pyrebase.initialize_app(config)
db = firebase.database()
loaded_rf = joblib.load("my_random_forest.joblib")
url = "https://air-quality.p.rapidapi.com/current/airquality"

city = ["Delhi","Mumbai","Kolkata","Bangalore","Chennai"]
lat = [28.6600,18.9667,22.5411,12.9699,13.0825]
lng = [77.2300,72.8333,88.3378,77.5980,80.2750]

#Utilized Rapid-API to fetch real time data for the cities
c=0
for i,j in zip(lat,lng):
  querystring = {"lat":f"{i}","lon":f"{j}"}
  headers = {
    'x-rapidapi-host': "air-quality.p.rapidapi.com",
    'x-rapidapi-key': "9090a5b2ebmshe3b4fc81b1f0f56p17108cjsn3d87a9516544"
    }

  response = requests.request("GET", url, headers=headers, params=querystring)
  main = response.json()
  data = main['data']
  co = data[0]['co']
  no2 = data[0]['no2']
  o3 = data[0]['o3']
  pm10 = data[0]['pm10']
  pm25 = data[0]['pm25']
  so2 = data[0]['so2']
  aqi=data[0]['aqi']
  pm = pm25+pm10
  pre = [pm,no2,0,so2,co,o3]
  air=pre
  # Using Random Forest Model for prediction
  pred=loaded_rf.predict([pre])
  pred=float(pred)
  air.append(pred)
  air.append(aqi)
  print(c,"  ",air)
  db.child("AQI1").child(city[c]).set(air)
  c=c+1
c=0
@app.route('/', methods=['GET','POST'])
def index():
    return str(pred)
    
if __name__ == '__main__':
    app.run(debug=True)