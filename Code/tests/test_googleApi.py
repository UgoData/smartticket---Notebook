# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from Code.raw_treatments.googlePlaces import GoogleApi

g = GoogleApi('b boyz', '5 avenue trudaine 75009')
json_google = json.load(open("data_test/test_json_apigoogle.json", "rb"))


class TestGoogleApi(TestCase):
    def test_get_place_infos(self):
        result = g.get_place_infos()
        self.assertEqual(result['status'], 'OK')
        self.assertEqual(result['results'][0]['name'], 'B-BOYZ')
        self.assertEqual(result['results'][0]['types'], ["restaurant", "food", "point_of_interest", "establishment"])

    def test_get_place_type_from_google(self):
        result = g.get_place_type_from_google(json_google)
        self.assertEqual(result, ["restaurant", "food", "point_of_interest", "establishment"])

    def test_convert_googletypes_into_rmwtypes(self):
        result = g.convert_googletypes_into_rmwtypes(["restaurant", "food", "point_of_interest", "establishment"])
        print result
        self.assertEqual(result[0], 'Restaurant')
        self.assertEqual(result[3], '')

    def test_return_only_one_category(self):
        result = g.return_only_one_category(["restaurant", "food", "", ""])
        self.assertEqual(result, 'food')
