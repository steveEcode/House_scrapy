import requests
import re

class Mls_scrapy():

    headers = {
        'Host': 'www.mls.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def __init__(self,transaction_type):
        '''
        transaction_type = 1 for sale transaction_type = 2 str
        :param transaction_type:
        '''
        self.transaction_type = transaction_type
        self._getGL_Key()

    def _getGL_Key(self):
        '''
        get gl ket from web and set in header
        :return:
        '''
        url = "https://www.mls.com/Listings.mvc"
        response = requests.get(url=url,headers=self.headers)
        gl_key = re.findall(r'(?<=data-gl-key=")(.+?)(?=" data-title="Real Estate Listings Search"></div>)',response.text)[0]
        self.headers["GL-KEY"] = gl_key
        return

    def _getCityDetail(self,cityName):
        url = f"https://api.globallistings.com/locations?category_id=1&transaction_type_id=1&keyword={cityName}"
        response = requests.get(url=url,headers=self.headers)
        print(response.text)
        return response.json()

    def getHouse(self,cityName):
        '''
        :param cityName:
        :return: list
        '''

        cityDetail = self._getCityDetail(cityName)
        self.getHouse_list(cityDetail,1)

    def getHouse_list(self,cityDetail,page_num):
        country_id = cityDetail['country_id']
        region_id = cityDetail['region_id']
        city_id = cityDetail['city_id']
        # location_str = cityDetail['location_str']

        api = f"https://api.globallistings.com/search?bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn={page_num}&pz=100&sort=package_id&sort_dir=desc&category_id=1&transaction_type_id={self.transaction_type}&country_id={country_id}&region_id={region_id}&city_id={city_id}&bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn=1&pz=100&sort=package_id&sort_dir=desc"
        response = requests.get(url=api,headers=self.headers)
        print(response.text)


if __name__ == '__main__':
    spider = Mls_scrapy("1")
    spider.getHouse("Yulee")