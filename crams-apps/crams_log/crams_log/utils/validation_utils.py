# coding=utf-8
"""
 validation utils
"""


class ChangedMetadata:
    def __init__(self):
        self.obj_dict = dict()
        self.modified_related_field_set = set()
        self.new_related_field_set = set()
        self.removed_related_field_set = set()
        self.err_list = list()
