from Abstract.ScrapyAbstract import Scrapy_Abstract
import requests
import json
import time

class Realtor_spider(Scrapy_Abstract):

    headers = {
        'Host': 'www.realtor.com',
        'Connection': 'keep-alive',
        'Content-Length': '3578',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Origin': 'https://www.realtor.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.realtor.com/realestateandhomes-search/32097',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def __init__(self,proxy=None):
        self.proxy = proxy

    def _getCityAndState(self,zipCode):
        '''
        :param zipCode:
        :return: city state_code ==> string
        '''
        api = f"https://parser-external.geo.moveaws.com/suggest?client_id=rdc-x&input={zipCode}&area_types=state%2Ccity%2Ccounty%2Cpostal_code%2Caddress%2Cstreet%2Cneighborhood%2Cschool%2Cschool_district%2Cuniversity%2Cpark%2Cmlsid&limit=1"
        response = requests.get(url=api,headers=self.headers,proxies=self.proxy)
        city = response .json()['autocomplete']['city']
        state_code = response .json()['autocomplete']['state_code']
        return city,state_code

    # Overwrite
    def getHouse(self,zipCode):
        city,state_code = self._getCityAndState(zipCode)
        location = f"{zipCode}, {city}, {state_code}"
        now_time = ...
        query_str = r'''\n\nquery ConsumerSearchMainQuery($query: HomeSearchCriteria!, $limit: Int, $offset: Int, $sort: [SearchAPISort], $sort_type: SearchSortType, $client_data: JSON, $bucket: SearchAPIBucket)\n{\n  home_search: home_search(query: $query,\n    sort: $sort,\n    limit: $limit,\n    offset: $offset,\n    sort_type: $sort_type,\n    client_data: $client_data,\n    bucket: $bucket,\n  ){\n    count\n    total\n    results {\n      property_id\n      list_price\n      primary_photo (https: true){\n        href\n      }\n      source {\n        id\n        agents{\n          office_name\n        }\n        type\n        spec_id\n        plan_id\n      }\n      community {\n        property_id\n        description {\n          name\n        }\n        advertisers{\n          office{\n            hours\n            phones {\n              type\n              number\n            }\n          }\n          builder {\n            fulfillment_id\n          }\n        }\n      }\n      products {\n        brand_name\n        products\n      }\n      listing_id\n      matterport\n      virtual_tours{\n        href\n        type\n      }\n      status\n      permalink\n      price_reduced_amount\n      other_listings{rdc {\n      listing_id\n      status\n      listing_key\n      primary\n    }}\n      description{\n        beds\n        baths\n        baths_full\n        baths_half\n        baths_1qtr\n        baths_3qtr\n        garage\n        stories\n        type\n        sub_type\n        lot_sqft\n        sqft\n        year_built\n        sold_price\n        sold_date\n        name\n      }\n      location{\n        street_view_url\n        address{\n          line\n          postal_code\n          state\n          state_code\n          city\n          coordinate {\n            lat\n            lon\n          }\n        }\n        county {\n          name\n          fips_code\n        }\n      }\n      tax_record {\n        public_record_id\n      }\n      lead_attributes {\n        show_contact_an_agent\n        opcity_lead_attributes {\n          cashback_enabled\n          flip_the_market_enabled\n        }\n        lead_type\n      }\n      open_houses {\n        start_date\n        end_date\n        description\n        methods\n        time_zone\n        dst\n      }\n      flags{\n        is_coming_soon\n        is_pending\n        is_foreclosure\n        is_contingent\n        is_new_construction\n        is_new_listing (days: 14)\n        is_price_reduced (days: 30)\n        is_plan\n        is_subdivision\n      }\n      list_date\n      last_update_date\n      coming_soon_date\n      photos(limit: 2, https: true){\n        href\n      }\n      tags\n      branding {\n        type\n        photo\n        name\n      }\n    }\n  }\n}'''
        api = "https://www.realtor.com/api/v1/hulk_main_srp?client_id=rdc-x&schema=vesta"
        body = {
                "query":query_str,
                "variables":{
                    "query":{
                        "status":[
                            "for_sale",
                            "ready_to_build"
                        ],
                        "primary":True,
                        "search_location":{
                            "location":location
                        }
                    },
                    "client_data":{
                        "device_data":{
                            "device_type":"web"
                        },
                        "user_data":{
                            "last_view_timestamp":-1
                        }
                    },
                    "limit":42,
                    "offset":0,
                    "zohoQuery":{
                        "silo":"search_result_page",
                        "location":location,
                        "property_status":"for_sale",
                        "filters":{

                        }
                    },
                    "sort_type":"relevant",
                    "geoSupportedSlug":f"{zipCode}",
                    "resetMap":"2022-04-16T00:00:00.00000.0000000000000000",
                    "by_prop_type":[
                        "home"
                    ]
                },
                "operationName":"ConsumerSearchMainQuery",
                "callfrom":"SRP",
                "nrQueryType":"MAIN_SRP",
                "visitor_id":"00000000-0000-0000-0000-000000000000",
                "isClient":True,
                "seoPayload":{
                    "asPath":"/realestateandhomes-search/32097",
                    "pageType":{
                        "silo":"search_result_page",
                        "status":"for_sale"
                    },
                    "county_needed_for_uniq":False
                }
            }
        ...

if __name__ == '__main__':
    rs = Realtor_spider()
    rs._getCityAndState(32097)





