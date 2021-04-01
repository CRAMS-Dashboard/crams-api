# coding=utf-8
"""Utils."""

import inspect
import itertools
import random
import string
import io


def get_random_num_str(num):
    return ''.join(
        random.SystemRandom().choice(string.digits) for _ in range(num))


def get_random_string(num):
    # http://stackoverflow.com/questions/2257441/random-string-generation-with
    # -upper-case-letters-and-digits-in-python/23728630#23728630
    # return ''.join(random.choice(string.ascii_uppercase + string.digits) for
    # _ in range(num))
    """
        get_random_string
    :param num:
    :return:
    """
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase +
            string.digits) for _ in range(num))


# Modified from
# http://stackoverflow.com/questions/18826571/python-powerset-of-a-given-set-with-generators
def power_set_generator(input_set):
    """
        power_set_generator
    :param input_set:
    """
    for subset in itertools.chain.from_iterable(
        itertools.combinations(
            input_set, r) for r in range(
            len(input_set) + 1)):
        yield set(subset)


def debug_function_name(level=1, print_upto=False):
    """
    Prints name of the current calling function, useful in debug,
    :return:
    """
    # current function ==> print(inspect.stack()[0][3])
    if print_upto:
        count = 0
        while count < level:
            print(inspect.stack()[count][3])
            count += 1
    print(inspect.stack()[level][3])


def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents
