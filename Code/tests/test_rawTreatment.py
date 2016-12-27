from unittest import TestCase

from Code.raw_treatments.rawTreatment import RawTreatment

event = {
    'status': 'finished',
    'extraction_type': 'RAW',
    'store_address': {
        'city': None,
        'street_number': None,
        'longitude': None,
        'street': None,
        'latitude': None,
        'zip_code': None
    },
    'uuid': '20161202-1324-5257-72351',
    'light_image_url': 'http://receipts.fidmarques.com/receipts/production/21/2016/12/02/20161202-1324-5257-72351-1/20161202-1324-5257-72351-1_prerotated.jpg',
    'retailer_name': 'Inconnu',
    'lines': [{
        'total_price': None,
        'ocr_processed_description': '01.49.35.88.70',
        'unit_price': None,
        'ocr_raw_description': None,
        'category_image_url': 'http://cdn1.skerou.com/images/products/skerou_created/unknown_product.png',
        'category_name': 'NON RECONNU',
        'quantity': None
    }, {
        'total_price': None,
        'ocr_processed_description': 'SAV 01.75.62.26.04',
        'unit_price': None,
        'ocr_raw_description': None,
        'category_image_url': 'http://cdn1.skerou.com/images/products/skerou_created/unknown_product.png',
        'category_name': 'NON RECONNU',
        'quantity': None
    }, {
        'total_price': None,
        'ocr_processed_description': "N'SIREN:345197552",
        'unit_price': None,
        'ocr_raw_description': None,
        'category_image_url': 'http://cdn1.skerou.com/images/products/skerou_created/unknown_product.png',
        'category_name': 'NON RECONNU',
        'quantity': None
    }, {
        'total_price': None,
        'ocr_processed_description': '**SHEXSHEUS*S***',
        'unit_price': None,
        'ocr_raw_description': None,
        'category_image_url': 'http://cdn1.skerou.com/images/products/skerou_created/unknown_product.png',
        'category_name': 'NON RECONNU',
        'quantity': None
    }
    ],
    'retailer_image_url': 'http://cdn1.skerou.com/images/retailers/inconnu.png',
    'nb_recognized_products': 0,
    'nb_products': 0,
    'date': '02-12-2016 13:24',
    'total': 65.98,
    'user_uuid': 'mtb8@mtb.com'
}

r = RawTreatment()


class TestRawTreatment(TestCase):
    def test_extract_first_lines(self, event):
        self.assertEqual(r.extract_first_lines(), ['01.49.35.88.70', 'SAV 01.75.62.26.04'])

    def test_extract_phone_number(self):
        # Normal phone number
        line_descr = '01.49.35.88.70'
        self.assertEqual(r.extract_phone_number(line_descr), '01.49.35.88.70')
        # Normal phone number
        line_descr = '0149358870'
        self.assertEqual(r.extract_phone_number(line_descr), '01.49.35.88.70')
        # TEL
        line_descr = 'TEL : 0149358870'
        self.assertEqual(r.extract_phone_number(line_descr), '01.49.35.88.70')
        # TELR
        line_descr = 'TELR01493588A70'
        self.assertEqual(r.extract_phone_number(line_descr), '01.49.35.88.70')
        # Wrong number
        line_descr = 'Date: 20/07/2016 16:34 Nb Article: 2'
        self.assertEqual(r.extract_phone_number(line_descr), '')

    def test_extract_phone_number_from_lines(self):
        lines = event['lines']
        self.assertEqual(r.extract_phone_number_from_lines(lines), '0149358870')
