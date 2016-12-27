import hashlib
import logging
import sys

import pymysql

import rds_config

# rds settings
rds_host = "52.31.201.94"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name,
                           passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")


class AccessRDS:
    """ Access the data stored into the bons plans database.
    For link with project Bons Plans"""
    def __init__(self):
        self

    def getBonsPlansInfosRow(self, input):
        """
        This function fetches content from mysql RDS instance
        """
        for i in range(input.shape[0]):
            if input.loc[i, 'user_id'] == 'mtb2':
                id_bp = input.loc[i, 'bonsplans_id']
                cat = "[" + str(input.loc[i, 'bonsplans_id']) + "]"
                offre_descr = input.loc[i, 'product_descr']
                user_id = input.loc[i, 'user_id']
                price = input.loc[i, 'price']
                retailer = input.loc[i, 'store']
                prod_id = hashlib.sha224(offre_descr).hexdigest()

                with conn.cursor() as cur:
                    str_insert = 'insert into userbonsplans (analytics_category, burned, offreDesc, offreLib, userId, prix, prix_unitOff, description, source, id)' \
                                 ' values("%(cat)s", 1, "%(offre_descr)s", " ", "%(user_id)s", %(price)f, %(price)f, "SmartTicket", "%(retailer)s", "%(prod_id)s")' % vars()
                    cur.execute(str_insert)
                    conn.commit()

# AccessRDS().getBonsPlansInfosRow('')
