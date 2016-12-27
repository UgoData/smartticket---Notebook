# coding: utf-8

from unittest import TestCase
from loadAndCleanData import LoadCleanData
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


class TestLoadCleanData(TestCase):

    def test_load_classes(self):
        l = LoadCleanData()
        df = l.load_classes()
        self.assertEqual(df.shape, (19, 1), 'Function Load Class not working')

    def test_load_open_food_facts(self):
        l = LoadCleanData()
        df = l.load_open_food_facts()
        self.assertEqual(df.shape, (34424, 18), 'Function Load Open Food Facts not working')

    def test_load_open_beauty_facts(self):
        l = LoadCleanData()
        df = l.load_open_beauty_facts()
        self.assertEqual(df.shape, (2274, 159), 'Function Load Open Beauty Facts not working')

    # def test_shape_df(self):
        # self.fail()

    def test_only_fr_data_from_open_ff(self):
        col_test = ["countries_fr"]
        df_test = pd.DataFrame([['France'], ['France'], ['Italie']], columns=col_test)
        l = LoadCleanData()
        df = l.only_fr_data_from_open_ff(df_test)
        self.assertEqual(df.shape, (2, 1), 'Function keep only french data not working')

    def test_add_merge_columns(self):
        df_test = pd.DataFrame({"product_name": ['a', 'b', 'c'], 'two': ['a', 'b', 'c']})
        col_test = ['two']
        l = LoadCleanData()
        l.add_merge_columns(df_test, col_test)
        self.assertIn("merge_col", df_test.columns, "Problem with columns merge")
        self.assertEqual('a a', df_test.iloc[0, 2], "Problem with columns merge")

    def test_select_col_beauty_fact(self):
        col_test = [
            "url", "product_name", "generic_name", "quantity",
            "brands_tags", "categories_fr", "stores", "countries_fr",
            "main_category_fr", "image_url", "to_delete"
        ]
        df_test = pd.DataFrame([
            ['url', 'product_1', '', 5, 'brand',  'cat', 'stor', 'count', 'main', 'imag', "to_delete"],
            ['url', np.nan, '', 5, 'brand',  'cat', 'stor', 'France', 'main', 'imag', "to_delete"],
            ['url', 'product_1', '', 5, 'brand', 'cat', 'stor', 'France', 'main', 'imag', "to_delete"]
        ], columns=col_test)
        l = LoadCleanData()
        df = l.select_col_beauty_fact(df_test)
        self.assertEqual(df.shape, (1, 10), 'Problem with column suppression')

    def test_load_clean_data(self):
        l = LoadCleanData()
        df1, df2 = l.load_clean_data()

    def test_concat_dfs(self):
        l = LoadCleanData()
        df1, df2 = l.load_clean_data()
        print l.concat_dfs(df1, df2).shape[0]
        self.assertEqual(26958, l.concat_dfs(df1, df2).shape[0], "Problem with Concat dfs")

    #def test_print_outputs(self):
        #self.fail()
