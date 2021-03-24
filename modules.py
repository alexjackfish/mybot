import netsnmp
import datetime
import ipaddress
import time
import re
import constant
import subprocess
import dataset
import requests
import sqlalchemy
from ping3 import ping
from netmiko import ConnectHandler
import netaddr
import openpyxl
import pandas as pd
import puresnmp
from puresnmp.x690.types import Integer, OctetString


# Определение иерархии хоста
def get_type(host, model):
    if ipaddress.IPv4Address(host) in ipaddress.IPv4Network(constant.MO_switchs):
        get_type = "switches"
        return get_type
    else:
        get_type = "other"
        return get_type

def load_users(fund):
    b = 0
    users = open(f'{constant.WORK_DIR}/users.txt')
    users = users.readlines()
    load_users = []
    for user in users:
        user = int((users[b].split('='))[1])
        load_users.insert(b, user)
        b = b + 1
    return load_users

def load_id_users(chat_id):
    b = 0
    users = open(f'{constant.WORK_DIR}/users.txt')
    users = users.readlines()
    for user in users:
        if chat_id == int((users[b].split('='))[1]):
            return b
        b = b + 1
    return load_users


def back_to_user_keyboard(func):
    if func == "menu":
        reply_keyboard = [
            ["10.36.20.244","10.36.52.244"],
            ["10.36.20.245","10.36.52.245"],
        ]
    
    elif func == 'get_type == "switches"':
        
            
            reply_keyboard = [
            ["10.36.20.244","10.36.52.244"],
            ["10.36.20.245","10.36.52.245"],
        ]
    return reply_keyboard

# Определение модели устройтсва
def get_model(host):
    try:
        if ipaddress.IPv4Address(host) in ipaddress.IPv4Network(
            constant.MO_switchs
        ):
            model = netsnmp.snmpget(
                constant.oid_model,
                DestHost=host,
                Version=2,
                Community=constant.ro_switchs,
            )[0].decode("utf-8")
        return model
    except AttributeError:
        model = "Ошибка"
        return model
    except ipaddress.AddressValueError:
        model = "Ошибка"
        return model

def basic_info(host, model):
    try:
        if ipaddress.IPv4Address(host) in ipaddress.IPv4Network(
            constant.MO_switchs
        ):
            try:
                sysname = (
                    netsnmp.snmpget(
                        constant.oid_sysname,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                uptime = (
                    netsnmp.snmpget(
                        constant.oid_cpu,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                uptime1 = (
                    netsnmp.snmpget(
                        constant.oid_ramf,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")
                   
                uptime2 = (
                    netsnmp.snmpget(
                        constant.oid_ramt,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")
                uptime3 = (
                    netsnmp.snmpget(
                        constant.oid_rama,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")       
                stastus = (
                    netsnmp.snmpget(
                        constant.oid_status,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")
                        
                iau = (
                    netsnmp.snmpget(
                        constant.oid_iau,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")
                          
                ias = (
                    netsnmp.snmpget(
                        constant.oid_ias,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")
                uptime1 = int(uptime1) / 1000000000
                uptime2 = int(uptime2) / 1000000000
                uptime3 = int(uptime3) / 1000000000
                uptime4 = int(uptime3 / uptime2 * 100 ) 
                uptime1 = int('{:.0f}'.format(uptime1))
                uptime2 = int('{:.0f}'.format(uptime2))
                uptime3 = int('{:.0f}'.format(uptime3))
                result = f"{constant.UP} IP: {host}\nИмя устройства: {sysname}\nCPU:{uptime}%\nRAM:{uptime4}%\nStatus ClusterXL:{stastus}\nIdentity Awareness Status:{ias}\nIdentity Awareness Users:{iau}\nTotal RAM:{uptime2}GB\nFree RAM:{uptime1}GB\nUsed RAM:{uptime3}GB"
                return result
            except:
                result = f"{constant.CRITICAL} Устройство не на связи"
                return result
    except ipaddress.AddressValueError:
        result = "Неверный IP"
        return result

