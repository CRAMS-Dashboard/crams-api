from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from crams.constants import db
from crams import permissions
from crams_collection.models import Project
from crams_collection.models import ProjectContact
from crams_collection.models import ProjectProvisionDetails
from crams_contact.models import CramsERBUserRoles
# from crams.tasks import send_email_notification
from crams_review.config.review_config import ERB_Review_Email_fn_dict
from crams_review.config.review_config import get_email_processing_fn
from crams_review import models as review_models
from crams_review.serializers import ReviewSerializer
from crams_review import utils

STATUS_DICT = review_models.ReviewDate.STATUS_CHOICES


class ReviewSendView(CreateModelMixin,
                     GenericViewSet):
    """
    Usage for sending single review:
    {
        "id": <review_date_id>,
        "notes": <string_free_text>
    }
    Usage for sending multiple review:
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
    queryset = review_models.ReviewDate.objects.none()
    serializer_class = ReviewSerializer

    # project contacts - people in the project the email is address to
    def _get_recipient_emails(self, project_contacts, contact_roles):
        # check project contact has the role of to receive an email
        recipient_list = []
        for prj_ct in project_contacts:
            if contact_roles.filter(contact_role=prj_ct.contact_role).first():
                recipient_list.append(prj_ct.contact.email)

        return recipient_list

    # admin contacts - crams administrative contacts approver, provisioner,
    # erb system level admins and erb level admins.
    # people who are not in the project but are cc'd in the email
    def _get_crams_admin_emails(self, contact_roles, erb):
        cc_list = []
        for contact_role in contact_roles:
            # add erb admin
            if contact_role.contact_role.name == db.E_RESEARCH_BODY_ADMIN:
                erb_role_list = CramsERBUserRoles.objects.filter(
                    role_erb=erb, is_erb_admin=True)
                for erb_role in erb_role_list:
                    cc_list.append(erb_role.contact.email)

            # TODO: customisation for other crams admin roles
            # add erbs admin
            if contact_role.contact_role.name == db.E_RESEARCH_BODY_SYSTEM_ADMIN:
                pass

            # add approver
            if contact_role.contact_role.name == db.E_RESEARCH_BODY_SYSTEM_APPROVER:
                pass

            # add provisioner
            if contact_role.contact_role.name == db.E_RESEARCH_BODY_SYSTEM_PROVISIONER:
                pass

            # add delegate
            if contact_role.contact_role.name == db.E_RESEARCH_SYSTEM_DELEGATE:
                pass

        return cc_list

    def _send_email(self, review_date, erb):
        current_request = utils.get_latest_request(review_date.request)
        # get the latest project
        project = current_request.project

        # get the erb review email template and recipients
        try:
            review_conf = review_models.ReviewConfig.objects.get(
                e_research_body=erb)
        except ObjectDoesNotExist:
            raise exceptions.ParseError(
                "No review config template found for erb - {}".format(
                    erb.name))

        # get email template file path
        email_template = review_conf.email_notification_template_file

        # using the latest project get the all the current project contacts
        prj_contacts = ProjectContact.objects.filter(
            project=project)
        data_cus = prj_contacts.filter(contact_role__name='Data Custodian')
        data_custodians = []
        for dc in data_cus:
            given_name = dc.contact.given_name
            surname = dc.contact.surname
            email = dc.contact.email
            user_name = email
            if given_name and surname:
                user_name = '{0} {1}'.format(given_name, surname)
            data_custodians.append(user_name)

        data_retention_period = None
        for q_resp in current_request.request_question_responses.all():
            if q_resp.question.key == 'racm_data_retention_period':
                data_retention_period = q_resp.question_response

        # fetch the recipient list of emails
        recipient_list = self._get_recipient_emails(
            prj_contacts, review_conf.contact_roles.all())

        # fetch the cc list of emails
        cc_list = self._get_crams_admin_emails(
            review_conf.contact_roles.all(), erb)

        # set the email subject with project title
        subject = 'Allocation review - {}'.format(project.title)

        # get the project first provision date
        provision_date = self._get_first_provision_date(project)

        if provision_date:
            provision_date = provision_date.strftime('%Y-%m-%d %H:%M:%S')

        # setup the mail content
        mail_content = {
            "project": {"title": project.title},
            "subject": subject,
            "data_custodians": data_custodians[0],
            "provision_date": provision_date,
            "retention_period": data_retention_period,
        }

        # send the email
        email_processing_fn = get_email_processing_fn(ERB_Review_Email_fn_dict, erb)
        if email_processing_fn:
            email_processing_fn(subject=subject,
                                mail_content=mail_content,
                                template=email_template,
                                recipient_list=recipient_list,
                                cc_list=cc_list)
        # send_email_notification.delay(sender=sender,
        #                               subject=subject,
        #                               mail_content=mail_content,
        #                               template_name=email_template,
        #                               recipient_list=recipient_list,
        #                               cc_list=cc_list,
        #                               bcc_list=None,
        #                               reply_to=sender,
        #                               fail_silently=False)
        

    def _get_first_provision_date(self, current_project):
        def get_prov_dets(project):
            prj_prov_dets = ProjectProvisionDetails. \
                objects.filter(project=project,
                               provision_details__status__in=['P', 'S']) \
                .order_by('provision_details__creation_ts')
            if prj_prov_dets:
                return prj_prov_dets.first().provision_details.creation_ts
            # default to none
            return None

        # get list of children projects
        children_prj = Project.objects.filter(
            current_project=current_project).order_by('creation_ts')

        if children_prj:
            for prj in children_prj:
                provision_date = get_prov_dets(prj)
                if provision_date:
                    return provision_date

        # not found provision from the history allocation, then check the current allocation,
        return get_prov_dets(current_project)

    def _update_review(self, review_sz, request):
        # check review_date exists
        try:
            rd = review_models.ReviewDate.objects.get(pk=review_sz.get('id'))
        except ObjectDoesNotExist:
            raise exceptions.ParseError(
                'Review id: {} does not exist'.format(review_sz.get('id')))

        # check review_date status is "pending" or "failed"
        if rd.status == 'P' or rd.status == 'F':
            # check user has the correct erb admin rights to send review email
            erb = rd.request.e_research_system.e_research_body
            utils.validate_erb_admin(request.user, erb)

            # get the review date period from erb
            review_period = utils.get_erb_review_period(erb)
            next_review_date = rd.review_date + relativedelta(months=review_period)

            # send email
            self._send_email(rd, erb)

            # mark review_date status as sent
            rd.status = 'S'
            rd.updated_by = request.user
            rd.notes = review_sz.get('notes')
            rd.save()

            # create the next review_date for this project
            # next review date = review period (months) + current review_date
            review_models.ReviewDate.objects.create(
                status='P',
                review_date=next_review_date,
                request=rd.request,
                created_by=request.user,
                updated_by=request.user
            )
        else:
            raise exceptions.ParseError(
                'Can not send review for id: {}, where status is {}'.format(
                    rd.id, rd.status
                )
            )

    # validate all review status from a iterable obj to ensure they are
    # all valid for sending and id exist in db
    def _validate_review_list_status(self, review_list_sz):
        for sz in review_list_sz:
            try:
                rd = review_models.ReviewDate.objects.get(pk=sz.get('id'))
            except ObjectDoesNotExist:
                raise exceptions.ParseError(
                    'Review id {} not found'.format(sz.get('id'))
                )

            # if status is sent or skipped return error
            if rd.status == 'S' or rd.status == 'K':
                raise exceptions.ParseError(
                    'Can not send review for review id {}.'.format(rd.id)
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

            # check bulk reviews are valid for sending
            utils.validate_review_list_status(sz_data, ['P', 'F'])

            for review in serializer.data:
                self._update_review(review, request)

            return Response("Review emails sent.", status=HTTP_201_CREATED)
        else:
            rd_sz = self.get_serializer(request.data)

            try:
                rd_sz_data = rd_sz.data
            except KeyError:
                raise exceptions.ParseError(
                    'KeyError: check json format is valid'
                )

            self._update_review(rd_sz_data, request)

            return Response("Review email sent.", status=HTTP_201_CREATED)
