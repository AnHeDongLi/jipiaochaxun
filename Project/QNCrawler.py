# -*- coding:utf-8 -*-
import json
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from json.decoder import JSONDecodeError
from fake_useragent import UserAgent
import re
from urllib.parse import urlencode
import Proxys
from gevent import monkey
import gevent
import urllib3
import time
import hashlib

urllib3.disable_warnings()

monkey.patch_all(ssl=False)

se = requests.Session()

se.verify = False

journeys = []

QNTGQ_LEVEL = -1


def base_url(dcity, acity, ddate, code=''):
    url = 'https://flight.qunar.com/touch/api/domestic/wbdflightlist?'
    data = {
        'departureCity': dcity,
        'arrivalCity': acity,
        'departureDate': ddate,
    }
    if code == '':
        return url+urlencode(data)
    else:
        data['code'] = code
        data['type'] = 'list'
        return url+urlencode(data)


def key_err(json_data, key_str):
    if key_str in json_data:
        return json_data[key_str]
    else:
        return ''


header = headers()
proxy = Proxys.get_proxy()


def request_get_flight_number(url):
    global header, proxy
    url = url.strip()
    try:
        response = se.get(url, headers=header, timeout=30, allow_redirects=False, proxies=proxy)
        if response.status_code == 200 and 'uraTip' not in response.text:
            # print(response.text)
            return resolve_flights_no(response.json())
        else:
            print('[request_get_flight_number]状态码{}, 数据返回出错，正在重试'.format(response.status_code))
            header = headers()
            return request_get_flight_number(url)
    except (ConnectionError, JSONDecodeError, ReadTimeout):
        print('[request_get_flight_number]请求出错，正在重试')
        proxy = Proxys.get_proxy()
        return request_get_flight_number(url)


def request_get_flight_number_detail(url):
    global header, proxy
    url = url.strip()
    try:
        response = se.get(url, headers=header, timeout=30, allow_redirects=False, proxies=proxy)
        if response.status_code == 200 and 'uraTip' not in response.text:
            if response.json()['code'] == 0:
                # print(response.url)
                return resolve_flights_detail(response.json())
        else:
            if response.json()['msg'] == '该航班无报价':
                pass
            else:
                print('[request_get_flight_number_detail]状态码{}, 数据返回出错，正在重试'.format(response.status_code))
                header = headers()
                return request_get_flight_number_detail(url)
    except (ConnectionError, JSONDecodeError, ReadTimeout):
        print('[request_get_flight_number_detail]请求出错，正在重试')
        proxy = Proxys.get_proxy()
        return request_get_flight_number_detail(url)


def request_get_rule_detail(url, *args):
    global header, proxy
    if len(url) > 30:
        url = url.strip()
        try:
            response = se.get(url, headers=header, timeout=30, allow_redirects=False, proxies=proxy)
            response_text = re.sub('jsonp_.+\(|\)|callback\(', '', response.text)
            return resolve_rule_detail(json.loads(response_text), args[0], args[1])
        except (ConnectionError, JSONDecodeError, ReadTimeout):
            print('[request_get_rule_detail]请求出错，正在重试')
            proxy = Proxys.get_proxy()
            return request_get_rule_detail(url, args[0], args[1])
    else:
        return resolve_rule_detail(args[0], args[1])


def resolve_flights_no(json_data):
    try:
        flights = []
        for i in json_data['data']['flights']:
            if re.findall('binfo\d+', str(i)):
                pass
            else:
                flights.append(
                    [i['binfo']['depAirportCode'], i['binfo']['arrAirportCode'], i['binfo']['date'], i['code']])
        threads = [gevent.spawn(request_get_flight_number_detail,
                                base_url(dcity=item[0], acity=item[1],
                                         ddate=item[2],
                                         code=item[3])) for item in flights]
        gevent.joinall(threads)
    except KeyError:
        print('航班列表解析出错')


def resolve_flights_detail(json_data):
    flights_datas = json_data['data']['routes'][0]['fInfos'][0]['goInfos'][0]
    flights_data = {
        'carrier': key_err(flights_datas, 'airlineCode'),
        'flightNumber': key_err(flights_datas, 'flightNo'),
        'depAirport': key_err(flights_datas, 'depApCode'),
        'depTerminal': key_err(flights_datas, 'depTerminal'),
        'depTime': key_err(flights_datas, 'depDate')+' '+key_err(flights_datas, 'depTime'),
        'arrAirport': key_err(flights_datas, 'arrApCode'),
        'arrTerminal': key_err(flights_datas, 'arrTerminal'),
        'arrTime': key_err(flights_datas, 'arrDate')+' '+key_err(flights_datas, 'arrTime'),
        'aircraftCode': re.findall('[A-Za-z0-9]+', key_err(flights_datas, 'planeType'))[0],
        'meals': key_err(flights_datas, 'meal'),
    }
    cabinInfo_list = []
    cabinInfo_datas = json_data['data']['routes'][0]['vendors']
    if len(cabinInfo_datas) == 0:
        for i in cabinInfo_datas:
            rule = i['labels']
            if rule:
                rule = i['labels'][0]['queryUrl']
            else:
                rule = ''
            cabinInfo_data = {
                'productFlag': 0,
                'cabin': i['cabin'],
                'priceType': False,
                'price': i['price'],
                'tax': 60,
                'reducePrice': 0,
                'seats': '',
                'rule': rule
            }
            cabinInfo_list.append(cabinInfo_data)
    else:
        for i in cabinInfo_datas[0]:
            rule = i['labels']
            if rule:
                rule = i['labels'][0]['queryUrl']
            else:
                rule = ''
            cabinInfo_data = {
                'productFlag': 0,
                'cabin': i['cabin'],
                'priceType': False,
                'price': i['price'],
                'tax': 60,
                'reducePrice': 0,
                'seats': '',
                'rule': rule
            }
            cabinInfo_list.append(cabinInfo_data)
    flights_data['cabinInfos'] = cabinInfo_list
    if int(QNTGQ_LEVEL) == 1:
        threads = [gevent.spawn(request_get_rule_detail, 'https:'+item['rule'], flights_data, item['rule'])
                   for item in flights_data['cabinInfos']]
        gevent.joinall(threads)
    else:
        journeys.append(flights_data)


def resolve_rule_detail(json_data, *args):
    if 'cabinInfos' in str(json_data):
        journeys.append(json_data)
    else:
        if json_data['data']:
            tag_text = json_data['data'][0]['tgqAdult']['tgqText']
            items = args[0]
            for i in range(0, len(items['cabinInfos'])):
                if items['cabinInfos'][i]['rule'] == args[1] and '//flight.qunar.com/tgq/getSearchTgqList' \
                        in items['cabinInfos'][i]['rule']:
                    items['cabinInfos'][i]['rule'] = tag_text
            if '//flight.qunar.com/tgq/getSearchTgqList' not in str(items):
                journeys.append(items)
                # print(items)
        else:
            items = args[0]
            for i in range(0, len(items['cabinInfos'])):
                if items['cabinInfos'][i]['rule'] == args[1] and '//flight.qunar.com/tgq/getSearchTgqList' \
                        in items['cabinInfos'][i]['rule']:
                    items['cabinInfos'][i]['rule'] = ''
            if '//flight.qunar.com/tgq/getSearchTgqList' not in str(items):
                journeys.append(items)


if __name__ == '__main__':
    url = base_url('北京', '上海', '2018-06-22')
    request_get_flight_number(url)
    print(journeys)