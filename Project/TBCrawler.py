# -*- coding:utf-8 -*-
import requests
from requests.exceptions import ConnectionError, ReadTimeout
import json
from json.decoder import JSONDecodeError
from fake_useragent import UserAgent
import re
from urllib.parse import urlencode
import Proxys
from gevent import monkey
import gevent

# 变量控制出行

TBCX_LEVEL = -1

# 变量控制退改签规则

TBTGQ_LEVEL = -1

journeys = []
monkey.patch_all(ssl=False)

se = requests.Session()


def key_err(json_data, key_str):
    if key_str in json_data:
        return json_data[key_str]
    else:
        return ''


def base_url(depcity, arrcity, depdate, arrdate='', skey='', qid='', flightno=''):
    url = 'https://sjipiao.fliggy.com/searchow/search.htm?'
    urls = []
    if flightno:
        base = {
            'callback': 'jsonp3266',
            'tripType': '0',
            'depCityName': depcity,
            'arrCityName': arrcity,
            'depDate': depdate,
            'arrDate': arrdate,
            'searchSource': '99',
            'searchBy': '1280',
            'sKey': skey,
            'qid': qid,
            'flightNo': flightno,
            'type': 'lowprice',
            'needMemberPrice': 'true',
            '_input_charset': 'utf-8',
            'openCb': 'false'
        }
        if int(TBCX_LEVEL) == 1:
            url_low = url + urlencode(base)
            urls.append(url_low)
            base['type'] = 'gaoduan'
            url_gaoduan = url + urlencode(base)
            urls.append(url_gaoduan)
            return urls
        else:
            return url+urlencode(base)
    else:
        base = {
            'callback': 'jsonp160',
            'tripType': '0',
            'depCityName': depcity,
            'arrCityName': arrcity,
            'depDate': depdate,
            'arrDate': arrdate,
            'searchSource': '99',
            'searchBy': '1280',
            'sKey': skey,
            'qid': qid,
            'flightNo': flightno,
            'needMemberPrice': 'true',
            '_input_charset': 'utf-8',
            'openCb': 'false'
        }
        url = url+urlencode(base)
        return url


def rule_base_url(*args):
    url = 'https://sjipiao.fliggy.com/nsearch/tuigaiqianJson.htm?'
    base = {
        'callback': 'jsonp3302',
        'depCity': args[0],
        'arrCity': args[1],
        'date': args[2],
        'airline': args[3],
        'cabin': args[4],
        'discount': args[5],
        'ticketPrice': args[6],
        'agentId': args[7],
        'fareType': args[8],
        'fareId': args[9],
        'policyId': args[10],
        'depAirport': args[11],
        'arrAirport': args[12],
        'price': args[13],
        'basicCabinPrice': args[14],
        'sprodType': args[15],
    }
    url = url+urlencode(base)
    return url


header = headers()
proxy = Proxys.get_proxy()


def request_get_flight_number(url):
    global header, proxy
    url = url.strip()
    try:
        response = se.get(url, headers=header, timeout=30, allow_redirects=False, proxies=proxy)
        if response.status_code == 200 and 'jsonp' in response.text:
            _str = re.sub(r'jsonp\d+\(|\);|\(|\)', '', response.text).strip()
            return resolve_flights_no(json.loads(_str))
        else:
            return request_get_flight_number(url)
    except (ConnectionError, JSONDecodeError, ReadTimeout):
        print('[request_get_flight_number]请求出错，正在重试')
        proxy = Proxys.get_proxy()
        return request_get_flight_number(url)


def request_get_flight_number_detail(urls):
    global header, proxy
    if isinstance(urls, list):
        for item in urls:
            url_1 = item.strip()

            def request_get_flight_numbers_detail(url):
                global proxy
                try:
                    response = se.get(url, headers=header, timeout=30, allow_redirects=False, proxies=proxy)
                    if response.status_code == 200 and 'jsonp' in response.text:
                        _str = re.sub(r'jsonp\d+\(|\);|\(|\)', '', response.text).strip()
                        for i in re.findall('\d+:{', _str):
                            n = re.search('\d+', i)[0]
                            _str = re.sub(i, '"{n}":'.format(n=n) + '{', _str)
                        if '很抱歉，没有查询到' not in _str:
                            return resolve_flights_detail(json.loads(_str))
                        else:
                            pass
                    else:
                        return request_get_flight_numbers_detail(url)
                except (ConnectionError, JSONDecodeError, ReadTimeout):
                    print('[request_get_flight_numbers_detail]请求出错，正在重试')
                    proxy = Proxys.get_proxy()
                    return request_get_flight_numbers_detail(url)
            request_get_flight_numbers_detail(url_1)
    else:
        url_2 = urls.strip()
        try:
            response = se.get(url_2, headers=header, timeout=30, allow_redirects=False, proxies=proxy)
            if response.status_code == 200 and 'jsonp' in response.text:
                _str = re.sub(r'jsonp\d+\(|\);|\(|\)', '', response.text).strip()
                for i in re.findall('\d+:{', _str):
                    n = re.search('\d+', i)[0]
                    _str = re.sub(i, '"{n}":'.format(n=n) + '{', _str)
                return resolve_flights_detail(json.loads(_str))
            else:
                return request_get_flight_number_detail(url_2)
        except (ConnectionError, JSONDecodeError, ReadTimeout):
            print('[request_get_flight_number_detail]请求出错，正在重试')
            proxy = Proxys.get_proxy()
            return request_get_flight_number_detail(url_2)


def request_get_rule_detail(url, *args):
    global header, proxy
    url = url.strip()
    try:
        response = se.get(url, headers=header, timeout=30, allow_redirects=False, proxies=proxy)
        if response.status_code == 200 and 'jsonp' in response.text:
            _str = re.sub(r'jsonp\d+\(|\);|\(|\)', '', response.text).strip()
            return resolve_rule_detail(json.loads(_str), args[0], args[1])
        else:
            return request_get_rule_detail(url, args[0], args[1])
    except (ConnectionError, JSONDecodeError, ReadTimeout):
        print('[request_get_rule_detail]请求出错，正在重试')
        proxy = Proxys.get_proxy()
        return request_get_rule_detail(url, args[0], args[1])


def resolve_flights_no(json_data):
    items = json_data['data']['flight']
    depcity = json_data['data']['depCityName']
    arrcity = json_data['data']['arrCityName']
    depdate = items[0]['depTime'].split(' ')[0]
    qid = json_data['qid']
    skey = json_data['skey']
    threads = [gevent.spawn(request_get_flight_number_detail,
                            base_url(depcity, arrcity, depdate, skey=skey, qid=qid,
                                     flightno=item['flightNo'])) for item in items]
    gevent.joinall(threads)


def resolve_flights_detail(json_data):
    flights_datas = json_data['data']['flight']
    flights_data = {
        'carrier': key_err(flights_datas, 'airlineCode'),
        'flightNumber': key_err(flights_datas, 'flightNo'),
        'depAirport': key_err(flights_datas, 'depAirport'),
        'depTerminal': key_err(flights_datas, 'depTerm'),
        'depTime': key_err(flights_datas, 'depTime'),
        'arrAirport': key_err(flights_datas, 'arrAirport'),
        'arrTerminal': key_err(flights_datas, 'arrTerm'),
        'arrTime': key_err(flights_datas, 'arrTime'),
        'aircraftCode': re.findall('[A-Za-z0-9]+', key_err(flights_datas, 'flightType'))[0],
        'meals': False,
    }
    cabins_data = json_data['data']['cabin']
    cabins_list = []
    for item in cabins_data:
        cabin = {
            'productFlag': 0,
            'cabin': item['cabin'],
            'priceType': False,
            'price': item['price'],
            'tax': 60,
            'rule': item['fareId'],
            'reducePrice': 0,
            'seats': False,
        }
        cabins_list.append(cabin)
    flights_data['cabinInfos'] = cabins_list
    if int(TBTGQ_LEVEL) == -1:
        if int(TBCX_LEVEL) == 1:
            if journeys:
                for i in range(0, len(journeys)):
                    if journeys[i]['flightNumber'] == flights_data['flightNumber']:
                        for c in journeys[i]['cabinInfos']:
                            flights_data['cabinInfos'].append(c)
                        journeys[i] = flights_data
            else:
                journeys.append(flights_data)
            if flights_data in journeys:
                pass
            else:
                journeys.append(flights_data)
        else:
            journeys.append(flights_data)
    else:
        threads = [gevent.spawn(request_get_rule_detail, rule_base_url(json_data['data']['depCityCode'],
                                json_data['data']['arrCityCode'], flights_data['depTime'].split(' ')[0],
                                flights_data['carrier'], item['cabin'], item['discount'], item['ticketPrice'],
                                item['agentId'], item['fareType'], item['fareId'], item['policyId'],
                                flights_data['depAirport'], flights_data['arrAirport'],
                                item['price'], item['basicCabinPrice'], item['sprodType']), flights_data,
                                item['fareId'])
                   for item in cabins_data]
        gevent.joinall(threads)


def resolve_rule_detail(json_data, *args):
    for item in args[0]['cabinInfos']:
        if args[1] == item['rule']:
            rule = json_data['data'][0]['tuigaiqian']
            item['rule'] = rule
    if not re.findall('\'rule\': \d\d\d\d\d\d\d\d', str(args[0])) and args[0] not in journeys:
        if int(TBCX_LEVEL) == 1:
            if journeys:
                for i in range(0, len(journeys)):
                    if journeys[i]['flightNumber'] == args[0]['flightNumber']:
                        for c in journeys[i]['cabinInfos']:
                            args[0]['cabinInfos'].append(c)
                        journeys[i] = args[0]
            else:
                journeys.append(args[0])
            if args[0] in journeys:
                pass
            else:
                journeys.append(args[0])
        else:
            journeys.append(args[0])


if __name__ == '__main__':
    url_index = base_url('重庆', '北京', '2018-06-22')
    request_get_flight_number(url_index)
    print(len(journeys))
    print(journeys)

