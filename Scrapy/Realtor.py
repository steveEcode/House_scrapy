from Abstract.ScrapyAbstract import Scrapy_Abstract
import requests
import time,json
from Excel_Tools.GenExcels import Excel

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
        print(response.text)
        city = response.json()['autocomplete'][0]['city']
        state_code = response.json()['autocomplete'][0]['state_code']
        lon = response.json()['autocomplete'][0]['centroid']['lon']
        lat = response.json()['autocomplete'][0]['centroid']['lat']
        return city,state_code,lon,lat

    # Overwrite
    def getHouse(self,zipCode,house_type):
        ...

    def getHouseRent(self,zipCode):
        city, state_code,lon,lat = self._getCityAndState(zipCode)
        location = f"{zipCode}, {city}, {state_code}"
        # get now date and time
        now_time = int(time.time())
        timeArray = time.localtime(now_time)
        now_date = time.strftime("%Y-%m-%d", timeArray)

        has_more = True
        offset = 0
        house_list = []
        while has_more == True:
            query_str = '\n\nfragment geoStatisticsFields on Geo {\n  geo_statistics {\n    housing_market {\n      median_rent_price\n    }\n  }\n}\n\nfragment geoStatisticsFieldsWithMarketTrends on Geo {\n  parents {\n    geo_type\n    slug_id\n    name\n  }\n  geo_statistics {\n    market_trends: housing_market {\n      active_listing_count: rental_listing_count\n      rental_listing_price: median_rent_price\n      listing_price_sqft: median_price_per_sqft\n      listing_price: median_listing_price\n      age_days: median_days_on_market\n      median_sold_price\n      month_to_month {\n        active_rental_listing_count_percent_change\n      }\n    }\n  }\n}\n\nquery ConsumerSearchQuery($query: HomeSearchCriteria!, $limit: Int, $offset: Int, $sort: [SearchAPISort], $bucket: SearchAPIBucket, $medianPriceSlug: String!) {\n  geo(slug_id: $medianPriceSlug) {\n    ...geoStatisticsFieldsWithMarketTrends\n    recommended_cities: recommended(query: {geo_search_type: city, limit: 20}) {\n      geos {\n        ... on City {\n          city\n          state_code\n          geo_type\n          slug_id\n        }\n        ...geoStatisticsFields\n      }\n    }\n    recommended_neighborhoods: recommended(query: {geo_search_type: neighborhood, limit: 20}) {\n      geos {\n        ... on Neighborhood {\n          neighborhood\n          city\n          state_code\n          geo_type\n          slug_id\n        }\n        ...geoStatisticsFields\n      }\n    }\n    recommended_counties: recommended(query: {geo_search_type: county, limit: 20}) {\n      geos {\n        ... on HomeCounty {\n          county\n          state_code\n          geo_type\n          slug_id\n        }\n        ...geoStatisticsFields\n      }\n    }\n    recommended_zips: recommended(query: {geo_search_type: postal_code, limit: 20}) {\n      geos {\n        ... on PostalCode {\n          postal_code\n          geo_type\n          slug_id\n        }\n        ...geoStatisticsFields\n      }\n    }\n  }\n  home_search: home_search(query: $query, sort: $sort, limit: $limit, offset: $offset, bucket: $bucket) {\n    costar_counts {\n      costar_total\n      non_costar_total\n    }\n    count\n    total\n    aggregation\n    results {\n      permalink\n      lead_attributes {\n        show_contact_an_agent\n      }\n      branding {\n        type\n        photo\n        name\n      }\n      price_reduced_date\n      price_reduced_amount\n      matterport\n      advertisers {\n        email\n        fulfillment_id\n        href\n        mls_set\n        name\n        nrds_id\n        office {\n          email\n          fulfillment_id\n          mls_set\n          href\n          name\n          phones {\n            ext\n            number\n            primary\n            trackable\n            type\n          }\n        }\n        phones {\n          ext\n          number\n          primary\n          trackable\n          type\n        }\n      }\n      description {\n        baths\n        baths_full\n        baths_full_calc\n        baths_half\n        baths_3qtr\n        baths_1qtr\n        beds\n        garage\n        lot_sqft\n        name\n        sqft\n        sub_type\n        type\n        year_built\n        baths_min\n        baths_max\n        beds_max\n        beds_min\n        garage_min\n        garage_max\n        sqft_max\n        sqft_min\n      }\n      flags {\n        is_pending\n        is_deal_available\n        is_for_rent\n        is_garage_present\n        is_senior_community\n        is_new_listing(days: 3)\n      }\n      href\n      last_price_change_amount\n      last_price_change_date\n      last_update_date\n      list_date\n      list_price\n      list_price_min\n      list_price_max\n      listing_id\n      location {\n        address {\n          city\n          coordinate {\n            lat\n            lon\n          }\n          country\n          line\n          postal_code\n          state\n          state_code\n          street_direction\n          street_name\n          street_number\n          street_post_direction\n          street_suffix\n          unit\n        }\n        county {\n          fips_code\n          name\n          state_code\n        }\n        search_areas {\n          city\n          state_code\n        }\n      }\n      photo_count\n      photos(limit: 3, https: true) {\n        description\n        href\n        type\n        title\n        tags {\n          label\n          probability\n        }\n      }\n      pet_policy {\n        cats\n        dogs\n        text\n      }\n      primary_photo(https: true) {\n        description\n        href\n        type\n      }\n      open_houses {\n        description\n        end_date\n        start_date\n        time_zone\n        dst\n      }\n      other_listings {\n        rdc {\n          listing_id\n          status\n          primary\n        }\n      }\n      products {\n        product_attributes\n        products\n      }\n      property_history {\n        listing {\n          photos {\n            href\n          }\n        }\n      }\n      property_id\n      source {\n        agents {\n          agent_id\n          agent_name\n        }\n        id\n        listing_id\n        community_id\n        name\n        type\n      }\n      status\n      suppression_flags\n      tags\n      when_indexed\n    }\n    top_real_estate_markets: seo_linking_modules(type: top_real_estate) {\n      title\n      top_markets: linking_module {\n        url\n        city: title\n        text: title\n      }\n    }\n    popular_searches: seo_linking_modules(type: popular_searches) {\n      title\n      linking_module {\n        title\n        url\n      }\n    }\n    property_types: seo_linking_modules(type: top_property_types) {\n      title\n      linking_module {\n        title\n        url\n      }\n    }\n  }\n}\n'
            body = {'query': query_str, 'variables': {'query': {'status': ['for_rent'], 'pending': False, 'search_location': {'location': location}, 'primary': True}, 'limit': 100, 'offset': offset, 'zohoQuery': {'property_status': 'for_rent', 'geo': {'area_type': 'postal_code', '_id': 'ps:fl_32034', '_score': 0, 'postal_code': f'{zipCode}', 'state_code': f'{state_code}', 'city': f'{city}', 'counties': [{'name': 'Nassau', 'fips': '12089', 'state_code': f'{state_code}'}], 'country': 'USA', 'centroid': {'lon': lon, 'lat': lat}, 'slug_id': f'{zipCode}', 'geo_id': '00000000-0000-0000-0000-000000000000'}, 'silo': 'search_result_page', 'location': f'{location}', 'filters': {'beds': {'min': None, 'max': None}, 'keyword': None, 'cats': False, 'dogs': False, 'threeDTours': False, 'noFees': True, 'tags': [], 'radius': None, 'nearbyAreas': [], 'move_in_date': {'min': '', 'max': ''}, 'pending': False, 'sby': {'value': '15'}, 'baths': {'min': None, 'max': None}, 'price': {'min': None, 'max': None}, 'sqft': {'min': None, 'max': None}}}, 'medianPriceSlug': f'{zipCode}', 'zoom': 12, 'resetMap': f'{now_date}T00:00:00.00000.00000000000000000', 'bucket': {'sort': 'rentalModelV1', 'sort_options': {'costar_total': 3, 'non_costar_total': 23, 'variation': 'costar_basic'}}}, 'callfrom': 'MAIN_SRP_RENTALS', 'nrQueryType': 'MAIN_SRP_RENTALS', 'user_id': None, 'cacheKey': 'MAIN_SRP_RENTALS', 'cacheParams': f'{zipCode}'}
            api = "https://www.realtor.com/rentals/api/v1/hestia?client_id=rdc-x-rental"
            response = requests.post(url=api,data=json.dumps(body),headers=self.headers)
            print(f'Geting the response offset {offset}')
            h,has_more = self.parseBySellHouseList(response,zipCode)
            house_list += h
            offset += 100
        return house_list


    def getHouseSell(self,zipCode):
        city,state_code,lon,lat = self._getCityAndState(zipCode)
        location = f"{zipCode}, {city}, {state_code}"
        # get now date and time
        now_time = int(time.time())
        timeArray = time.localtime(now_time)
        now_date = time.strftime("%Y-%m-%d", timeArray)

        has_more = True
        house_list = []
        offset = 0
        while has_more == True:

            api = "https://www.realtor.com/api/v1/hulk_main_srp?client_id=rdc-x&schema=vesta"

            body = '{\"query\":\"\\n\\nquery ConsumerSearchMainQuery($query: HomeSearchCriteria!, $limit: Int, $offset: Int, $sort: [SearchAPISort], $sort_type: SearchSortType, $client_data: JSON, $bucket: SearchAPIBucket)\\n{\\n  home_search: home_search(query: $query,\\n    sort: $sort,\\n    limit: $limit,\\n    offset: $offset,\\n    sort_type: $sort_type,\\n    client_data: $client_data,\\n    bucket: $bucket,\\n  ){\\n    count\\n    total\\n    results {\\n      property_id\\n      list_price\\n      primary_photo (https: true){\\n        href\\n      }\\n      source {\\n        id\\n        agents{\\n          office_name\\n        }\\n        type\\n        spec_id\\n        plan_id\\n      }\\n      community {\\n        property_id\\n        description {\\n          name\\n        }\\n        advertisers{\\n          office{\\n            hours\\n            phones {\\n              type\\n              number\\n            }\\n          }\\n          builder {\\n            fulfillment_id\\n          }\\n        }\\n      }\\n      products {\\n        brand_name\\n        products\\n      }\\n      listing_id\\n      matterport\\n      virtual_tours{\\n        href\\n        type\\n      }\\n      status\\n      permalink\\n      price_reduced_amount\\n      other_listings{rdc {\\n      listing_id\\n      status\\n      listing_key\\n      primary\\n    }}\\n      description{\\n        beds\\n        baths\\n        baths_full\\n        baths_half\\n        baths_1qtr\\n        baths_3qtr\\n        garage\\n        stories\\n        type\\n        sub_type\\n        lot_sqft\\n        sqft\\n        year_built\\n        sold_price\\n        sold_date\\n        name\\n      }\\n      location{\\n        street_view_url\\n        address{\\n          line\\n          postal_code\\n          state\\n          state_code\\n          city\\n          coordinate {\\n            lat\\n            lon\\n          }\\n        }\\n        county {\\n          name\\n          fips_code\\n        }\\n      }\\n      tax_record {\\n        public_record_id\\n      }\\n      lead_attributes {\\n        show_contact_an_agent\\n        opcity_lead_attributes {\\n          cashback_enabled\\n          flip_the_market_enabled\\n        }\\n        lead_type\\n      }\\n      open_houses {\\n        start_date\\n        end_date\\n        description\\n        methods\\n        time_zone\\n        dst\\n      }\\n      flags{\\n        is_coming_soon\\n        is_pending\\n        is_foreclosure\\n        is_contingent\\n        is_new_construction\\n        is_new_listing (days: 14)\\n        is_price_reduced (days: 30)\\n        is_plan\\n        is_subdivision\\n      }\\n      list_date\\n      last_update_date\\n      coming_soon_date\\n      photos(limit: 2, https: true){\\n        href\\n      }\\n      tags\\n      branding {\\n        type\\n        photo\\n        name\\n      }\\n    }\\n  }\\n}\",\"variables\":{\"query\":{\"status\":[\"for_sale\",\"ready_to_build\"],\"primary\":true,\"search_location\":{\"location\":\"' + location + '\"}},\"client_data\":{\"device_data\":{\"device_type\":\"web\"},\"user_data\":{\"last_view_timestamp\":-1}},\"limit\":100,\"offset\":' + str(offset) + ',\"zohoQuery\":{\"silo\":\"search_result_page\",\"location\":\"00000, 00000, 00\",\"property_status\":\"for_sale\",\"filters\":{}},\"sort_type\":\"relevant\",\"geoSupportedSlug\":\"' + str(zipCode) + '\",\"resetMap\":\"' + str(now_date) + 'T00:00:00.00000.0000000000000000\",\"by_prop_type\":[\"home\"]},\"operationName\":\"ConsumerSearchMainQuery\",\"callfrom\":\"SRP\",\"nrQueryType\":\"MAIN_SRP\",\"visitor_id\":\"00000000-0000-0000-0000-000000000000\",\"isClient\":true,\"seoPayload\":{\"asPath\":\"/realestateandhomes-search/32097\",\"pageType\":{\"silo\":\"search_result_page\",\"status\":\"for_sale\"},\"county_needed_for_uniq\":false}}'

            # print(json.dumps(body).replace('"',r'\"'))
            # print(urllib.parse.quote(json.dumps(body)))
            # exit()
            print(f'Geting the response offset {offset}')
            response = requests.post(headers=self.headers,data=body,url=api)
            h,has_more = self.parseBySellHouseList(response,zipCode)
            house_list += h
            offset += 100
        print(len(house_list))
        return house_list

    def parseBySellHouseList(self,response,zipCode):
        has_more = True
        if response.json()['data']['home_search']['count'] == 0:
            has_more = False
        house_list = []
        for house in response.json()['data']['home_search']['results']:
            # print(house)
            if house['location']['address']['coordinate'] == None:
                lat = "None"
                lon = "None"
            else:
                lat = house['location']['address']['coordinate']['lat']
                lon = house['location']['address']['coordinate']['lon']
            house_list.append({
                "house_id": house['property_id'],
                "detailUrl": "https://www.realtor.com/realestateandhomes-detail/" + house['permalink'],
                "unformattedPrice": house['list_price'],
                "address": house['location']['address']['line'],
                "addressCity": house['location']['address']['city'],
                "addressState": house['location']['address']['state_code'],
                "beds": house['description']['beds'],
                "bathrooms": house['description']['baths'],
                "area": house['description']['sqft'],
                "latitude": lat,
                "longitude": lon,
                "Zipcode": zipCode,
                "homeStatus": house['status']
            })
        return house_list,has_more

    def parseByRentHouseList(self,response,zipCode):
        has_more = True
        if response.json()['data']['home_search']['count'] == 0:
            has_more = False
        house_list = []
        for house in response.json()['data']['home_search']['result']:
            if house['location']['address']['coordinate'] == None:
                lat = "None"
                lon = "None"
            else:
                lat = house['location']['address']['coordinate']['lat']
                lon = house['location']['address']['coordinate']['lon']
            house_list.append({
                "house_id": house['property_id'],
                "detailUrl": "https://www.realtor.com/realestateandhomes-detail/" + house['permalink'],
                "unformattedPrice": house['list_price_max'],
                "address": house['location']['address']['line'],
                "addressCity": house['location']['address']['city'],
                "addressState": house['location']['address']['state_code'],
                "beds": house['description']['beds'],
                "bathrooms": house['description']['baths'],
                "area": house['description']['sqft'],
                "latitude": lat,
                "longitude": lon,
                "Zipcode": zipCode,
                "homeStatus": house['status']
            })



if __name__ == '__main__':
    rs = Realtor_spider()
    # rs.getHouseRent(32097)
    house_list = rs.getHouseRent(32097)
    excel = Excel(r"D:\english_课程\House_scrapy\realtor_rent.xlsx")
    excel.gen_excel(house_list)





