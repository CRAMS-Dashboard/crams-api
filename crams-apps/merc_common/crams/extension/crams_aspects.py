# coding=utf-8
"""

"""


class CramsAspect:
    def __init__(self, serializer_class):
        self.serializer_class = serializer_class
        self.pre_method_dict = dict()
        self.post_method_dict = dict()

    def add_pre_fn_for_method_name(self, method_name, pre_fn):
        if method_name not in self.pre_method_dict:
            self.pre_method_dict[method_name] = set()
        upd_pre_fn_set = self.pre_method_dict[method_name]
        upd_pre_fn_set.add(pre_fn)

    def add_post_fn_for_method_name(self, method_name, post_fn):
        if method_name not in self.post_method_dict:
            self.post_method_dict[method_name] = set()
        upd_post_fn_set = self.post_method_dict[method_name]
        upd_post_fn_set.add(post_fn)


CRAMS_ASPECT_DICT = dict()
