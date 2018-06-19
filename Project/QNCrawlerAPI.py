# -*- coding:utf-8 -*-
import QNCrawler


class QNSpiderAll(object):
    def __init__(self, depcity, arrcity, depdate, rule):
        self.depcity = depcity
        self.arrcity = arrcity
        self.depdate = depdate
        self.rule = rule
        QNCrawler.QNTGQ_LEVEL = self.rule

    def base_url(self):
        url = QNCrawler.base_url(dcity=self.depcity, acity=self.arrcity, ddate=self.depdate)
        return url

    def get_data(self):
        QNCrawler.request_get_flight_number(self.base_url())
        return QNCrawler.journeys


class QNSpiderFlight(object):
    def __init__(self, depcity, arrcity, depdate, aircode, rule):
        self.depcity = depcity
        self.arrcity = arrcity
        self.depdate = depdate
        self.aircode = aircode
        self.rule = rule

    def base_url(self):
        url = QNCrawler.base_url(dcity=self.depcity, acity=self.arrcity, ddate=self.depdate, code=self.aircode)
        return url

    def get_data(self):
        QNCrawler.QNTGQ_LEVEL = self.rule
        QNCrawler.request_get_flight_number_detail(self.base_url())
        return QNCrawler.journeys


if __name__ == '__main__':
    spider = QNSpiderFlight('重庆', '上海', '2018-06-22', 'HO3772')
    spider.get_data()
    print(QNCrawler.journeys)
