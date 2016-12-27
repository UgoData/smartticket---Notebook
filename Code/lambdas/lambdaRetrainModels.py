# coding: utf-8

# ------ IMPORTS -----
import cPickle as pickle
from time import gmtime, strftime

import boto3
import pandas as pd
import re
import sklearn.metrics as m
from sklearn.model_selection import cross_val_score
from utilCsv import UnicodeWriter, Utils

from Code.Utils.utilNormalizer import Normalizer
from Code.db_access.dynamoDB import AccessDB
from tfidfClassification import Classification

# TODO : create context
a = AccessDB()
c = Classification()
n = Normalizer()
u = Utils()

# AWS Access
client = boto3.client('s3', region_name="eu-west-1")
s3 = boto3.resource('s3')
tfidfp = client.get_object(Bucket='smartticket-analytics', Key='dumpTfIdf.pkl')
tf_idf_load_from_pickle = pickle.loads(tfidfp['Body'].read())
rfp = client.get_object(Bucket='smartticket-analytics', Key='dumpRf.pkl')
rf_load_from_pickle = pickle.loads(rfp['Body'].read())

table = boto3.resource('dynamodb').Table('prod-analytics-smarttickets')
classif_result = s3.Object(bucket_name='smartticket-analytics', key='classif_results.csv')


class retrainModel:
    """
    Retrain of the model from purchease history
    """
    def __init__(self):
        self

    def db_to_df(self):
        """
        Import all the elements of a dynamodb and convert useful columns to df.
        This method do not allow to check by hand the data.
        Prefer to load csv into s3, check it and reload it from s3
        :return:
        """
        dict_db = a.get_item_from_dynamodb()
        data_df = []
        for p in dict_db:
            for line in p['lines']:
                if line['category_name_purchease'] != 'NON RECONNU':
                    data_df.append(
                        [line['category_name_purchease'], line['category_name_rmw'], line['ocr_processed_description']])
        df_res = pd.DataFrame(data_df, columns=['purchease_cat', 'rmw_cat', 'description'])
        print df_res.shape
        return df_res

    def get_classif_results_from_csv(self):
        """ return df from a csv located ni s3"""
        cat_raw_2 = classif_result.get()['Body'].read()
        line = re.split('\n', cat_raw_2)
        data = []
        for i in line:
            spl = i.split(",")
            try:
                data.append([spl[0], spl[1], spl[2]])
            except(IndexError):
                print "No split possible for :", spl
        result = pd.DataFrame(data, columns=['purchease_cat', 'rmw_cat', 'description'])
        print "Number of lines of the classification history :", result.shape[0]
        result.drop_duplicates(inplace=True)
        print "Number of UNIQUE lines of the classification history :", result.shape[0]
        return result

    def save_dynamodbresult_into_csv_s3(self):

        # get to the curren date
        date_fmt = strftime("%Y_%m_%d", gmtime())
        # Give your file path
        filepath = '/tmp/classif_results_' + date_fmt + '.csv'
        # Give your filename
        filename = 'classif_results_' + date_fmt + '.csv'

        tickets = table.scan()
        if 'Items' in tickets:
            dict_db = u.replace_decimals(tickets['Items'])
            data_df = []
            for p in dict_db:
                for line in p['lines']:
                    if line['category_name_purchease'] != 'NON RECONNU':
                        data_df.append([line['category_name_purchease'], line['category_name_rmw'],
                                        line['ocr_processed_description']])
            with open(filepath, 'wb') as myfile:
                UnicodeWriter(myfile).writerows(data_df)

            s3.Object('smartticket-analytics', filename).put(Body=open(filepath, 'rb'))
            return "CSV has been saved into S3 smartticket-analytics"
        else:
            return None

    def get_old_model_score(self, df_res):
        X_df = df_res['description'].apply(lambda x: n.end_to_end_normalize(x))
        y = df_res['purchease_cat']
        return cross_val_score(rf_load_from_pickle, tf_idf_load_from_pickle.transform(X_df), y, cv=5).mean()

    def get_score_new_model(self, df_res):
        X_df = df_res['description'].apply(lambda x: n.end_to_end_normalize(x))
        y = df_res['purchease_cat']
        vectorizer = c.tfidf_learning(X_df)
        X_vect = vectorizer.transform(X_df)
        model = c.rf_learning(X_vect, y)
        return cross_val_score(model, X_vect, y, cv=5).mean()

    def print_score_sumup(self, old_model, new_model, df_res):
        print "Previous model compare to Purchease results : %s" % old_model
        print "Retrain model compare to Purchease results : %s" % new_model
        old_results_vs_purchease_results = m.accuracy_score(df_res['purchease_cat'], df_res['rmw_cat'])
        print "Old results compare to Purchease results : %s" % old_results_vs_purchease_results

    def if_better_create_pickle(self, df_res, X_df, y):
        if self.get_old_model_score(df_res) < self.get_score_new_model(df_res):
            c.pickle_tfidf(self.tfidf_learning(X_df))
            c.pickle_rf(self.rf_learning(X_df, y, self.tfidf_learning(X_df)))
        return self

    def load_pickles_into_s3(self):
        return self


r = retrainModel()
r.db_to_df().to_csv("results_stocked_2.csv", sep=";", encoding='utf-8')
# df = r.get_classif_results_from_csv()
# old_model = r.get_old_model_score(df)
# new_model = r.get_score_new_model(df)
# r.print_score_sumup(old_model, new_model, df)
