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
        return response.json()

    def getHouse(self,cityName):
        '''
        :param cityName:
        :return: list
        '''

        cityDetail = self._getCityDetail(cityName)
        result = []
        page_num = 1
        while True:
            house_list,has_more = self.getHouse_list(cityDetail,page_num)
            result += house_list
            if has_more == False:
                break
            else:
                page_num += 1
        return result

    def getHouse_list(self,cityDetail,page_num):
        country_id = cityDetail[0]['country_id']
        region_id = cityDetail[0]['region_id']
        city_id = cityDetail[0]['city_id']

        # location_str = cityDetail['location_str']
        # api = f"https://api.globallistings.com/search?bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn={page_num}&pz=100&sort=package_id&sort_dir=desc&category_id=1&transaction_type_id={self.transaction_type}&country_id={country_id}&region_id={region_id}&city_id={city_id}&bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn=1&pz=100&sort=package_id&sort_dir=desc"
        # api = f"https://api.globallistings.com/search?category_id=1&transaction_type_id={self.transaction_type}&country_id={country_id}&region_id={region_id}&city_id={city_id}&bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn=1&pz=100&sort=package_id&sort_dir=desc&category_id=1&transaction_type_id={self.transaction_type}&country_id={country_id}&region_id={region_id}&city_id={city_id}&bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn=1&pz=100&sort=package_id&sort_dir=desc"
        api = f"https://api.globallistings.com/search?category_id=1&transaction_type_id={self.transaction_type}&country_id={country_id}&region_id={region_id}&city_id={city_id}&bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn=1&pz=36&sort=package_id&sort_dir=desc&category_id=1&transaction_type_id={self.transaction_type}&country_id={country_id}&region_id={region_id}&city_id={city_id}&bedrooms=&bathrooms=&min_price=&max_price=&min_size=&max_size=&size_unit=&commercial_lease_type=&residential_lease_type=&keywords=&pn=1&pz=36&sort=package_id&sort_dir=desc"
        response = requests.get(url=api,headers=self.headers)
        return self.parseHouseData(response,page_num)

    def parseHouseData(self,response,page_num):
        '''
        :param response:
        :return: house_list,has_more
        '''
        if len(response.text) == 0:
           return [], False

        total_page = int(response.json()['meta']['page_number'])
        if page_num < total_page:
            has_more = True
        else:
            has_more = False

        addressCity = response.json()['meta']['city_name']
        house_list = []
        if self.transaction_type == "1":
            home_status = "for sale"
        elif self.transaction_type == "2":
            home_status = "for rent"

        for house in response.json()['listings']:
            if self.transaction_type == "1":
                unformattedPrice = house['soldPrice']
            elif self.transaction_type == "2":
                unformattedPrice = house['price']
            house_list.append(
                {
                    "house_id":house['listing_id'],
                    "detailUrl":'https://www.mls.com/Listings.mvc?lid=' + house['listing_id'],
                    "unformattedPrice":unformattedPrice,
                    "address":house['street_address'],
                    "addressCity":addressCity,
                    "addressState":house['location'],
                    "beds":house['bedrooms'],
                    "bathrooms":house['bathrooms'],
                    "area":"Unknown",
                    "latitude":house['latitude'],
                    "longitude":house['longitude'],
                    "Zipcode":"None",
                    "homeStatus":home_status
                }
            )

        return house_list,has_more

if __name__ == '__main__':
    from Excel_Tools.GenExcels import Excel
    city_list = ["Bryceville","Callahan","Yulee","Hilliard","Fernandina Beach"]
    house_type_list = ["1","2"]
    houses = []


    for house_type in house_type_list:
        spider = Mls_scrapy(house_type)
        for city in city_list:
            houses += spider.getHouse(city)

    csv_path = r'D:\english_课程\demo.xlsx'
    Excel(csv_path).gen_excel(houses)