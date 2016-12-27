# -*- coding: utf-8 -*-
from unittest import TestCase

from Code.Utils.utilNormalizer import Normalizer

n = Normalizer()
class TestNormalizer(TestCase):
    def test_to_lower(self):
        str1 = 'Test l\'épée manGeons d\'aujourd\'hui 3   '
        res = n.to_lower(str1)
        self.assertEqual('test l\'épée mangeons d\'aujourd\'hui 3   ', res, "Problem with lower case")

    def test_suppress_number(self):
        str1 = 'test l\'épée mangeons d\'aujourd\'hui 3   '
        res = n.suppress_number(str1)
        self.assertEqual('test l\'épée mangeons d\'aujourd\'hui    ', res, "Problem with suppress number")

    def test_suppress_apostrophe(self):
        str1 = 'test l\'épée mangeons d\'aujourd\'hui    '
        res = n.suppress_apostrophe(str1)
        self.assertEqual('test épée mangeons aujourd\'hui    ', res, "Problem with suppress apostrophe")

    def test_suppress_punctuation(self):
        str1 = 'test épée mangeons aujourd\'hui    '
        res = n.suppress_punctuation(str1)
        print type(res)
        print res
        self.assertEqual('test épée mangeons aujourdhui    ', res, "Problem with suppress punctuation")

    def test_suppress_stopword(self):
        str1 = 'a test épée mangeons aujourdhui    '
        res = n.suppress_stopword(str1)
        self.assertEqual('test', res[0], "Problem with suppress stopwords")

    def test_suppress_accent(self):
        str1 = 'a test épée mangeons aujourdhui    '
        res_temp = n.suppress_stopword(str1)
        res = n.suppress_accent(res_temp)
        print res
        self.assertEqual('epee', res[1], "Problem with suppress accent")

    def test_stemm_words(self):
        str1 = 'a test épée mangeons aujourdhui    '
        res_temp = n.suppress_stopword(str1)
        res_temp2 = n.suppress_accent(res_temp)
        res = n.stemm_words(res_temp2)
        self.assertEqual('epe', res[1], "Problem with stemming")

    def test_end_to_end_normalize(self):
        str1 = 'Test l\'épée manGeons d\'aujourd\'hui 3   '
        res = n.end_to_end_normalize(str1)
        self.assertEqual('test epe mangeon aujourdhui', res, "Problem with end to end")

    def test_clean_duplicate_string(self):
        str1 = 'a a test test test'
        res = n.clean_duplicate_string(str1)
        self.assertEqual('a test', res, "Problem with clean Duplicate")

    def test_keep_first_letters(self):
        str1 = 'a test expose test'
        res = n.keep_first_letters(str1, 3)
        self.assertEqual('a tes exp', res, "Problem with keep first letter")

    def test_from_dict_to_list(self):
        dict = {u'CHAUSSON FRUIT': u'NON RECONNU', u'BOUTEILLE 33CL': u'NON RECONNU'}
        list_res = n.from_dict_to_list(dict)
        self.assertEqual(list_res, ['CHAUSSON FRUIT', 'BOUTEILLE 33CL'])

    def test_from_two_lists_to_dict(self):
        list_key = ['b', 'a']
        list_value = ['d', 'c']
        dict_res = n.from_two_lists_to_dict(list_key, list_value)
        self.assertEqual(dict_res, {"b": "d", "a": "c"})
