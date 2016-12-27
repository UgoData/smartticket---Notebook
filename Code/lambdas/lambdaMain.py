# coding=utf-8
import json

import boto3
import warnings

from Code.Utils.utilNormalizer import Normalizer
from Code.db_access.dynamoDB import AccessDB
from loadAndCleanData import LoadCleanData
from loadPurcheaseData import LoadPurchease
from processTextData import ProcessText

warnings.filterwarnings("ignore")

print "INTO LAMBDA"

# Load python files
p = ProcessText()
l = LoadCleanData()
u = Normalizer()


# Load data for test
# event = json.load(open("../data/smart-tickets-payload-example.json", "rb"))


# print input

lambda_client = boto3.client('lambda', region_name="eu-west-1")

def eventHandler(event, context):
    """
    Main lambda for our classification.
    It invokes lambda enrich location as a first step.
    Case RAW : only add lcoation and google place type if finded
    Case Structured : send Purchease classification, our classif is only used if Purchease send Non-Reconnu
    :param event: json input send by Purchease
    :param context: non need
    :return: output json to be send to Purchease
    """
    print "event init :", event
    d = AccessDB(event['stageVariables'])

    event_bytes = json.dumps(event['body'])
    function_name = event['stageVariables']['stage'] + '-' + "smartticket-location"
    invoke_response = lambda_client.invoke(FunctionName=function_name,
                                           InvocationType='RequestResponse',
                                           Payload=event_bytes)
    new_event = invoke_response['Payload'].read()
    print "New event : ", new_event
    new_event_smartt = json.loads(new_event)['smartticket']
    new_event_smartt = replace_empty_string(new_event_smartt)

    if new_event_smartt['extraction_type'] == 'STRUCTURED':
        ll = LoadPurchease(new_event_smartt)
        output_full = ll.fill_input_with_classif(new_event_smartt)
        # Save into db
        d.put_item_into_dynamodb(output_full)
        # Clean output for send into post : del purchease_cat and rmw_cat, only stay cat
        return respond('', ll.good_shape_output_for_post(output_full))
    else:
        return respond('', new_event)


def respond(err, res=None):
    return {
        'statusCode': '404' if err else '200',
        'body': json.dumps(err) if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def replace_empty_string(obj):
    if isinstance(obj, list):
        for i in xrange(len(obj)):
            obj[i] = replace_empty_string(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.iterkeys():
            obj[k] = replace_empty_string(obj[k])
        return obj
    elif isinstance(obj, (str, unicode)):
        print(obj)
        if not obj:
            return None
        else:
            return obj
    else:
        return obj
