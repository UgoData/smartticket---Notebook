import boto3

from Code.Utils.utilNormalizer import Normalizer

n = Normalizer()


class AccessDB:
    """
    Put and get items from and to a dynamo db
    """
    def __init__(self, context_execut):
        table_name = context_execut['table_name']
        self.table = boto3.resource('dynamodb').Table(table_name)

    # def __init__(self):
    #     self.table = boto3.resource('dynamodb').Table('test-analytics-smarttickets')

    def put_item_into_dynamodb(self, json_input):
        print json_input
        self.table.put_item(Item=n.replace_floats(json_input['smartticket']))
        return "Item {} saved into db", json_input['smartticket']['uuid']

    def get_item_from_dynamodb(self):
        tickets = self.table.scan()
        print tickets
        if 'Items' in tickets:
            return n.replace_decimals(tickets['Items'])
        else:
            return None
