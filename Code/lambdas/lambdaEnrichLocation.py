# coding: utf-8

# ------ IMPORTS -----
import json
import warnings
warnings.filterwarnings("ignore")

print "INTO LAMBDA ENRICH LOCATION PLACE"

class EnrichLocation:
    def __init__(self):
        self

    def enrich_location(self, event):
        """
        Add location informations for RAW json inputs. If also get the google palce types and create a line if success to match
        :param event: json input send by Purchease
        :param context: no need
        :return: enrich smarticket
        """
        r = RawTreatment()
        event = json.loads(event)

        if event['extraction_type'] == 'RAW':
            result = r.create_output(event)
            return result
        else:
            return {'smartticket': event, 'analytics_result': 'FAILURE'}