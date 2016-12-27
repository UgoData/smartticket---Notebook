import cPickle as pickle

import boto3
import re

from Code.Utils.utilNormalizer import Normalizer
from loadPurcheaseData import LoadPurchease

client = boto3.client('s3', region_name="eu-west-1")
pipeline = client.get_object(Bucket='smartticket-analytics', Key='dumpPipeline.pkl')
pipeline_load_from_pickle = pickle.loads(pipeline['Body'].read())


u = Normalizer()


def eventHandler(event, context):
    """
    New classification made with pipeline from purchease classification history
    :param event:
    :param context:
    :return:
    """

    l = LoadPurchease(event)
    dict_prod = {}
    for line in event['lines']:
        if line['ocr_processed_description'] != "":
            dict_prod[line['ocr_processed_description']] = u.end_to_end_normalize_noaccent(line['category_name'])
        else:
            dict_prod[line['ocr_raw_description']] = u.end_to_end_normalize_noaccent(
                    line['category_name'])
    if len(dict_prod) > 0:
        list_prod = u.from_dict_to_list(dict_prod)
        list_prod = [re.compile('[^\D]').sub('', x.lower()) for x in list_prod]
        result = pipeline_load_from_pickle.predict(list_prod)
        list_result = []
        for idx, i in enumerate(result):
            list_result.append(i)
        return u.from_two_lists_to_dict(list_prod, list_result)
    else:
        return {}



event = {
        	'status': 'finished',
        	'extraction_type': 'STRUCTURED',
        	'total': 36.14,
        	'uuid': '20161109-0959-9752-402881196-1',
        	'retailer_name': 'Carrefour',
        	'lines': [{
        			'total_price': 7.1,
        			'ocr_processed_description': 'x/ champ emince',
        			'unit_price': 3.05,
        			'ocr_raw_description': 'CHAOSSON FROIT',
        			'category_image_url': 'http://cdn1.skerou.com/images/products/skerou_created/unknown_product.png',
        			'quantity': 2,
        			'category_name': 'NON RECONNU'
        		}, {
        			'total_price': 1.59,
        			'ocr_processed_description': 'dos arabica crf',
        			'unit_price': 1.59,
        			'ocr_raw_description': 'BOUTEILLE 33CL',
        			'category_image_url': 'http://cdn1.skerou.com/images/products/skerou_created/unknown_product.png',
        			'quantity': 1,
        			'category_name': 'NON RECONNU'
        		}
        	],
        	'retailer_image_url': 'http://cdn1.skerou.com/images/retailers/carrefour.png',
        	'date': '09-11-2016 09:59',
        	'nb_products': 7,
        	'nb_recognized_products': 0,
        	'store_address': {
        		'city': 'Paris',
        		'street_number': '150',
        		'longitude': '3.234567890987654',
        		'street': 'rue du Faubourg Poissonniere',
        		'latitude': '2.2345678909876543',
        		'zip_code': '75010'
        	},
        	'light_image_url': 'http://receipts.fidmarques.com/receipts/production/21/2016/11/09/20161109-0959-9752-402881196-1/20161109-0959-9752-402881196-1_prerotated.jpg',
        	'user_uuid': '123456789'
        }
eventHandler(event, '')