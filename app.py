import datetime
from flask import Flask
from flask import request
import pymongo
import requests
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from flask_apispec import FlaskApiSpec
from marshmallow import Schema

app = Flask(__name__)
app.config.update({
    'APISPEC_SWAGGER_URL': '/dbopenapi',
    'APISPEC_SWAGGER_UI_URL': '/dbswaggerui'
})
docs = FlaskApiSpec(app, document_options=False)

service_name = "database_core_service"
service_ip = "34.96.72.77"

ecostreet_core_service = "34.96.72.77"
configuration_core_service = "34.96.72.77"

users = [{"username":"admin", "password":"admin", "AccessToken":"0x7ac93hd98s"},{"username":"matej", "password": "1337h4x0r", "AccessToken":"0xf8423ab29c"}]
class NoneSchema(Schema):
        pass

# HEALTH PAGE
@app.route("/")
@marshal_with(NoneSchema, description='200 OK', code=200)
def health():
    return "200"
docs.register(health)

# HOME PAGE
@app.route("/db")
@marshal_with(NoneSchema, description='200 OK', code=200)
def hello_world():
    return "Database microservice."
docs.register(hello_world)

# USER AUTHENTICATION - DATABASE MOCKUP
@app.route('/dblogin', methods = ['POST'])
@use_kwargs({'username': fields.Str(), 'password': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='UNAUTHORIZED', code=401)
@marshal_with(NoneSchema, description='USER NOT FOUND', code=404)
def login():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/dblogin accessed")
    try:
        user = None
        for suser in users:
            if suser["username"] == request.form["username"]:
                user = suser
        try:
            if(user["password"] == request.form["password"]):
                return user["AccessToken"]
            else:
                return "Error 401: Unauthorized. Login  Incorrect.", 401
        except:
            return "Error 404: User Not Found.", 404
    except Exception as err:
        return err
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
            return "200 OK"
    return "UNAUTHORIZED", 401
docs.register(authenticate_request)

 
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
        return response.text
    except:
        return "Something went wrong.", 500
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
        return "200 OK"
    except Exception as err:
        return "Something went wrong.", 500
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
    
    return str([ecostreet_core_service, configuration_core_service])
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
        return "METRIC CHECK FAIL: configuration unavailable", 500
    end = datetime.datetime.now()
    
    start2 = datetime.datetime.now()
    try:
        url = 'http://' + ecostreet_core_service + '/lghealthcheck'
        response = requests.get(url)
    except Exception as err:
        return "METRIC CHECK FAIL: login service unavailable", 500
    end2 = datetime.datetime.now()
    
    delta1 = end-start
    crt = delta1.total_seconds() * 1000
    delta2 = end2-start2
    lrt = delta2.total_seconds() * 1000
    health = {"metric check": "successful", "configuration response time": crt, "login response time": lrt}
    return str(health)
docs.register(get_health)

# HEALTH CHECK
@app.route("/dbhealthcheck")
@marshal_with(NoneSchema, description='200 OK', code=200)
def send_health():
    print("/dbhealthcheck accessed")
    return "200 OK"
docs.register(send_health)
