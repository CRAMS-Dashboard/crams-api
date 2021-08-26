from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from crams import permissions
from crams_allocation.models import Request
from crams_collection.models import Project
from crams_review import models as review_models
from crams_review.serializers import ReviewDateSerializer
from crams_review import utils


class ReviewDateView(ListModelMixin,
                     RetrieveModelMixin,
                     GenericViewSet):
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsCramsAdmin]
    queryset = Project.objects.none()
    serializer_class = ReviewDateSerializer

    def list(self, request, *args, **kwargs):
        # fetch the erb
        erb_str = request.query_params.get('erb')
        erb = utils.get_erb_obj(erb_str)

        # validate erb admin
        utils.validate_erb_admin(request.user, erb)

        # fetch and validate status
        status_str = utils.validate_status(
            request.query_params.get('status'))
        if status_str is None:
            status_str = 'pending'

        review_qs = review_models.ReviewDate.objects.filter(
            request__e_research_system__e_research_body=erb)

        # get date_filter param if exist
        date_range_str = None
        date_range = None
        if request.query_params.get('date_filter'):
            date_range_str = request.query_params.get('date_filter')
            date_range = utils.get_date_range(date_range_str)

        # for pending reviews get the review date notify period
        # and filter reviews
        if status_str == 'pending':
            # if date filter is specified ignore the notify period
            if date_range_str:
                # if reviews from the specified date_range
                if date_range:
                    start_date = datetime.now() - date_range
                    end_date = datetime.now()
                    review_qs = review_qs.filter(review_date__range=(
                        start_date, end_date), status='P').order_by(
                        'review_date')
                else:
                    # if date range is none show everything
                    review_qs = review_qs.filter(status='P').order_by('review_date')
            else:
                # use the notify period to get list of reviews
                notify_period = utils.get_erb_notify_period(erb)
                review_date = datetime.now() + relativedelta(months=notify_period)
                review_qs = review_qs.filter(review_date__lte=review_date,
                                             status='P').order_by('review_date')
        else:
            status_code = utils.get_status_code(status_str)
            review_qs = review_qs.filter(status=status_code).order_by(
                'review_date')

            if date_range:
                start_date = datetime.now() - date_range
                end_date = datetime.now()
                review_qs = review_qs.filter(review_date__range=(
                    start_date, end_date))

        return Response(
            self.serializer_class(review_qs, many=True).data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            int(pk)
        except ValueError:
            raise exceptions.ParseError(
                'Invalid pk - {}'.format(pk))
        # get review date
        try:
            review_date = review_models.ReviewDate.objects.get(pk=pk)

            # check admin has access to request via erb
            utils.validate_erb_admin(
                request.user,
                review_date.request.e_research_system.e_research_body)
        except ObjectDoesNotExist:
            raise exceptions.ParseError(
                'Review Date not found for pk - {}'.format(pk))

        return Response(self.serializer_class(review_date).data)

    @action(detail=True, url_path='history')
    def get_history(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            int(pk)
        except ValueError:
            raise exceptions.ParseError(
                'Invalid pk = {}'.format(pk))

        # get the status if provided otherwise return all status history
        status_str = utils.validate_status(request.query_params.get('status'))

        # get review date
        try:
            review_date = review_models.ReviewDate.objects.get(pk=pk)

            # check admin has access to request via erb
            utils.validate_erb_admin(
                request.user,
                review_date.request.e_research_system.e_research_body)

            review_date_list = review_models.ReviewDate.objects.filter(
                request=review_date.request)

            # filter results by status if provided
            if status_str:
                review_date_list.filter(
                    status=utils.get_status_code(status_str))

        except ObjectDoesNotExist:
            raise exceptions.ParseError(
                'Review Date not found for pk - {}'.format(pk))

        return Response(
            self.serializer_class(review_date_list, many=True).data)

    @action(detail=False, url_path='request_history/(?P<request_id>[^/.]+)')
    def get_request_history(self, request, *args, **kwargs):
        req_id = kwargs.get('request_id')
        try:
            int(req_id)
        except ValueError:
            raise exceptions.ParseError(
                'Invalid request id = {}'.format(req_id))

        # get the status if provided otherwise return all status history
        status_str = utils.validate_status(
            request.query_params.get('status'))

        # get the request
        try:
            req_obj = Request.objects.get(pk=req_id)

            # check admin has access to request via erb
            utils.validate_erb_admin(
                request.user,
                req_obj.e_research_system.e_research_body)

            # get the latest parent request
            if req_obj.current_request:
                req_obj = req_obj.current_request

            # get request child list of ids
            child_req_ids_list = Request.objects.filter(
                current_request=req_obj).values_list('id', flat=True)

            # append the parent to the list
            child_req_ids_list.append(req_obj.id)

            review_date_list = review_models.ReviewDate.objects.filter(
                request_id__in=child_req_ids_list)

            # filter results by status if provided
            if status_str:
                review_date_list.filter(
                    status=utils.get_status_code(status_str))

        except ObjectDoesNotExist:
            raise exceptions.ParseError(
                'Request not found for id - {}'.format(req_id))

        return Response(
            self.serializer_class(review_date_list, many=True).data)
