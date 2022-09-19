from datetime import datetime
from operator import truediv
from flask import Flask, render_template, request, jsonify
import json
import logging
import datetime
import base64
import sys
import os
import redis

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
irds_channel = os.getenv('RDS_CHANNEL');

log('Підключеня до redis: ' + 'host=' + irds_host  )
log('Підключеня до redis: ' + 'Порт=' + str(irds_port)  )
log('Підключеня до redis: ' +  'Пароль: ' + irds_psw )
    
log('Підключеня до redis: ' + 'host=' + irds_host + ' Порт=' + irds_port + ' Пароль: ' + irds_psw + ' Канал=' + irds_channel)

log("Connect to Redis")
red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=True)
log(" Trying PING")
log("1=======================")
rping=red.ping()
log( str(rping) )


#==========================================
# Публікація команди в чергу
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ap_cmd = { "cmd": "loadcfg", "params": {}}
#========================================== 
def sendCmd( ap_cmd ):
    log("Відправляюь комнаду сервсам: ")
    res=red.publish(irds_channel, json.dumps(ap_cmd) )
    return res   





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
    log('Call APICall counter: redis-result=' , 'health')
    return json.dumps({'success':True}), 200, {'Content-Type':'application/json'}


