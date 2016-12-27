# coding: utf-8

# ------ IMPORTS -----
import re

import pandas as pd
import requests as r

print "INTO GOOGLE PLACE"

KEY_GOOGLE = 'AIzaSyC7xlB5DRTXXRbAdKIGzggf4xy9rFquxlY'  # key perso Antonio
PREFIX_QUERY_PLACE = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='

classif_result = pd.read_csv('data/google_types.csv', sep=';', header=None, names=['google_type', 'rmw_cat', 'bonus'])


class GoogleApi:
    def __init__(self, retailer_name, retailer_address):
        self.retailer_name = retailer_name
        self.retailer_address = retailer_address

    def get_place_infos(self):
        query = self.retailer_name + ' ' + self.retailer_address
        print 'QUERY TO GOOGLE :', query
        return r.get(PREFIX_QUERY_PLACE + query + '&key=' + KEY_GOOGLE).json()

    # def get_map_google_types(self):
    #     """ return df from a csv located in s3"""
    #     cat_raw = classif_result.get()['Body'].read()
    #     line = re.split('\n', cat_raw)
    #     data = []
    #     for i in line:
    #         spl = i.split(";")
    #         try:
    #             data.append([spl[0], spl[1], spl[2]])
    #         except(IndexError):
    #             print "No split possible for :", spl
    #     return pd.DataFrame(data, columns=['google_type', 'rmw_cat', 'bonus'])

    def get_place_type_from_google(self, query_result):
        """

        :param query_result: json result from google query
        :return: list of google types
        """
        print query_result
        return query_result['results'][0]['types']

    def get_raw_from_google(self, query_result):
        """

        :param query_result: json result from google query
        :return: list of google types
        """
        if query_result['status'] != 'ZERO_RESULTS':
            return query_result['results'][0]
        else:
            return ''

    def convert_googletypes_into_rmwtypes(self, google_list):
        """
        From google types to rmw types
        :param google_list: list of types from google
        :return: list of rmw values
        """
        # list to df
        df_google = pd.DataFrame({'google_names': google_list})
        # merge dfs
        return \
        pd.merge(df_google, classif_result, left_on='google_names', right_on='google_type', how='left')[
            'rmw_cat'].fillna('').values

    def return_only_one_category(self, list_rmw_cat, google_list):
        """
        Choosing among the list the right category.
        In case of equality, alphabetic order is taken
        :param list_rmw_cat: list with various categories
        :return: most occurent value in list, empty are not taken into account
        """
        # Suppress empty items
        list_rmw_cat_not_null = [item for item in list_rmw_cat if item != ""]
        print "List of the not null Google Cat :", list_rmw_cat_not_null
        if len(list_rmw_cat_not_null) > 0:
            # Remove food and store
            list_rmw_cat_not_food = [item for item in list_rmw_cat_not_null if item not in ['food']]
            list_rmw_cat_not_store = [item for item in list_rmw_cat_not_null if item not in ['store']]
            if (len(list_rmw_cat_not_food) > 0) and (len(list_rmw_cat_not_store) == 0):
                return "Magasin"
            list_rmw_cat_not_foodstore = [item for item in list_rmw_cat_not_null if item not in ['food', 'store']]
            if len(list_rmw_cat_not_foodstore) > 0:
                return max(set(list_rmw_cat_not_foodstore), key=list_rmw_cat_not_foodstore.count)
            else:
                return 'Magasin alimentaire spécialisé'
        elif len(list_rmw_cat) > 0:
            print "Not enought description in Google : ", google_list
            return "Magasin"
        else:
            return ''

    def google_cat_name_raw(self):
        result_google_request = self.get_place_infos()
        result_google_type = []
        if result_google_request['status'] != 'ZERO_RESULTS':
            list_cat_google = self.get_place_type_from_google(result_google_request)
            google_list_raw = self.convert_googletypes_into_rmwtypes(list_cat_google)
            cat_google = self.return_only_one_category(google_list_raw, list_cat_google)
            if cat_google != '':
                result_google_type.append(cat_google)
            else:
                print 'Google Categories are to ambiguous :', list_cat_google
        else:
            print "No results in Google Places for :", self.retailer_name + " " + self.retailer_address
        goog_res_raw = self.get_raw_from_google(result_google_request)
        return result_google_type, goog_res_raw

