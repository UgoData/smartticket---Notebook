import re
import unicodedata

import boto3
import pandas as pd

client = boto3.client('s3', region_name="eu-west-1")
class_client = client.get_object(Bucket='smartticket-analytics', Key='correspondance_bonsplans.csv')
cat_raw = class_client['Body'].read()


class dynamoDBPrep:
    """
    Used for Bons Plans correspondance
    From dynamoDB to Bons plans
    """
    def __init__(self):
        self

    def from_dynamo_to_mysql(self, input_json):
        # Convert json to df
        list_data = []
        for ticket in input_json:
            store_name = ticket['retailer_name']
            user_id = ticket['user_uuid']
            for line in ticket['lines']:
                cat = line['category_name_purchease']
                prod_descr = line['ocr_processed_description']
                price = line['unit_price']
                list_data.append([cat, prod_descr, store_name, user_id, price])
        df = pd.DataFrame(list_data, columns=['category', 'product_descr', 'store', 'user_id', 'price'])
        df.loc[:, 'category'] = df['category'].apply(
            lambda x: unicodedata.normalize('NFKD', x).encode('ascii', 'ignore'))
        nom_cat = self.get_bonsplans_nomencl(cat_raw)
        result = pd.merge(df, nom_cat, how='left', left_on='category', right_on='cat_name')
        # print result.head()
        return result

    def get_bonsplans_nomencl(self, cat_raw):
        """ return df from a csv located ni s3"""
        line = re.split('\n', cat_raw)
        data = []
        for i in line:
            spl = i.split(";")
            data.append([spl[0], spl[1]])
        return pd.DataFrame(data, columns=['cat_name', 'bonsplans_id'])



        # dynamoDBPrep().from_dynamo_to_mysql(AccessDB().get_item_from_dynamodb())
