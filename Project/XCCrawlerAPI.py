from urllib.parse import urlencode
import XCCrawler


class XCCrawlerAll(object):
    def __init__(self, depcity, arrcity, depdate):
        self.depcity = depcity
        self.arrcity = arrcity
        self.depdate = depdate

    def base_url(self):
        base = {
            'DCity1': self.depcity,
            'ACity1': self.arrcity,
            'DDate1': self.depdate,
            'SearchType': 'S',
            'DDate2': '',
        }
        url = 'http://flights.ctrip.com/domesticsearch/search/SearchFirstRouteFlights?'
        url = url + urlencode(base)
        return url

    def get_data(self):
        return XCCrawler.request_get_flight_number_detail(self.base_url())


class XCCrawlerFlight(object):
    def __init__(self, flightNo):
        self.flightNo = flightNo

    def resolve_flights_no_detail(self, data):
        for item in data:
            if item['flightNumber'] == self.flightNo:
                return item


if __name__ == '__main__':
    spider = XCCrawlerFlight('CKG', 'SHA', '2018-06-30', 'CA4949').get_data()
    # spider.get_data()
    print(spider)
    # print(XCCrawler.journeys)