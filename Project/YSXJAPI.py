# coding:utf-8
from flask import Flask, jsonify, request
import QNCrawlerAPI
import QNCrawler
import XCCrawler
import XCCrawlerAPI
import re
from CityCode import city_code
from gevent import monkey
import TBCrawlerAPI
import TBCrawler
# from gevent.pywsgi import WSGIServer

monkey.patch_all(ssl=False)

app = Flask(__name__)


@app.route('/YSXJ/QNGetData', methods=['GET'])
def qn_app():
    QNCrawler.journeys = []
    dataTag = request.args.get('dataTag')
    tripType = request.args.get('tripType')
    depair = request.args.get('depair')
    arrair = request.args.get('arrair')
    deptime = request.args.get('depDate')
    arrDate = request.args.get('arrDate')
    rule = request.args.get('rule')
    flightNo = request.args.get('flightNo')
    if re.findall('[A-Z\u4e00-\u9fa5]+', depair) and re.findall('[A-Z\u4e00-\u9fa5]+', arrair) and re.findall('\d+-\d+-\d+', deptime):
        if rule and deptime and depair and arrair:
            if flightNo:
                tasks = QNCrawlerAPI.QNSpiderFlight(depair, arrair, deptime, flightNo, rule).get_data()
            else:
                tasks = QNCrawlerAPI.QNSpiderAll(depair, arrair, deptime, rule).get_data()
            if tasks:
                return jsonify({
                          "code": 0,
                          "msg": "success",
                          "dataTag": dataTag,
                          "extra ": "",
                          "imgBase64": "",
                          "journeys": tasks
                })
            else:
                return jsonify({
                    "code": -2,
                    "msg": "询价失败",
                    "dataTag": dataTag,
                    "error": "没有此航班（航线）信息"
                })
        else:
            return jsonify({"code": -1, 'msg': '询价失败'})
    else:
        return jsonify({"code": -1, 'msg': '询价失败'})


@app.route('/YSXJ/XCGetData', methods=['GET'])
def xc_app():
    XCCrawler.journeys = []
    dataTag = request.args.get('dataTag')
    tripType = request.args.get('tripType')
    depair = request.args.get('depair')
    arrair = request.args.get('arrair')
    deptime = request.args.get('depDate')
    arrDate = request.args.get('arrDate')
    flightNo = request.args.get('flightNo')
    if re.findall('[\u4e00-\u9fa5]+', depair) and re.findall('[\u4e00-\u9fa5]+', arrair) and re.findall(
            '\d+-\d+-\d+', deptime):
        if depair and arrair and deptime:
            depair = city_code()[depair]
            arrair = city_code()[arrair]
            tasks = XCCrawlerAPI.XCCrawlerAll(depair, arrair, deptime).get_data()
            if flightNo:
                task = XCCrawlerAPI.XCCrawlerFlight(flightNo).resolve_flights_no_detail(tasks)
                return jsonify({
                    "code": 0,
                    "msg": "success",
                    "dataTag": dataTag,
                    "extra ": "",
                    "imgBase64": "",
                    "journeys": task
                })
            else:
                return jsonify({
                    "code": 0,
                    "msg": "success",
                    "dataTag": dataTag,
                    "extra ": "",
                    "imgBase64": "",
                    "journeys": tasks
                })
        else:
            return jsonify({"code": -1, 'msg': '询价失败'})
    else:
        return jsonify({"code": -1, 'msg': '询价失败'})


@app.route('/YSXJ/TBGetData', methods=['GET'])
def tb_app():
    TBCrawler.journeys = []
    dataTag = request.args.get('dataTag')
    tripType = request.args.get('tripType')
    depair = request.args.get('depair')
    arrair = request.args.get('arrair')
    deptime = request.args.get('depDate')
    arrDate = request.args.get('arrDate')
    rule = request.args.get('rule')
    cx = request.args.get('cx')
    flightNo = request.args.get('flightNo')
    if re.findall('[A-Z\u4e00-\u9fa5]+', depair) and re.findall('[A-Z\u4e00-\u9fa5]+', arrair) and re.findall('\d+-\d+-\d+', deptime):
        if rule and cx and depair and arrair and deptime:
            if flightNo:
                tasks = TBCrawlerAPI.TBSpiderFlight(depair, arrair, deptime, flightNo, rule, cx).get_data()
            else:
                tasks = TBCrawlerAPI.TBSpiderAll(depair, arrair, deptime, rule, cx).get_data()
            if tasks:
                return jsonify({
                          "code": 0,
                          "msg": "success",
                          "dataTag": dataTag,
                          "extra ": "",
                          "imgBase64": "",
                          "journeys": tasks
                })
            else:
                return jsonify({
                    "code": -2,
                    "msg": "询价失败",
                    "dataTag": dataTag,
                    "error": "没有此航班（航线）信息"
                })
        else:
            return jsonify({"code": -1, 'msg': '询价失败'})

    else:
        return jsonify({"code": -1, 'msg': '询价失败'})


if __name__ == '__main__':
    app.run(debug=True, threaded=True)