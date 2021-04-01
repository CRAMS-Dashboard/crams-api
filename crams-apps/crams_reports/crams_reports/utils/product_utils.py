# coding=utf-8
"""

"""
from crams_reports.constants import report_constants


RETURN_ALLOCATED_ONLY_PARAM = 'allocated_only'


def calc_product_cost(product_obj, size):
    def cost(dollar_value):
        return size * dollar_value * report_constants.GB_TO_TB_METRIC_FACTOR

    cap_cost = cost(product_obj.unit_cost)
    op_cost = cost(product_obj.operational_cost)
    return cap_cost, op_cost, cap_cost + op_cost
