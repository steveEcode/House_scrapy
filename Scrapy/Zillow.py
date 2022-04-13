import requests
import re
import json
import os
import urllib.parse
from Excel_Tools.GenExcels import Excel
from General_Tools.Data_Tools import orderDictColum
class ZillowScrapy():

    def __init__(self,proxy):
        self.proxy = proxy

    de_dict = {
        "house_id": "None",
        "detailUrl": "None",
        "unformattedPrice": "None",
        "address": "None",
        "addressCity": "None",
        "addressState": "None",
        "beds": "None",
        "bathrooms": "None",
        "area": "None",
        "latitude": "None",
        "longitude": "None",
        "Zipcode": "None",
        "homeStatus": "None"
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'www.zillow.com',
        'Pragma': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
    }

    def _getcoordinateData(self,zip_code):
        '''
        获取zipcode的经纬度数值,区域值
        :param zip_code:int
        :return:west,east,south,north,regionId,regionType int
        '''

        url = f"https://www.zillow.com/homes/{zip_code}_rb/"
        response = requests.get(proxies=self.proxy,headers=self.headers,verify=False,url=url)
        coordinate_json_str = re.findall(r'(?<=obileSearchPageStore" ><!--)(.+?)(?=--></script><script>)',response.text)[0]
        west = json.loads(coordinate_json_str)['queryState']['mapBounds']['west']
        east = json.loads(coordinate_json_str)['queryState']['mapBounds']['east']
        south = json.loads(coordinate_json_str)['queryState']['mapBounds']['south']
        north = json.loads(coordinate_json_str)['queryState']['mapBounds']['north']
        regionId = json.loads(coordinate_json_str)['queryState']['regionSelection'][0]['regionId']
        regionType = json.loads(coordinate_json_str)['queryState']['regionSelection'][0]['regionType']
        mapzoom = json.loads(coordinate_json_str)['defaultQueryState']['mapZoom']
        return west,east,south,north,regionId,regionType,mapzoom

    def getHouseDetail(self,zipCode,catch_type):
        '''
        :param zipCode:
        :param catch_tpye:
        :return:
        '''

        west,east,south,north,regionId,regionType,mapzoom = self._getcoordinateData(zipCode)
        if catch_type == "rent":
            parse_func = self.parseRentData
            baseData = {"pagination":{},"usersSearchTerm":f"{zipCode}","mapBounds":{"west":west,"east":east,"south":south,"north":north},"regionSelection":[{"regionId":regionId,"regionType":regionType}],"isMapVisible":True,"filterState":{"isForSaleByAgent":{"value":False},"isForSaleByOwner":{"value":False},"isNewConstruction":{"value":False},"isForSaleForeclosure":{"value":False},"isComingSoon":{"value":False},"isAuction":{"value":False},"isForRent":{"value":True},"isAllHomes":{"value":True}},"isListVisible":True,"mapZoom":mapzoom}
        elif catch_type == "isRecentlySold":
            baseData = {"pagination":{},"usersSearchTerm":f"{zipCode}","mapBounds":{"west":west,"east":east,"south":south,"north":north},"regionSelection":[{"regionId":regionId,"regionType":regionType}],"isMapVisible":True,"filterState":{"sortSelection":{"value":"globalrelevanceex"},"isForSaleByAgent":{"value":False},"isForSaleByOwner":{"value":False},"isNewConstruction":{"value":False},"isForSaleForeclosure":{"value":False},"isComingSoon":{"value":False},"isAuction":{"value":False},"isRecentlySold":{"value":True},"isAllHomes":{"value":True}},"isListVisible":True,"mapZoom":mapzoom}
            parse_func = self.parseRecentlySoldData
        elif catch_type == "forSale":
            # baseData = {"pagination":{},"mapBounds":{"west":west,"east":east,"south":south,"north":north},"isMapVisible":True,"filterState":{"isAllHomes":{"value":True},"sortSelection":{"value":"globalrelevanceex"}},"isListVisible":True,"mapZoom":mapzoom}
            baseData = {"pagination":{},"usersSearchTerm":f"{zipCode}","mapBounds":{"west":west,"east":east,"south":south,"north":north},"regionSelection":[{"regionId":regionId,"regionType":regionType}],"isMapVisible":True,"filterState":{"sortSelection":{"value":"globalrelevanceex"},"isAllHomes":{"value":True}},"isListVisible":True,"mapZoom":mapzoom}
            parse_func = self.parseSaleData

        wants = '{%22cat1%22:[%22listResults%22,%22mapResults%22]}'
        url = f"https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState={urllib.parse.quote(json.dumps(baseData))}&wants={wants}&requestId=3"
        response = requests.get(url=url,headers=self.headers,proxies=self.proxy,verify=False)

        return parse_func(raw_json=response.json(),zipCode=zipCode)

    def parseRentData(self,raw_json,zipCode):
        # result = {}
        # result['zipCode'] = zipCode

        house_list = []
        for house in raw_json['cat1']['searchResults']['listResults']:

            if 'price' not in house.keys():
                house_detail = {
                    "house_id": house['lotId'],
                    "address": house['addressStreet'],
                    "addressCity": house['addressCity'],
                    "addressState": house['addressState'],
                    "area": "None",
                    "latitude": house['latLong']['latitude'],
                    "longitude": house['latLong']['longitude'],
                    "Zipcode": zipCode,
                    "homeStatus": house['statusType']
                }
                for u in house['units']:
                    house_detail['price'] = u['price']
                    house_detail['beds'] = u['beds']
                    house_detail['bathrooms'] = 'None'
                    house_detail['detailUrl'] = f"https://www.zillow.com{house['detailUrl']}"

                    house_list.append(orderDictColum(self.de_dict,house_detail))
            else:
                price = house['price']
                detailUrl = house['detailUrl']
                house_detail = {
                        "house_id":house['id'],
                        "detailUrl":detailUrl,
                        "unformattedPrice":price,
                        "address":house['addressStreet'],
                        "addressCity":house['addressCity'],
                        "addressState":house['addressState'],
                        "beds":house['beds'],
                        "bathrooms":house['baths'],
                        "area":house['area'],
                        "latitude":"None",
                        "longitude":"None",
                        "Zipcode":zipCode,
                        "homeStatus":house['statusType']
                    }
                house_list.append(orderDictColum(self.de_dict,house_detail))
        # result['house_list'] = house_list
        return house_list

    def parseRecentlySoldData(self,raw_json,zipCode):
        house_list = []
        for house in raw_json['cat1']['searchResults']['listResults']:
            house_detail = {
                "house_id": house['id'],
                "detailUrl": house['detailUrl'],
                "unformattedPrice": house['soldPrice'],
                "address": house['address'],
                "addressCity": house['addressCity'],
                "addressState": house['addressState'],
                "beds": house['beds'],
                "bathrooms": house['baths'],
                "area": house['area'],
                "latitude": "None",
                "longitude": "None",
                "Zipcode": zipCode,
                "homeStatus": house['statusType']
            }
            house_list.append(orderDictColum(self.de_dict,house_detail))


        return house_list

    def parseSaleData(self,raw_json,zipCode):
        house_list = []
        for house in raw_json['cat1']['searchResults']['listResults']:
            print(house)
            if 'latLong' in house.keys() and 'latitude' in house['latLong'].keys():
                latitude = house['latLong']['latitude']
                longitude = house['latLong']['longitude']
            else:
                latitude = "None"
                longitude = "None"

            house_detail = {
                "house_id": house['id'],
                "detailUrl": house['detailUrl'],
                "unformattedPrice": house['price'],
                "address": house['address'],
                "addressCity": house['addressCity'],
                "addressState": house['addressState'],
                "beds": house['beds'],
                "bathrooms": house['baths'],
                "area": house['area'],
                "latitude": latitude,
                "longitude": longitude,
                "Zipcode": zipCode,
                "homeStatus": house["statusType"]
            }
            house_list.append(orderDictColum(self.de_dict,house_detail))
        return house_list

if __name__ == '__main__':
    # zip_code_list = [32009,32011,32034,32035,32041,32046,32097]
    zip_code_list = [32097]

    zs = ZillowScrapy(proxy=None)
    catch_type_list = ["forSale","rent","isRecentlySold"]

    results = []
    for catch_type in catch_type_list:
        for zip_code in zip_code_list:
            result = zs.getHouseDetail(zipCode=zip_code,catch_type=catch_type)
            results += result

    ex = Excel(r"D:\english_课程\House_scrapy\zillow.xlsx")
    ex.gen_excel(results)

    # result = []
    # for zip_code in zip_code_list:
    #     result.append(zs.getHouseDetail(zip_code,"isRecentlySold"))
    #
    # gen_excel(result)