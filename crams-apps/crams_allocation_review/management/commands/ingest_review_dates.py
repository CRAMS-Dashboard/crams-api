from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand

from crams import models as crams_models
from crams.config import config_init
from crams.review import models as review_models


class Command(BaseCommand):
    help = 'Sets review dates on provisioned projects based ' \
           'on first provisioned request of a project.'

    def handle(self, *args, **options):
        # get all the erb that have been configured to have review dates
        review_conf_list = review_models.ReviewConfig.objects.all()

        # for each erb get all request related
        for conf in review_conf_list:
            erb = conf.e_research_body
            review_period = \
                config_init.eSYSTEM_REVIEW_PERIOD_MAP[erb.name.lower()]

            req_list = crams_models.Request.objects.filter(
                e_research_system__e_research_body=erb,
                current_request=None)

            for req in req_list:
                # for the parent request get all child request
                req_children_list = crams_models.Request.objects.filter(
                    current_request=req).order_by('creation_ts')

                # check if any of the children requests has an existing
                # review entry recorded against the project
                review_list = review_models.ReviewDate.objects.filter(
                    request__in=req_children_list)

                # skip the next processes if a review date has already
                # been recorded for the project
                if not review_list:
                    # get the first request with a provisioned date
                    for req_child in req_children_list:
                        prj_prov_dets = crams_models.ProjectProvisionDetails.\
                            objects.filter(project=req_child.project,
                                           provision_details__status='P')\
                            .order_by('provision_details__creation_ts')

                        # if provisioning details found for the earliest
                        # request set a review entry for project
                        if prj_prov_dets:
                            # create review date for this request
                            # using the erb to get the review date period
                            review_date = prj_prov_dets.first().provision_details\
                                .creation_ts + relativedelta(months=review_period)

                            review_models.ReviewDate.objects.create(
                                review_date=review_date,
                                request=req_child,
                            )
                            break

        print("Review dates ingest complete.")
