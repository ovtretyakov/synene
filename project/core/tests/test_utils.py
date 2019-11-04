from decimal import Decimal

from django.test import TestCase

from ..utils import get_total_over_result, get_total_under_result, get_handicap_result


class UtilsTest(TestCase):

    def setUp(self):
        pass

    #######################################################################
    def test_get_total_over_result(self):
        odd_value = Decimal('3')
        match_value = 2

        param_value = Decimal('1.5')
        expected_result = (odd_value/2 + odd_value/2)
        result = get_total_over_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('1.75')
        expected_result = (odd_value/2 + Decimal('1')/2)
        result = get_total_over_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('2.00')
        expected_result = (Decimal('1')/2 + Decimal('1')/2)
        result = get_total_over_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('2.25')
        expected_result = (Decimal('1')/2 + Decimal('0')/2)
        result = get_total_over_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('2.50')
        expected_result = (Decimal('0')/2 + Decimal('0')/2)
        result = get_total_over_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        odd_value = Decimal('1.75')
        expected_result = (odd_value/2 + Decimal('1')/2)
        param_value = Decimal('1.75')
        result = get_total_over_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

    #######################################################################
    def test_get_total_under_result(self):
        odd_value = Decimal('3')
        match_value = 2

        param_value = Decimal('1.5')
        expected_result = (Decimal('0')/2 + Decimal('0')/2)
        result = get_total_under_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('1.75')
        expected_result = (Decimal('1')/2 + Decimal('0')/2)
        result = get_total_under_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('2.00')
        expected_result = (Decimal('1')/2 + Decimal('1')/2)
        result = get_total_under_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('2.25')
        expected_result = (odd_value/2 + Decimal('1')/2)
        result = get_total_under_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('2.50')
        expected_result = (odd_value/2 + odd_value/2)
        result = get_total_under_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        odd_value = Decimal('1.75')
        expected_result = (odd_value/2 + Decimal('1')/2)
        param_value = Decimal('2.25')
        result = get_total_under_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

    #######################################################################
    def test_get_handicap_result(self):
        #### negativ
        odd_value = Decimal('3')
        match_value = 2

        param_value = Decimal('-1.5')
        expected_result = (odd_value/2 + odd_value/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('-1.75')
        expected_result = (odd_value/2 + Decimal('1')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('-2.00')
        expected_result = (Decimal('1')/2 + Decimal('1')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('-2.25')
        expected_result = (Decimal('1')/2 + Decimal('0')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('-2.50')
        expected_result = (Decimal('0')/2 + Decimal('0')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        odd_value = Decimal('1.75')
        expected_result = (odd_value/2 + Decimal('1')/2)
        param_value = Decimal('-1.75')
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        #### positiv
        odd_value = Decimal('3')
        match_value = -3

        param_value = Decimal('2.5')
        expected_result = (Decimal('0')/2 + Decimal('0')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('2.75')
        expected_result = (Decimal('1')/2 + Decimal('0')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('3.00')
        expected_result = (Decimal('1')/2 + Decimal('1')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('3.25')
        expected_result = (odd_value/2 + Decimal('1')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        param_value = Decimal('3.50')
        expected_result = (odd_value/2 + odd_value/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)

        odd_value = Decimal('1.75')
        param_value = Decimal('2.75')
        expected_result = (Decimal('1')/2 + Decimal('0')/2)
        result = get_handicap_result(param_value, match_value, odd_value)
        self.assertEquals(result, expected_result)
