import requests
from requests.exceptions import ConnectionError
from gevent import monkey
# from gevent.pywsgi import WSGIServer

monkey.patch_all(ssl=False)


def get_proxy():
    global res
    try:
        url = ''
        res = requests.get(url).json()
        if res['ret'] == 1:
            proxy = 
            proxies = {'http': 'http://'+proxy, 'https': 'https://'+proxy}
            print('获取代理成功:', res['data']['ip'])
            return proxies
        else:
            print('获取代理失败，正在重试')
            return get_proxy()
    except ConnectionError:
        print('请求代理出错，正在重试')
        return get_proxy()
    finally:
        try:
            requests.get(
                ''.format(res['data']['host']))
        except ConnectionError:
            pass
            # print('释放代理失败')
        # print('释放代理成功')


if __name__ == '__main__':

    print(requests.get('http://httpbin.org/get', proxies=get_proxy()).text)