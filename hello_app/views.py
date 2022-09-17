from datetime import datetime
from operator import truediv
from flask import Flask, render_template, request
import json
import logging
import datetime
import base64
import sys
import os
import redis

import sqlalchemy.dialects.postgresql
from sqlalchemy import create_engine

application = Flask(__name__)


# ============================================================================
# Формування RestAPi відповіді з помилкою у випадку не коректних вхідних даних 
# ============================================================================
class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, code, message, target=None, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code 
        if target is not None:
            self.target = target
        else:
            self.target = ""
        self.payload = payload

    def to_dict(self):
        errdsc = {}
        errdsc["code"] = self.code
        errdsc["description"] = self.message
        errdsc["target"] = self.target
        rv={}
        rv["Error"]=errdsc
        rv["Error"]["Inner"]=dict(self.payload or ())
        return rv


# ============================================================================
# Формування RestAPi відповіді з помилкою у випадку не коректного методу
# ============================================================================
class UnexpectedHttpMethod(Exception):
    status_code = 404

    def __init__(self, code, message, target=None, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code 
        if target is not None:
            self.target = target
        else:
            self.target = ""
        self.payload = payload

    def to_dict(self):
        errdsc = {}
        errdsc["code"] = self.code
        errdsc["description"] = self.message
        errdsc["target"] = self.target
        rv={}
        rv["Error"]=errdsc
        rv["Error"]["Inner"]=dict(self.payload or ())
        return rv




# =======================================================
# Перехоплювач помилок API  та формування відповіді
# =======================================================

@application.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    r=e.to_dict()
    return json.dumps(r), e.status_code, {'Content-Type':'application/json'}



@application.errorhandler( UnexpectedHttpMethod)
def unexpected_http_method_error(e):
    r=e.to_dict()
    return json.dumps(r), e.status_code, {'Content-Type':'application/json'}



logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

#===================================================
# Функціф внутрішнього логера
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===================================================
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)

log("Підключення до Redis")

irds_host = os.getenv('RDS_HOST');
irds_port = os.getenv('RDS_PORT');
irds_psw = os.getenv('RDS_PSW');

log('Підключеня до redis: ' + 'host=' + irds_host  )
log('Підключеня до redis: ' + 'Порт=' + str(irds_port)  )
log('Підключеня до redis: ' +  'Пароль: ' + irds_psw )

red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=True)
log(" Trying PING")
log("1=======================")
rping=red.ping()
log( str(rping) )
# Set KEY NAME FOR API COUNTER
i_apicntr_key="APICALLS"
if rping:
    log("redis Connected")

    log("set predefined key by 0 value: " +  i_apicntr_key ) 
    red.set(i_apicntr_key, 0)
    log("Check the valuse of key: " + i_apicntr_key )
    log( "Read value: " + str( red.get(i_apicntr_key) ) )


   
else:
    log("redis NOT CONNECTED!!!")    

log("2=======================")



log("1==========POSTGRES=============")
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USR')
db_pass = os.getenv('DB_PSW')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
log("2==========POSTGRES=============")
db_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)
log("3==========POSTGRES=============" + db_string)
db = create_engine(db_string)


#==================================================
# Функція підраховування викликів API
#
#=================================================
def apicallscntr():
    l_label="apicallscntr"
    log("Старт", l_label)
    return red.incrby( i_apicntr_key, 1)




#=================================================
# Головна сторінка
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#=================================================
@application.route("/")
def home():
    log("render home.html" )
    return render_template("home.html")


#=================================================
# Про програму
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#=================================================
@application.route("/about/")
def about():
    return render_template("about.html")





#===========================================================================
#    *********** Сервісні  АПІ для роботи EDS ******************************
#===========================================================================

# =================================================================================
# Метод health check
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Повертає {'success':True} якщо контейнер працює
# =================================================================================
@application.route("/api/health", methods=["GET"])
def health():
    
    log('Health check', 'health')
    log('Call APICall counter', 'health')
    r=apicallscntr()
    log('Call APICall counter: redis-result=' + str(r), 'health')
    return json.dumps({'success':True}), 200, {'Content-Type':'application/json'}


# =================================================================================
# Метод повертає список всіх ключів в БД redis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Повертає {'success':True} якщо контейнер працює
# =================================================================================
@application.route("/api/key", methods=["GET"])
def get_keys_list():
    l_label='get_keys_list'
    log('Start', l_label)
    log('Call redis api', l_label)
    result=red.keys("*")
    log('print redis-result= ' + json.dumps(result)  , l_label)
    return json.dumps({'list': result}), 200, {'Content-Type':'application/json'}


# =================================================================================
# Метод повертає список всіх ключів в БД redis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Повертає {'success':True} якщо контейнер працює
# =================================================================================
@application.route("/api/key", methods=["POST"])
def set_key():
    l_label='set_key'
    log( 'старт', l_label)
    log( 'Отримую тіло запиту', l_label)
    body = request.get_json()
    log( 'Розбираю тіло запиту в dict' + json.dumps(  body ), l_label)
    keyname = body["keyname"]
    keyval = body["keyvalue"]
    log('Call redis API '  , l_label)
    result=red.set(keyname, keyval)
    log('print redis-result= '  , l_label)
    log('print redis-result= ' + json.dumps(result)  , l_label)
    return json.dumps({'redis_result': result}), 200, {'Content-Type':'application/json'}
