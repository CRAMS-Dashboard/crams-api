from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions

from crams.extension import config_init
from crams.models import EResearchBody
from crams_allocation.models import Request
from crams_contact.models import Contact
from crams_contact.models import CramsERBUserRoles
from crams_review.models import ReviewDate
from crams_review.models import ReviewConfig

STATUS_DICT = ReviewDate.STATUS_CHOICES
DATE_FILTER = ['week', 'month', 'year', 'all']


# when function is called checks the request:
#   - erb for review settings
#   - request id/s if a review has been previously set before
# after checking the request meets prerequisites it will save
# a review entry for that request.
def set_review(crams_req):
    # check erb from request has a review config settings
    erb = crams_req.e_research_system.e_research_body

    r_conf = ReviewConfig.objects.filter(e_research_body=erb).first()

    if not r_conf:
        # no need to continue, no review configuration found
        # no review date will be set for this request
        return

    # get the latest/current request
    current_req = get_latest_request(crams_req)

    # grab all past children request
    req_children = Request.objects.filter(current_request=current_req)

    # check if any requests have a review set previously
    existing_reviews = ReviewDate.objects.filter(request__in=req_children)
    if not existing_reviews:
        # if no reviews found with children requests check with current req
        existing_reviews = ReviewDate.objects.filter(request=current_req)
        if not existing_reviews:
            # get the next review date from today plus the review period
            review_period = get_erb_review_period(erb)
            next_review_date = datetime.now() + relativedelta(months=review_period)

            # save a new review for the request
            new_rd = ReviewDate.objects.create(
                review_date=next_review_date,
                request=current_req,
                status='P',
                notes=None,
                review_json=None
            )


def get_latest_request(request):
    if request.current_request:
        return request.current_request
    else:
        return request


def get_erb_notify_period(e_research_body):
    try:
        r_conf = ReviewConfig.objects.get(e_research_body=e_research_body)
        return r_conf.review_notify_month
        
    except:
        raise exceptions.ParseError(
            'Notification period not set for ERB - {}'.format(
                e_research_body.name))


def get_erb_review_period(e_research_body):
    try:
        r_conf = ReviewConfig.objects.get(e_research_body=e_research_body)
        return r_conf.review_period_month
    except:
        raise exceptions.ParseError(
            'Review period not set for ERB - {}'.format(
                e_research_body.name))


def validate_erb_admin(user, e_research_body):
    try:
        contact = Contact.objects.get(email=user.email)
    except ObjectDoesNotExist:
        raise exceptions.ParseError(
            'User contact {} does not exist'.format(user.email))

    # user has a erb admin role
    crams_roles = CramsERBUserRoles.objects.filter(
        contact=contact, role_erb=e_research_body, is_erb_admin=True)

    if crams_roles:
        return True
    else:
        raise exceptions.PermissionDenied(
            'User is does not have the correct erb admin privilege')


def validate_status(status_str):
    if status_str:
        for stat in STATUS_DICT:
            if status_str.lower() == stat[1].lower():
                return status_str
        # no status not found in the status choice
        raise exceptions.ParseError(
            'Unknown status provided - {}'.format(status_str))
    else:
        return None


def validate_review_list_status(review_list_sz, valid_status_list):
    for sz in review_list_sz:
        try:
            rd = ReviewDate.objects.get(pk=sz.get('id'))
        except ObjectDoesNotExist:
            raise exceptions.ParseError(
                'Review id {} not found'.format(sz.get('id'))
            )

        # if status is sent or skipped return error
        if rd.status not in valid_status_list:
            raise exceptions.ParseError(
                'Unable to proceed with review id: {}, invalid status: {}, ' +
                'expecting: {}'.format(rd.id, rd.status, valid_status_list)
            )


def get_status_code(status_str):
    for stat in STATUS_DICT:
        if stat[1].lower() == status_str.lower():
            return stat[0]


def get_erb_obj(erb_str):
    try:
        return EResearchBody.objects.get(name__iexact=erb_str)
    except ObjectDoesNotExist:
        raise exceptions.ParseError(
            'EResearchBody - {} not found'.format(erb_str))


def get_date_range(date_range_str):
    if date_range_str.lower() in DATE_FILTER:
        if date_range_str.lower() == 'week':
            return relativedelta(weeks=1)

        if date_range_str.lower() == 'month':
            return relativedelta(months=1)

        if date_range_str.lower() == 'year':
            return relativedelta(months=12)

        if date_range_str.lower() == 'all':
            return None
    else:
        raise exceptions.ParseError(
            'Date_filter: {} invalid, use {}'.format
                (date_range_str, DATE_FILTER)
        )


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
