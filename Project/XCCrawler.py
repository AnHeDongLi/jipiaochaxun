# -*- coding:utf-8 -*-
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from json.decoder import JSONDecodeError
from fake_useragent import UserAgent
from urllib.parse import urlencode
import Proxys
from gevent import monkey
import urllib3
urllib3.disable_warnings()

monkey.patch_all(ssl=False)

journeys = []


def request_get_flight_number_detail(url):
    if url:
        url = url.strip()
    try:
        response = requests.get(url, headers=headers(), timeout=10, allow_redirects=False, proxies=Proxys.get_proxy())
        if response.status_code == 200 and '不通航' not in response.json() and response.json()['lps'] != {}:
            return resolve_flights_detail(response.json())
        else:
            print('状态码{},数据传输出错,请排除Cookie,Proxy,或者参数传输是否有误, 正在重试'.format(response.status_code))
            return request_get_flight_number_detail(url)
    except (ConnectionError, JSONDecodeError, ReadTimeout):
        print('请求出错，正在重试')
        return request_get_flight_number_detail(url)


def resolve_flights_detail(json_data):
    try:
        for item in json_data['fis'][1:]:
            carrier = item['alc']
            depAirport = item['dpc']
            depTerminal = item['dsmsn']
            arrAirport = item['apc']
            arrTerminal = item['asmsn']
            depTime = item['dt']
            arrTime = item['at']
            flightNumber = item['fn']
            aircraftCode = item['cf']['c']
            if item['sdft'] != None:
                shared = 1
                actualFlightNo = item['sdft']
            else:
                shared = 0
                actualFlightNo = ' '
            flights = {
                'carrier': carrier,
                'depAirport': depAirport,
                'depTerminal': depTerminal,
                'arrAirport': arrAirport,
                'arrTerminal': arrTerminal,
                'depTime': depTime,
                'arrTime': arrTime,
                'flightNumber': flightNumber,
                'aircraftCode': aircraftCode,
                'actualFlightNo': actualFlightNo,
                'shared': shared,
            }
            flights_list = []
            for scs in item['scs']:
                cabin = scs['sc']
                price = scs['p']
                tax = 60
                rule = scs['tgq']['edn']+';'+scs['tgq']['rfn']+';'+scs['tgq']['rrn']
                flights_list.append(
                    {
                        'productFlag': 0,
                        'cabin': cabin,
                        'priceType': False,
                        'price': price,
                        'tax': tax,
                        'rule': rule,
                        'fuel': 0,
                        'reducePrice': 0,
                        'seats': 0,
                    }
                )
            flights['cabinInfos'] = flights_list
            journeys.append(flights)
        return journeys
    except KeyError:
        print('KeyError')
        return None


def main(DCity1, ACity1, DDate1, DDate2=''):
    base = {
        'DCity1': DCity1,
        'ACity1': ACity1,
        'DDate1': DDate1,
        'SearchType': 'S',
        'DDate2': DDate2,
    }
    url = 'http://flights.ctrip.com/domesticsearch/search/SearchFirstRouteFlights?'
    url = url+urlencode(base)
    return request_get_flight_number_detail(url)


if __name__ == '__main__':
    print(main('CKG', 'SHA', '2018-06-30'))
    print(journeys)