from Code.db_access.accessRds import AccessRDS
from Code.db_access.dynamoDB import AccessDB
from Code.db_access.dynamoDBDataPrep import dynamoDBPrep

ards = AccessRDS()
ad = AccessDB()
d = dynamoDBPrep()


def handler(event, context):
    """
    Update the database bons plans with smarticket informations
    The link between users from Bons Plans and Smarticket need to be done by MTB
    :param event:
    :param context:
    :return:
    """
    # Get dynamobd data : full info TODO replace by active flow
    input_json = ad.get_item_from_dynamodb()
    result_df = d.from_dynamo_to_mysql(input_json)
    ards.getBonsPlansInfosRow(result_df)


handler('', '')
