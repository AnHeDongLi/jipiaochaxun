import TBCrawler


class TBSpiderAll(object):
    def __init__(self, depcity, arrcity, depdate, rule_tag, gd_tag):
        self.depcity = depcity
        self.arrcity = arrcity
        self.depdate = depdate
        self.rule_tag = rule_tag
        self.gd_tag = gd_tag
        TBCrawler.TBTGQ_LEVEL = self.rule_tag
        TBCrawler.TBCX_LEVEL = self.gd_tag

    def base_url(self):
        url = TBCrawler.base_url(depcity=self.depcity, arrcity=self.arrcity, depdate=self.depdate)
        return url

    def get_data(self):
        TBCrawler.request_get_flight_number(self.base_url())
        return TBCrawler.journeys


class TBSpiderFlight(object):
    def __init__(self, depcity, arrcity, depdate, aircode, rule_tag, gd_tag):
        self.depcity = depcity
        self.arrcity = arrcity
        self.depdate = depdate
        self.aircode = aircode
        self.rule_tag = rule_tag
        self.gd_tag = gd_tag
        TBCrawler.TBTGQ_LEVEL = self.rule_tag
        TBCrawler.TBCX_LEVEL = self.gd_tag

    def base_url(self):
        url = TBCrawler.base_url(depcity=self.depcity, arrcity=self.arrcity, depdate=self.depdate, flightno=self.aircode)
        return url

    def get_data(self):
        TBCrawler.request_get_flight_number_detail(self.base_url())
        return TBCrawler.journeys


if __name__ == '__main__':
    spider = TBSpiderFlight('重庆', '北京', '2018-06-22', 'SC1155', 1, 1)
    spider.get_data()
    print(TBCrawler.journeys)