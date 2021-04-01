# coding=utf-8
"""
Date Utility Functions
"""
import pytz
from calendar import timegm
from merc_common.settings import TIME_ZONE
from django.utils import timezone as d_timezone
from datetime import datetime, date, timedelta, MINYEAR, MAXYEAR
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


def parse_datetime_from_str(str_datetime_obj):
    if isinstance(str_datetime_obj, datetime):
        return str_datetime_obj
    if isinstance(str_datetime_obj, date):
        return date_to_datetime(str_datetime_obj)
    return convert_naive_to_timezone(parse(str_datetime_obj))


def is_timestamp(obj):
    return isinstance(obj, datetime)


def get_epoch_time(datetime_obj):
    """
        Return Epoch Time
    :param datetime_obj:
    :return:
    """
    return timegm(datetime_obj.timetuple())


def test_get_epoch_time():
    """
        Test get_epoch_time

    """
    assert get_epoch_time(date(1995, 1, 12)) == 789868800


def get_date_str(obj):
    """
        Convert date object to string
    :param obj:
    :return:
    """
    date_obj = obj
    if isinstance(obj, datetime):
        date_obj = obj.date()
    return str(date_obj)


def test_get_date_str():
    """
        Test get_date_str

    """
    assert get_date_str(date(2014, 10, 16)) == '2014-10-16'
    assert get_date_str(get_current_time_for_app_tz()) == get_current_date()


def is_current_year(date_time_obj):
    """
        check if the given date is in current year

    :param date_time_obj:
    :rtype : bool
    """
    return get_current_year() == date_time_obj.year


def test_is_current_year():
    """
        test is_current_year

    """
    now = datetime.now()
    assert is_current_year(now), "tests for current year fails"
    assert not is_current_year(increase_date(
        now.date(), 370)), "next year should be equal to current year"
    assert not is_current_year(reduce_date(now.date(),
                                           370)), \
        "previous year should be equal to current year"


def get_current_year():
    """
        return current year

    :return:
    """
    return get_current_time_for_app_tz().year


def test_get_current_year():
    """
        test get_current_year

    """
    assert datetime.now().year == get_current_year(), 'current year not ' \
                                                      'fetched correctly'


def get_jan01_current_year():
    """
        get First day of Current Year

    :return:
    """
    return date(get_current_year(), 1, 1)


def get_min_date():
    """
    test get_jan01_current_year

    :return:
    """
    return date(MINYEAR, 1, 1)


def get_max_date():
    """
        get system maximum date

    :return:
    """
    return date(MAXYEAR, 12, 31)


def get_current_time_for_app_tz():
    """
        get current time

    :return:
    """
    tz = pytz.timezone(TIME_ZONE)
    return datetime.now(tz)


def get_current_date():
    """
        get current date

    :return:
    """
    return get_current_time_for_app_tz().date()


def date_to_datetime(in_date, choose_end_of_day=False):
    ret_date = None
    if isinstance(in_date, date):
        ret_date = in_date
    elif isinstance(in_date, datetime):
        ret_date = in_date.date()
    elif isinstance(in_date, str):
        ts = parse_datetime_from_str(in_date)
        ret_date = ts.date()

    if choose_end_of_day:
        ret_date = increase_date(ret_date, 1)

    ret_ts = datetime.combine(ret_date, datetime.min.time())
    if choose_end_of_day:
        one_second = timedelta(seconds=1)
        ret_ts = ret_ts - one_second
    return convert_naive_to_timezone(ret_ts)


def get_mssql_date(in_date):
    """
        get date suitable for use by microsoft SQL
    :param in_date:
    :return:
    """
    return in_date.strftime('%Y%m%d')


def get_mssql_timestamp(in_time_stamp):
    """
        get timestamp suitable for use by microsoft SQL
    :param in_time_stamp:
    :return:
    """
    return in_time_stamp.strftime('%Y-%m-%d %H:%M:%S')


def get_day_difference(date_obj0, date_obj1):
    """
        calculate date difference between date_obj0 and date_obj1
    :param date_obj0:
    :param date_obj1:
    :return:
    """
    delta = date_obj0 - date_obj1
    return delta.days


def test_get_day_difference():
    """
        test get_day_difference

    """
    assert get_day_difference(date(2014, 10, 16), date(
        2014, 10, 5)) == 11, "difference in days not computed properly"


def increase_date(date_to_increase, increase_by):
    """
        increase dateObj by given days
    :param date_to_increase:
    :param increase_by:
    :return:
    """
    return transpose_date(date_to_increase, increase_by)


def test_increase_date():
    """
        test increase_date

    """
    assert increase_date(date(2014, 10, 16), 4) == date(
        2014, 10, 20), "increasing by 4 days does not work"


def get_midnight_next_day(timestamp_obj):
    expiry_ts = timestamp_obj + timedelta(days=2)
    return expiry_ts.replace(hour=0, minute=0, second=0, microsecond=0)


def reduce_date(date_to_reduce, reduce_by):
    """
        reduce date obj by given days
    :param date_to_reduce:
    :param reduce_by:
    :return:
    """
    return transpose_date(date_to_reduce, -1 * reduce_by)


def test_reduce_date():
    """
        test reduce_date

    """
    assert reduce_date(date(2014, 10, 16), 3) == date(
        2014, 10, 13), "reducing by 3 days does not work"


def update_by_year(date_to_transpose, year_count):
    return date_to_transpose + relativedelta(years=year_count)


def update_by_month(date_to_transpose, month_count):
    return date_to_transpose + relativedelta(months=month_count)


def transpose_date(date_to_transpose, by_days):
    """
        transpose given date bu given days,
            positive and negative values allowed for by_days parameter
    :param date_to_transpose:
    :param by_days:
    :return:
    """
    return date_to_transpose + timedelta(days=by_days)


def test_transpose_date():
    """
        test transpose_date

    """
    assert transpose_date(date(2014, 10, 16), -6) == date(2014, 10, 10), \
        "transposing by negative 6 days does not work"
    assert transpose_date(date(2014, 10, 16), 6) == date(2014, 10, 22), \
        "transposing by positive 6 days does not work"


def is_given_date_after_current_date(given_date):
    """
        test if given date obj is after current date
    :param given_date:
    :return:
    """
    return get_day_difference(given_date, get_current_date()) > 0


def test_is_current_date_after_given_date():
    """
        test is_current_date_after_current_date

    """
    assert is_given_date_after_current_date(
        increase_date(
            get_current_date(),
            3)), "Current date must be before future date " + str(
        increase_date(
            get_current_date(), 3))
    assert not is_given_date_after_current_date(
        get_current_date()), "Current date must not be before current date"
    assert not is_given_date_after_current_date(
        reduce_date(
            get_current_date(),
            3)), "Current date must not be before past date " + str(
        reduce_date(
            get_current_date(), 3))


def get_minutes_elapsed(end_ts, start_ts):
    return int(get_seconds_elapsed(end_ts, start_ts) / 60)


def get_seconds_elapsed(end_ts, start_ts):
    start_ts_non_naive = convert_naive_to_timezone(start_ts)
    end_ts_non_naive = convert_naive_to_timezone(end_ts)
    elapsed_dt = end_ts_non_naive - start_ts_non_naive
    return elapsed_dt.total_seconds()


def convert_naive_to_timezone(ts, time_zone=TIME_ZONE):
    if d_timezone.is_naive(ts):
        tz = pytz.timezone(time_zone)
        zone_ts = tz.localize(ts)
        return zone_ts
    return ts
