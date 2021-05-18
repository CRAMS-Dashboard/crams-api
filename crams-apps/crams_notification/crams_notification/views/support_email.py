from crams.models import SupportEmailContact
from crams.permissions import IsCramsAuthenticated
from crams_notification import tasks
from django.core import exceptions
from django.core.validators import validate_email
from rest_framework import exceptions as rest_exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class SupportEmailViewSet(APIView):
    """
    class SupportEmailViewSet
    """
    permission_classes = [IsCramsAuthenticated]

    def post(self, request, fail_silently=True):
        try:
            sender = request.user.email
            subject = request.data["subject"]
            body = request.data["body"]
            support_email_contact_id = request.data["support_email_contact_id"]

        except:
            return Response({"detail": "Error in email, check all fields are \
                                                    provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        # get email recipient, from e_research_body_system if provided
        # if no e_research_body_system is provided default to system email
        recipients = []

        # get the suport_email_contact
        try:
            support_email = SupportEmailContact.objects.get(pk=support_email_contact_id)
            recipients.append(support_email.email)
        except:
            raise rest_exceptions.ParseError("Can not get support email contact ID: " + support_email_contact_id)

        # check subject is not empty
        if not subject.strip():
            return Response({"detail": "Email Subject can not be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # check body is not empty
        if not body.strip():
            return Response({"detail": "Email Body can not be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # validate sender email
        try:
            validate_email(sender)
        except exceptions.ValidationError:
            return Response({"detail": "The Sender '" + sender + "' is an invalid email"},
                            status=status.HTTP_400_BAD_REQUEST)

        # validate recipient emails
        recipient = ''
        try:
            for recipient in recipients:
                validate_email(recipient)
        except exceptions.ValidationError:
            return Response({"detail": "The Recipient '" + recipient + "' is an invalid email"},
                            status=status.HTTP_400_BAD_REQUEST)

        # send email
        try:
            tasks.send_email(sender=sender, subject=subject, mail_content=body, recipient_list=recipients,
                             cc_list=[sender], fail_silently=fail_silently)

            return Response({"detail": "Support Email Sent"},
                            status=status.HTTP_200_OK)
        except exceptions:
            return Response({"detail": "Error sending support email to server, please try again later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
