# coding: utf-8

""" Add classification to purchease json if necessarly"""

# ------ IMPORTS -----
import cPickle as pickle
import json

import pandas as pd
import re
import warnings
warnings.filterwarnings("ignore")

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilNormalizer import Normalizer
from tfidfClassification import Classification

print "INTO load purchease"

# Load Pickle
tf_idf_load_from_pickle = pickle.load(open( "models/dumpTfIdf.pkl", "rb" ))
rf_load_from_pickle = pickle.load(open( "models/dumpRf.pkl", "rb" ))
pipeline_load_from_pickle = pickle.load(open( "models/dumpPipeline.pkl", "rb" ))
cat_raw_2 = pd.read_csv('data/categories.csv', sep=';', header=None, names=['name_rmw', 'name_purchease', 'img'])


BOISSONS_KEYWORDS = ['BOUTEIL', 'PERRIER', 'PELLEGRINO', 'QUEZAC', 'PJ', 'JUS', 'VITTEL', 'BOISS', 'EAU', 'VIN ',
                     'RHUM', 'WHISKY', 'CAFE', 'THE', 'COCA'] # not uses anymore


class LoadPurchease:
    def __init__(self, input_json):
        self.input_json = input_json

    def extract_description(self, input_json):
        """
        Extraction of the description of the products.
        If ocr processed is not empty then it is a key else we use ocr raw
        :param input: json input from purchease
        :return: dictionary with key equals to production description
        """

        u = Normalizer()
        dict_description = {}
        for line in input_json['lines']:
            if line['ocr_processed_description'] != "":
                dict_description[line['ocr_processed_description']] = u.end_to_end_normalize_noaccent(
                    line['category_name'])
            else:
                dict_description[line['ocr_raw_description']] = u.end_to_end_normalize_noaccent(line['category_name'])
        return dict_description

    def classification_homemade(self, input_json):
        """
        Classify the products description into a dictionary.
        The boissons classification is made by hand.
        Not Boissons in learning stage.
        :return: dictionary key: description value : rmw category
        """
        u = Normalizer()
        dict_prod = self.extract_description(input_json)

        if len(dict_prod) > 0:
            list_prod = u.from_dict_to_list(dict_prod)
            t = Classification()
            result = t.tfidf_rf_classif_apply(tf_idf_load_from_pickle, rf_load_from_pickle, list_prod)
            list_result = []
            for idx, i in enumerate(result):
                print i
                print list_prod[idx]
                if any(word.lower() in list_prod[idx].lower() for word in BOISSONS_KEYWORDS):
                    list_result.append('boissons')
                else:
                    list_result.append(i)
            return u.from_two_lists_to_dict(list_prod, list_result)
        else:
            return {}

    def classification_homemade_v2(self, input_json):
        """
        Classify the products description into a dictionary.
        From the first 5000 classifications of Purchease, we retrain the model
        :return: dictionary key: description value : rmw category
        """
        u = Normalizer()
        dict_prod = self.extract_description(input_json)

        if len(dict_prod) > 0:
            list_prod = u.from_dict_to_list(dict_prod)
            list_prod_2 = [re.compile('[^\D]').sub('', x.lower()) for x in list_prod]
            result = pipeline_load_from_pickle.predict(list_prod_2)
            list_result = []
            for idx, i in enumerate(result):
                list_result.append(i)
            return u.from_two_lists_to_dict(list_prod, list_result)
        else:
            return {}

    def fill_input_with_classif(self, input_json):
        """
        Create a json with purchease classification and rmw classification
        :param input_json: json from purchease classification
        :return:
        """
        dict_class = self.classification_homemade_v2(input_json)
        output = {'analytics_result': 'FAILURE', 'smartticket': input_json}
        df_classification = cat_raw_2
        print 'intitulé', 'rmw_classif', 'purchease_classif'
        if dict_class != {}:
            for line in input_json['lines']:
                # Creation of a purchease category
                line['category_name_purchease'] = line['category_name']
                # Creation of a rmw category
                if (line['ocr_processed_description'] != ""):
                    print line['ocr_processed_description'],'|', dict_class[line['ocr_processed_description']],'|', line['category_name']
                    # line['category_name_rmw'] = self.from_rmwname_to_purcheaseinfos(df_classification, dict_class[
                    #     line['ocr_processed_description']], 'name_rmw', 'name_purchease')
                    line['category_name_rmw'] = dict_class[line['ocr_processed_description']]
                else:
                    print line['ocr_raw_description'],'|', dict_class[line['ocr_raw_description']],'|', line['category_name']
                    line['category_name_rmw'] = dict_class[line['ocr_raw_description']]
                if (line['category_name'] == 'NON RECONNU') and (line['category_name'] <> line['category_name_rmw']):
                    output['analytics_result'] = 'SUCCESS'
                    line['category_name'] = line['category_name_rmw']
                    line['category_image_url'] = self.from_rmwname_to_purcheaseinfos(df_classification,
                                                                                     line['category_name_rmw'],
                                                                                     'name_purchease', 'img')
                    # TODO : change category_image_url too
        return output

    def good_shape_output_for_post(self, input_json):
        u = Normalizer()
        output = input_json.copy()
        for line in output['smartticket']['lines']:
            del line['category_name_purchease']
            del line['category_name_rmw']
        output = u.replace_decimals(output)
        return json.dumps(output)

    def get_categories_name_from_csv(self, cat_raw_2):
        """ return df from a csv located ni s3"""
        line = re.split('\n', cat_raw_2)
        data = []
        for i in line:
            spl = i.split(";")
            data.append([spl[0], spl[1], spl[2]])
        return pd.DataFrame(data, columns=['name_rmw', 'name_purchease', 'img'])

    def from_rmwname_to_purcheaseinfos(self, df, rmw_name, col_to_check, col_to_get):
        return df.loc[df[col_to_check] == rmw_name][col_to_get].iloc[0]

        # l = LoadPurchease(input)
        # print l.fill_input_with_classif()
