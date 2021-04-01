from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from crams.utils import django_utils
from crams import permissions
from crams_contact.serializers.organisation_serializers import OrganisationSerializer
from crams_contact.serializers.organisation_serializers import FacultySerializer
from crams_contact.serializers.organisation_serializers import DepartmentSerializer
from crams_contact.serializers.organisation_serializers import DepartmentListSerializer
from crams_contact.serializers.organisation_serializers import DepartmentParentSerializer
from crams_contact.models import Department
from crams_contact.models import Faculty
from crams_contact.models import Organisation


class OrganisationViewSet(django_utils.CramsModelViewSet):
    """
    class OrganisationViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsLookupAdmin]
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer


class FacultyViewSet(django_utils.CramsModelViewSet):
    """
    class FacultyViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsLookupAdmin]
    queryset = Faculty.objects.all().order_by('name')
    serializer_class = FacultySerializer

    @action(detail=False, url_path='organisation/(?P<org_id>\d+)')
    def get_org_faculty(self, request, org_id):
        ret_val = dict()
        if org_id:
            queryset = self.queryset.filter(organisation__id=org_id)
            ret_val = self.serializer_class(queryset, many=True).data
        return Response(ret_val)


class DepartmentViewSet(django_utils.CramsModelViewSet):
    """
    class DepartmentViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsLookupAdmin]
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer

    @action(detail=False, url_path='faculty/(?P<faculty_id>\d+)')
    def get_faculty_department(self, request, faculty_id):
        ret_val = dict()
        if faculty_id:
            queryset = self.queryset.filter(faculty__id=faculty_id)
            ret_val = self.serializer_class(queryset, many=True).data
        return Response(ret_val)

# TOOD: fix base
# class FacultyListViewSet(mixins.RetrieveModelMixin,
#                          base.BaseCramsReportPrimaryKeyViewSet):
class FacultyListViewSet(mixins.RetrieveModelMixin):
    """
    class FacultyListViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated]
    queryset = Faculty.objects.none()

    @classmethod
    def build_org_data_dict(cls, org, faculty_list):
        org_data_dict = dict()
        org_data_dict['id'] = org.id
        org_data_dict['short_name'] = org.short_name
        org_data_dict['name'] = org.name
        org_data_dict['faculties'] = FacultySerializer(faculty_list,
                                                       many=True).data
        return org_data_dict

    def build_pk_view_response(self, http_request, faculty_qs):
        faculty_list = list()
        if self.pk_param:
            try:
                org = Organisation.objects.get(pk=self.pk_param)
            except Organisation.DoesNotExist:
                msg = 'Organisation with pk {} does not exists'
                raise exceptions.ValidationError(msg.format(self.pk_param))

            for f in faculty_qs:
                if f.organisation == org:
                    faculty_list.append(f)
            return Response(self.build_org_data_dict(org, faculty_list))
        return Response(dict())

    def build_view_response(self, http_request, faculty_qs):
        if hasattr(self, 'pk_param'):
            return self.build_pk_view_response(http_request, faculty_qs)

        org_faculty_dict = dict()
        for faculty in faculty_qs:
            f_list = org_faculty_dict.get(faculty.organisation)
            if not f_list:
                f_list = list()
                org_faculty_dict[faculty.organisation] = f_list
            f_list.append(faculty)

        ret_list = list()
        for org, faculty_list in org_faculty_dict.items():
            ret_list.append(self.build_org_data_dict(org, faculty_list))

        return Response(ret_list)

    def build_admin_queryset(self, qs, erbs_list):
        return Faculty.objects.all()

    def build_faculty_queryset(self, qs, contact):
        return user_utils.fetch_contact_faculties_qs(contact)

    def build_department_queryset(self, qs, contact):
        return self.queryset

    def build_organisation_queryset(self, qs, contact):
        return user_utils.fetch_contact_faculties_qs(contact)

    def build_null_role_queryset(self, qs, contact):
        return self.queryset


class DepartmentListViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin):
    """
    class DepartmentListViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsLookupAdmin]
    queryset = Faculty.objects.all()
    serializer_class = DepartmentListSerializer


class DepartmentParentViewSet(viewsets.GenericViewSet,
                              mixins.RetrieveModelMixin):
    """
    class DepartmentParentViewSet
    """
    permission_classes = [permissions.IsCramsAuthenticated,
                          permissions.IsLookupAdmin]
    queryset = Department.objects.all()
    serializer_class = DepartmentParentSerializer