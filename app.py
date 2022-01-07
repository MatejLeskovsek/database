import datetime
from flask import Flask
from flask import request
import pymongo
import requests
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from flask_apispec import FlaskApiSpec
from marshmallow import Schema
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config.update({
    'APISPEC_SWAGGER_URL': '/dbopenapi',
    'APISPEC_SWAGGER_UI_URL': '/dbswaggerui'
})
docs = FlaskApiSpec(app, document_options=False)

cors = CORS(app)
service_name = "database_core_service"
service_ip = "35.190.119.123"

ecostreet_core_service = "35.190.119.123"
configuration_core_service = "35.190.119.123"


users = [{"username":"admin", "password":"admin", "AccessToken":"0x7ac93hd98s"},{"username":"matej", "password": "1337h4x0r", "AccessToken":"0xf8423ab29c"}]

games = [{"name":"1337", "date":"14.1.2022"}]

class NoneSchema(Schema):
    response = fields.Str()

# HEALTH PAGE
@app.route("/")
@marshal_with(NoneSchema, description='200 OK', code=200)
def health():
    return {"response": "200"}, 200
docs.register(health)

# HOME PAGE
@app.route("/db")
@marshal_with(NoneSchema, description='200 OK', code=200)
def hello_world():
    return {"response": "Database microservice."}, 200
docs.register(hello_world)

# USER AUTHENTICATION - DATABASE MOCKUP 
@app.route('/dblogin', methods = ['POST'])
@use_kwargs({"username": fields.Str(), "password": fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
@marshal_with(NoneSchema, description='USER NOT FOUND', code=404)
@marshal_with(NoneSchema, description='INTERNAL SERVER ERROR', code=500)
def login():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/dblogin accessed")
    
    # klic za mongodb
    #client = pymongo.MongoClient("mongodb+srv://admin:admin@ecostreet.hqlgz.mongodb.net/EcoStreet?retryWrites=true&w=majority")
    #db = client.ecostreetdb
    try:
        user = None
        for suser in users:
            if suser["username"] == request.form["username"]:
                user = suser
        try:
            if(user["password"] == request.form["password"]):
                return {"response": user["AccessToken"]}, 200
            else:
                return {"response": "Error 401: Unauthorized. Login  Incorrect."}, 401
        except:
            return {"response": "Error 404: User Not Found."}, 404
    except Exception as err:
        return {"response": str(err)}, 500
docs.register(login)

# COMMAND AUTHENTICATION FUNCTION
@app.route("/dbauthenticate", methods = ['POST'])
@use_kwargs({'AccessToken': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
def authenticate_request():
    global users
    print("/dbauthenticate accessed")
    for suser in users:
        if suser["AccessToken"] == request.form["AccessToken"]:
            # additional functionalities could be implemented
            return {"response": "200 OK"}, 200
    return {"response": "UNAUTHORIZED"}, 401
docs.register(authenticate_request)


# GET GAMES
@app.route("/dbgetgames")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
def get_games():
    for suser in users:
        if suser["AccessToken"] == request.form["AccessToken"]:
            return {"response": games}, 200
    return {"response": "UNAUTHORIZED"}, 401
docs.register(get_games)

# ADD GAME
@app.route("/dbaddgame", methods=["POST"])
@use_kwargs({'name': fields.Str(), 'date': fields.Str(), 'AccessToken':fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
@marshal_with(NoneSchema, description='Game already exists', code=402)
def add_game():
    for suser in users:
        if suser["AccessToken"] == request.form["AccessToken"]:
            for game in games:
                if game["name"] == request.form["name"]:
                    return {"response": "Game already exists"}, 402
            games.append({"name":request.form["name"], "date":request.form["date"]})
            print(games)
            return {"response": "200 OK"}, 200
    return {"response": "UNAUTHORIZED"}, 401
docs.register(add_game)

# REMOVE GAME
@app.route("/dbremovegame", methods=["POST"])
@use_kwargs({'name': fields.Str(), 'AccessToken':fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
def remove_game():
    for suser in users:
        if suser["AccessToken"] == request.form["AccessToken"]:
            for i in range(len(games)):
                game = games[i]
                if game["name"] == request.form["name"]:
                    games.pop(i)
                    print(games)
            return {"response": "200 OK"}, 200
    return {"response": "UNAUTHORIZED"}, 401
docs.register(remove_game)

 
# SERVICE IP UPDATE FUNCTION
@app.route("/dbupdate_ip", methods = ['POST'])
@use_kwargs({'name': fields.Str(), 'ip': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
def update_ip():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/dbupdate_ip accessed")
    
    service_ip = request.form["ip"]
    
    data = {"name": service_name, "ip": service_ip}
    try:
        url = 'http://' + configuration_core_service + '/cfupdate'
        response = requests.post(url, data=data)
        return {"response": response.text}, 200
    except:
        return {"response": "Something went wrong."}, 500
docs.register(update_ip)

# FUNCTION TO UPDATE IP'S OF OTHER SERVICES
@app.route("/dbconfig", methods = ['POST'])
@use_kwargs({'name': fields.Str(), 'ip': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
def config_update():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/dbconfig accessed")
    
    try:
        microservice = request.form["name"]
        ms_ip = request.form["ip"]
        if microservice == "database_core_service":
            ecostreet_core_service = ms_ip
        if microservice == "configuration_core_service":
            configuration_core_service = ms_ip
        return {"response": "200 OK"}, 200
    except Exception as err:
        return {"response": "Something went wrong."}, 500
docs.register(config_update)

# FUNCTION TO GET CURRENT CONFIG
@app.route("/dbgetconfig")
@marshal_with(NoneSchema, description='200 OK', code=200)
def get_config():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/dbgetconfig accessed")
    
    return {"response": str([ecostreet_core_service, configuration_core_service])}, 200
docs.register(get_config)

# METRICS FUNCTION
@app.route("/dbmetrics")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='METRIC CHECK FAIL', code=500)
def get_health():
    print("/dbmetrics accessed")
    start = datetime.datetime.now()
    try:
        url = 'http://' + configuration_core_service + '/cfhealthcheck'
        response = requests.get(url)
    except Exception as err:
        return {"response": "METRIC CHECK FAIL: configuration unavailable"}, 500
    end = datetime.datetime.now()
    
    start2 = datetime.datetime.now()
    try:
        url = 'http://' + ecostreet_core_service + '/lghealthcheck'
        response = requests.get(url)
    except Exception as err:
        return {"response": "METRIC CHECK FAIL: login service unavailable"}, 500
    end2 = datetime.datetime.now()
    
    delta1 = end-start
    crt = delta1.total_seconds() * 1000
    delta2 = end2-start2
    lrt = delta2.total_seconds() * 1000
    health = {"metric check": "successful", "configuration response time": crt, "login response time": lrt}
    return {"response": str(health)}, 200
docs.register(get_health)

# HEALTH CHECK
@app.route("/dbhealthcheck")
@marshal_with(NoneSchema, description='200 OK', code=200)
def send_health():
    print("/dbhealthcheck accessed")
    try:
        url = 'http://' + ecostreet_core_service + '/lg'
        response = requests.get(url)
        url = 'http://' + configuration_core_service + '/cf'
        response = requests.get(url)
    except Exception as err:
        return {"response": "Healthcheck fail: depending services unavailable"}, 500
    return {"response": "200 OK"}, 200
docs.register(send_health)
