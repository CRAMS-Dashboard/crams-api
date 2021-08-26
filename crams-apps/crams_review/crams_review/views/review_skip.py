from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from crams import permissions
from crams_collection.models import Project
from crams_review import models as review_models
from crams_review.serializers import ReviewSerializer
from crams_review import utils

STATUS_DICT = review_models.ReviewDate.STATUS_CHOICES


class ReviewSkipView(CreateModelMixin,
                     GenericViewSet):
    """
    Usage for skipping single review:
    {
        "id": <review_date_id>,
        "notes": <string_free_text>
    }

    Usage for skipping muiltiple reivews:
    [{
        "id": <review_date_id>,
        "notes": <string_free_text>
    },{
        "id": <review_date_id>,
        "notes": <string_free_text>
    }]
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsCramsAdmin]
    queryset = Project.objects.none()
    serializer_class = ReviewSerializer

    def _update_review(self, review_sz, request):
        # check review_date exists
        try:
            rd = review_models.ReviewDate.objects.get(pk=review_sz.get('id'))
        except ObjectDoesNotExist:
            raise exceptions.ParseError(
                'Review id: {} does not exist'.format(review_sz.get('id'))
            )

        # check review_date status is "pending"
        if rd.status != 'P':
            raise exceptions.ParseError(
                'Can not skip review for id: {}, where status is {}'.format(
                    rd.id, rd.status
                )
            )

        # check user has the correct erb admin rights to skip the review
        erb = rd.request.e_research_system.e_research_body
        utils.validate_erb_admin(request.user, erb)

        # get the review date period from erb
        review_period = utils.get_erb_review_period(erb)
        next_review_date = rd.review_date + relativedelta(months=review_period)

        # mark review_date status as skipped
        rd.status = 'K'
        rd.updated_by = request.user
        rd.notes = review_sz.get('notes')
        rd.save()

        # create the next review date
        review_models.ReviewDate.objects.create(
            status='P',
            review_date=next_review_date,
            request=rd.request,
            created_by=request.user,
            updated_by=request.user
        )

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        if is_many:
            serializer = self.get_serializer(request.data, many=True)
            try:
                sz_data = serializer.data
            except KeyError:
                raise exceptions.ParseError(
                    'KeyError: check json format is valid'
                )

            # check bulk reviews are valid before skipping them
            utils.validate_review_list_status(sz_data, ['P'])

            for review in serializer.data:
                self._update_review(review, request)

            return Response("Reviews skipped", status=HTTP_201_CREATED)

        else:
            rd_sz = self.get_serializer(request.data)

            try:
                rd_sz_data = rd_sz.data
            except KeyError:
                raise exceptions.ParseError(
                    'KeyError: check json format is valid'
                )

            self._update_review(rd_sz_data, request)

            return Response("Review skipped.", status=HTTP_201_CREATED)
