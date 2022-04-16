from abc import abstractmethod


class Scrapy_Abstract():

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

    @abstractmethod
    def getHouse(self,*args,**kwargs):
        raise NotImplemented
