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
import psutil
import sys

import logging
import socket
from logging.handlers import SysLogHandler

app = Flask(__name__)
app.config.update({
    'APISPEC_SWAGGER_URL': '/dbopenapi',
    'APISPEC_SWAGGER_UI_URL': '/dbswaggerui'
})
docs = FlaskApiSpec(app, document_options=False)

cors = CORS(app)
service_name = "database_core_service"
service_ip = "database-core-service"

ecostreet_core_service = "ecostreet-core-service"
configuration_core_service = "configuration-core-service"
play_core_service = "play-core-service"
admin_core_service = "admin-core-service"


users = [{"username":"admin", "password":"admin", "AccessToken":"0x7ac93hd98s"},{"username":"matej", "password": "1337h4x0r", "AccessToken":"0xf8423ab29c"}]

games = [{"name":"1337", "date":"14.1.2022"}]

class ContextFilter(logging.Filter):
    hostname = socket.gethostname()
    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True

syslog = SysLogHandler(address=('logs3.papertrailapp.com', 17630))
syslog.addFilter(ContextFilter())
format = '%(asctime)s %(hostname)s TimeProject: %(message)s'
formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
syslog.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(syslog)
logger.setLevel(logging.INFO)

class NoneSchema(Schema):
    response = fields.Str()

# FALLBACK
@app.errorhandler(404)
def not_found(e):
    return "The API call destination was not found.", 404


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
    logger.info("Database microservice: /dblogin accessed\n")
    
    # klic za mongodb
    #client = pymongo.MongoClient("mongodb+srv://admin:admin@ecostreet.hqlgz.mongodb.net/EcoStreet?retryWrites=true&w=majority")
    #db = client.ecostreetdb
    try:
        user = None
        for suser in users:
            if str(suser["username"]) == str(request.form["username"]):
                user = suser
        try:
            if(str(user["password"]) == str(request.form["password"])):
                logger.info("Database microservice: /dblogin finished\n")
                return {"response": user["AccessToken"]}, 200
            else:
                logger.info("Database microservice: /dblogin unauthorized access\n")
                return {"response": "Error 401: Unauthorized. Login  Incorrect."}, 401
        except:
            logger.info("Database microservice: /dblogin invalid login\n")
            return {"response": "Error 404: User Not Found."}, 404
    except Exception as err:
        logger.info("Database microservice: /dblogin hit an error\n")
        return {"response": str(err)}, 500
docs.register(login)

# COMMAND AUTHENTICATION FUNCTION
@app.route("/dbauthenticate", methods = ['POST'])
@use_kwargs({'AccessToken': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
def authenticate_request():
    global users
    logger.info("Database microservice: /dbauthenticate accessed\n")
    for suser in users:
        if str(suser["AccessToken"]) == str(request.form["AccessToken"]):
            # additional functionalities could be implemented
            logger.info("Database microservice: /dbauthenticate finished\n")
            return {"response": "200 OK"}, 200
    logger.info("Database microservice: /dbauthenticate unauthorized access\n")
    return {"response": "UNAUTHORIZED"}, 401
docs.register(authenticate_request)


# GET GAMES
@app.route("/dbgetgames", methods=["POST"])
@use_kwargs({'AccessToken':fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
def get_games():
    logger.info("Database microservice: /dbgetgames accessed\n")
    for suser in users:
        if str(suser["AccessToken"]) == str(request.form["AccessToken"]):
            logger.info("Database microservice: /dbgetgames finished\n")
            return {"response": games}, 200
    logger.info("Database microservice: /dbgetgames unauthorized access\n")
    return {"response": "UNAUTHORIZED"}, 401
docs.register(get_games)

# ADD GAME
@app.route("/dbaddgame", methods=["POST"])
@use_kwargs({'name': fields.Str(), 'date': fields.Str(), 'AccessToken':fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
@marshal_with(NoneSchema, description='Game already exists', code=402)
@marshal_with(NoneSchema, description='ERROR', code=500)
def add_game():
    logger.info("Database microservice: /dbaddgame accessed\n")
    for suser in users:
        if str(suser["AccessToken"]) == str(request.form["AccessToken"]):
            for game in games:
                if str(game["name"]) == str(request.form["name"]):
                    logger.info("Database microservice: /dbaddgame unable to create game\n")
                    return {"response": "Game already exists"}, 402
            try:
                games.append({"name":request.form["name"], "date":request.form["date"]})
                logger.info("Database microservice: /dbaddgame finished\n")
                return {"response": "200 OK"}, 200
            except Exception as e:
                logger.info("Database microservice: /dbaddgame hit an error\n")
                return {"response": e}, 500
    logger.info("Database microservice: /dbaddgame unauthorized access\n")
    return {"response": "UNAUTHORIZED"}, 401
docs.register(add_game)

# REMOVE GAME
@app.route("/dbremovegame", methods=["POST"])
@use_kwargs({'name': fields.Str(), 'AccessToken':fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
def remove_game():
    logger.info("Database microservice: /dbremovegame accessed\n")
    for suser in users:
        if str(suser["AccessToken"]) == str(request.form["AccessToken"]):
            for i in range(len(games)):
                game = games[i]
                if str(game["name"]) == str(request.form["name"]):
                    games.pop(i)
                    sys.stdout.write(games)
            try:
                logger.info("Database microservice: /dbremovegame finished\n")
                return {"response": "200 OK"}, 200
            except Exception as e:
                logger.info("Database microservice: /dbremovegame hit an error\n")
                return {"response": e}, 500
    logger.info("Database microservice: /dbremovegame unauthorized access\n")
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
    logger.info("Database microservice: /dbupdate_ip accessed\n")
    
    service_ip = request.form["ip"]
    
    data = {"name": service_name, "ip": service_ip}
    try:
        url = 'http://' + configuration_core_service + '/cfupdate'
        response = requests.post(url, data=data)
        logger.info("Database microservice: /dbupdate_ip finished\n")
        return {"response": response.text}, 200
    except:
        logger.info("Database microservice: /dbupdate_ip hit an error\n")
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
    global play_core_service
    global admin_core_service
    global service_ip
    global service_name
    global users
    logger.info("Database microservice: /dbconfig accessed\n")
    
    try:
        microservice = str(request.form["name"])
        ms_ip = str(request.form["ip"])
        if microservice == "ecostreet_core_service":
            ecostreet_core_service = ms_ip
        if microservice == "configuration_core_service":
            configuration_core_service = ms_ip
        if microservice == "play_core_service":
            play_core_service = ms_ip
        if microservice == "admin_core_service":
            admin_core_service = ms_ip
        logger.info("Database microservice: /dbconfig finished\n")
        return {"response": "200 OK"}, 200
    except Exception as err:
        logger.info("Database microservice: /dbconfig hit an error\n")
        return {"response": "Something went wrong."}, 500
docs.register(config_update)

# FUNCTION TO GET CURRENT CONFIG
@app.route("/dbgetconfig")
@marshal_with(NoneSchema, description='200 OK', code=200)
def get_config():
    global ecostreet_core_service
    global configuration_core_service
    global play_core_service
    global admin_core_service
    global service_ip
    global service_name
    global users
    logger.info("Database microservice: /dbgetconfig accessed\n")
    logger.info("Database microservice: /dbgetconfig finished\n")
    
    return {"response": str([ecostreet_core_service, configuration_core_service, play_core_service, admin_core_service])}, 200
docs.register(get_config)

# METRICS FUNCTION
@app.route("/dbmetrics")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='METRIC CHECK FAIL', code=500)
def get_health():
    logger.info("Database microservice: /dbmetrics accessed\n")
    start = datetime.datetime.now()
    try:
        url = 'http://' + configuration_core_service + '/cfhealthcheck'
        response = requests.get(url)
    except Exception as err:
        logger.info("Database microservice: /dbmetrics hit an error\n")
        return {"response": "METRIC CHECK FAIL: configuration unavailable"}, 500
    end = datetime.datetime.now()
    
    start2 = datetime.datetime.now()
    try:
        url = 'http://' + ecostreet_core_service + '/lghealthcheck'
        response = requests.get(url)
    except Exception as err:
        logger.info("Database microservice: /dbmetrics hit an error\n")
        return {"response": "METRIC CHECK FAIL: login service unavailable"}, 500
    end2 = datetime.datetime.now()
    
    delta1 = end-start
    crt = delta1.total_seconds() * 1000
    delta2 = end2-start2
    lrt = delta2.total_seconds() * 1000
    cpu_load = psutil.cpu_percent(2)
    ram_load = psutil.virtual_memory().percent
    health = {"metric check": "successful", "configuration response time": crt, "login response time": lrt, "database CPU load": str(cpu_load) + "%", "database RAM load": str(ram_load) + "%"}
    logger.info("Database microservice: /dbmetrics finished\n")
    return {"response": str(health)}, 200
docs.register(get_health)

# HEALTH CHECK
@app.route("/dbhealthcheck")
@marshal_with(NoneSchema, description='200 OK', code=200)
def send_health():
    logger.info("Database microservice: /dbhealthcheck accessed\n")
    try:
        url = 'http://' + ecostreet_core_service + '/lg'
        response = requests.get(url)
        url = 'http://' + configuration_core_service + '/cf'
        response = requests.get(url)
    except Exception as err:
        logger.info("Database microservice: /dbhealthcheck hit an error\n")
        return {"response": "Healthcheck fail: depending services unavailable"}, 500
    
    logger.info("Database microservice: /dbhealthcheck finished\n")
    return {"response": "200 OK"}, 200
docs.register(send_health)
