from Abstract.ScrapyAbstract import Scrapy_Abstract
from Excel_Tools.GenExcels import Excel
import requests

class HomeFinder_Scrapy(Scrapy_Abstract):

    # Overwrite
    def getHouse(self,zipCode,homeStatus):
        if homeStatus == "for-sale":
            parse_func = self.parseSaleHouseList
        elif homeStatus == "rentals":
            parse_func = self.parseRentHouseList

        page_num = 1
        has_more = True
        house_list = []
        while has_more:
            api = f"https://api.homefinder.com/v1/listing?scope={homeStatus}&term={zipCode}&area=%7B%22zip%22:%22{zipCode}%22%7D&page={page_num}"
            response = requests.get(url=api,verify=False)
            new_house_list,has_more = parse_func(response,zipCode,homeStatus)
            house_list += new_house_list
            print(f"Zipcode {zipCode} {homeStatus} {page_num}")
            page_num += 1
        return house_list

    def parseSaleHouseList(self,response,zipCode,homeStatus):
        '''
        :return: house_list,has_more
        '''
        print(response.text)
        if response.json()['meta']['page'] >= response.json()['meta']['pages']:
            has_more = False
        else:
            has_more = True

        house_list = []
        for house in response.json()['listings']:
            house_list.append(
                {
                    "house_id": house['id'],
                    "detailUrl": "https://homefinder.com/property/" + str(house['id']) + "/" + house['addressLine1'].replace(" ","-") + f"-{zipCode}",
                    "unformattedPrice": house["price"],
                    "address": house['addressLine1'],
                    "addressCity": house["city"],
                    "addressState": house["state"],
                    "beds": house["bed"],
                    "bathrooms": house["bath"],
                    "area": house["squareFootage"],
                    "latitude": "None",
                    "longitude": "None",
                    "Zipcode": zipCode,
                    "homeStatus": homeStatus
                }
            )
        return house_list,has_more

    def parseRentHouseList(self,response,zipCode,homeStatus):
        print(response.text)
        if response.json()['meta']['page'] >= response.json()['meta']['pages']:
            has_more = False
        else:
            has_more = True

        house_list = []
        for house in response.json()['listings']:
            house_list.append(
                {
                    "house_id": house['id'],
                    "detailUrl": "https://homefinder.com/property/" + str(house['id']) + "/" + house[
                    'addressLine1'].replace(" ", "-") + f"-{zipCode}",
                    "unformattedPrice": house["price"],
                    "address": house['addressLine1'],
                    "addressCity": house["city"],
                    "addressState": house["state"],
                    "beds": house["bed"],
                    "bathrooms": house["bath"],
                    "area": house["squareFootage"],
                    "latitude": house["latitude"],
                    "longitude": house["longitude"],
                    "Zipcode": zipCode,
                    "homeStatus": homeStatus
                }
            )
        return house_list, has_more



if __name__ == '__main__':
    zipCode_list = [32009, 32011, 32034, 32035, 32041, 32046, 32097]
    house_status_list = ['for-sale','rentals']

    house_list = []
    for zipCode in zipCode_list:
        for house_status in house_status_list:
            spider = HomeFinder_Scrapy()
            house_list += spider.getHouse(str(zipCode),house_status)

    ex = Excel(r"D:\english_课程\House_scrapy\HomeFinder.xlsx")
    ex.gen_excel(house_list)
