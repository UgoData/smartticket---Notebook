# -*- coding: utf-8 -*-
import cPickle as pickle
import sys

import pandas as pd

from Code.Utils.utilNormalizer import Normalizer
from Code.raw_treatments.googlePlaces import GoogleApi
from Code.db_access.dynamoDB import AccessDB
from loadPurcheaseData import LoadPurchease
from tfidfClassification import Classification

reload(sys)
sys.setdefaultencoding('utf8')

c = Classification()
n = Normalizer()
# TODO : create context
a = AccessDB()
l = LoadPurchease({'est': 'fdsfg'})

LIST_TO_PREDICT = [
    'CHOCO', 'TOURNESOL MOZZARELLA', 'CHAUSSON FRUIT',
    '6X XTREME3 P SENSI', 'TOMATE CERISE', 'POIRE',
    'X72 LINGET EAU NET', 'Bianco, boisson aromatisée blanc',
    # Ticket Franprix
    'BOUTEILL 33CL J', 'PICK UP LAIT X',
    # Ticket Auchan
    'LOTUS CONFORT PAPIER TOILE', 'POUCE VINAIGRE ALCOOL BLAN', 'FOXY ESSUIE TOUT ABSO BLAN',
    'PETIT NAVIRE THON NATUREL',
    'HIPP BIO RISOTTO POULET', 'CYRIO VINAIGRE BALSAMIQUE',
    'STEAK HACHE', 'ENTRECOTE',
    'HERTA LARDONS FUMES'
]

EXPECTED_RESULT = [
    'epicerie_sucree', 'produits_laitiers_lait_oeufs', 'epicerie_sucree',
    'hygiene_beaute', 'legumes', 'fruits',
    'hygiene_beaute', 'boissons',
    'boissons', 'epicerie_sucree',
    'hygiene_beaute', 'epicerie_salee',
    'hygiene_beaute', 'poissonnerie',
    'epicerie_salee', 'epicerie_salee',
    'viande', 'viande',
    'viande'
]

BOISSONS_KEYWORDS = ['BOUTEIL', 'PERRIER', 'PELLEGRINO', 'QUEZAC', 'PJ', 'JUS', 'VITTEL', 'BOISS', 'EAU', 'VIN ',
                     'RHUM', 'WHISKY', 'CAFE', 'THE', 'COCA']


def test_classification_via_apprentissage():
    #### Test classification via apprentissage
    X_df, y = c.load_data()

    vectorizer = c.tfidf_learning(X_df)
    X_vect = vectorizer.transform(X_df)

    model = c.rf_learning(X_vect, y)

    list_pred = [n.end_to_end_normalize(x) for x in LIST_TO_PREDICT]
    print list_pred
    result_classif = model.predict(vectorizer.transform(list_pred))
    list_result = []
    for idx, i in enumerate(result_classif):
        print i
        print LIST_TO_PREDICT[idx]
        if any(word.lower() in LIST_TO_PREDICT[idx].lower() for word in BOISSONS_KEYWORDS):
            list_result.append('boissons')
        else:
            list_result.append(i)
    return list_result


def print_result(model_result):
    result_precision = 1
    len_res = len(model_result)
    for idx, res in enumerate(model_result):
        if EXPECTED_RESULT[idx] != res:
            to_print = {'val': LIST_TO_PREDICT[idx], 'res': res, 'exp': EXPECTED_RESULT[idx]}
            print 'pb with **%(val)s**: our model predict : **%(res)s** instead of **%(exp)s**' % to_print
            result_precision -= 1 / float(len_res)
    print 'total precision : ', result_precision


def check_vectorizer(X_df, y, model):

    vectorizer = c.tfidf_learning(X_df)
    vocab = vectorizer.vocabulary_
    idf = vectorizer.idf_
    dense = vectorizer.transform(X_df).todense()
    df_tiidf = pd.DataFrame(dense, columns=[x for (x, z) in sorted(vocab.items(), key=lambda (k, v): v)])
    df_tiidf['categories'] = y
    dict_res = {}
    for cat_name in df_tiidf['categories'].unique():
        print cat_name
        df_temp = df_tiidf[df_tiidf['categories'] == cat_name]
        list_col = []
        for col in df_temp.columns:
            if df_temp['col'].sum() > 0:
                list_col.append(col)
        dict_res[cat_name] = list_col
    print dict_res
    print dict(zip(vectorizer.get_feature_names(), idf))

    c.get_features_importance(model, vectorizer.transform(X_df), vocab)


def test_classification_via_pickle():
    #### Test CLassification

    # Load TF-IDF
    tf_idf_load_from_pickle = pickle.load(open("../models/dumpTfIdf.pkl", "rb"))
    # Load Random Forest
    rf_load_from_pickle = pickle.load(open("../models/dumpRf.pkl", "rb"))

    return c.tfidf_rf_classif_apply(tf_idf_load_from_pickle, rf_load_from_pickle,
                                    [n.end_to_end_normalize(x) for x in LIST_TO_PREDICT])


def test_google_api():
    #### Test Google API
    first_line, second_line = 'B.8OVY2', '5 AVENUE TRUDAINE'
    g = GoogleApi(first_line, second_line)
    print g.google_cat()


def create_pickles():
    X_df, y = c.load_data()
    c.save_pickles(X_df, y)


def get_dynamodb_data():
    print a.get_item_from_dynamodb()


def get_csv_from_s3():
    print l.get_categories_name_from_csv()


# print_result(test_classification_via_apprentissage())

# create_pickles()

# get_dynamodb_data()

# get_csv_from_s3()

test_google_api()
