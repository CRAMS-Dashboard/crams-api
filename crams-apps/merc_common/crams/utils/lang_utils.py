# coding=utf-8
"""
    Python utils
"""


def has_invalid_prefix(str, invalid_prefix_list):
    return not validate_prefix(str, invalid_prefix_list, False)


def has_valid_prefix(str, valid_prefix_list):
    return validate_prefix(str, valid_prefix_list, True)


def validate_prefix(str, prefix_list, prefix_list_is_valid=True):
    for prefix in prefix_list:
        if str and str.startswith(prefix):
            return prefix_list_is_valid
    return not prefix_list_is_valid


def strip_lower(str):
    return str.strip().lower()


def reverse_dict(d):
    return {v: k for k, v in d.items()}


def update_return_dict(map, key, value):
    map.update({key: value})
    return map


# http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
class Bunch(list):

    """

    :param args:
    :param kw:
    """

    def __init__(self, *args, **kw):
        super(Bunch, self).__init__()
        self[:] = list(args)
        setattr(self, '__dict__', kw)


class BunchDict(dict):

    """

    :param kw:
    """

    def __init__(self, **kw):
        # noinspection PyTypeChecker
        dict.__init__(self, kw)
        self.__dict__ = self

    def __str__(self):
        state = ["%s=%r" % (attribute, value)
                 for (attribute, value)
                 in self.__dict__.items()]
        return '\n'.join(state)


# http://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
class CommonEqualityMixin(object):
    """
        Common Equality Mixin
    """
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class SortableObject(CommonEqualityMixin):
    """

    :param obj:
    :param sort_lambda:
    """

    def __init__(self, obj, sort_lambda):
        self.obj = obj
        self.sortLambda = sort_lambda

    def is_same_internal_object(self, other):
        """

        :param other:
        :return:
        """
        if (isinstance(other, type(self))) or\
                (isinstance(self.obj, type(other))):
            return other.obj == self.obj
        return False
