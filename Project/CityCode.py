import requests
import re


def city_code():
    url = 'http://webresource.c-ctrip.com/code/cquery/resource/address/flight/flight_new_poi_gb2312.js'
    response = requests.get(url)
    cityCodeList = re.findall('[\u4e00-\u9fa5]+\([A-Z]+\)\|\d+\|[A-Z]+', response.text)
    cityCodeDict = {}
    for cityCode in cityCodeList:
        # print(city_code)
        city = re.findall('[\u4e00-\u9fa5]+', cityCode)[0]
        code = cityCode.split('|')[2]
        cityCodeDict[city] = code

    return cityCodeDict


if __name__ == '__main__':
    print(city_code())