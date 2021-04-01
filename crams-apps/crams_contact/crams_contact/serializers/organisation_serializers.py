from rest_framework import serializers

from crams_contact.models import Department, Faculty, Organisation
from crams.serializers import utilitySerializers
from crams.serializers.model_serializers import ReadOnlyModelSerializer


class ReadOnlyOrganisationSerializer(ReadOnlyModelSerializer):
    """class OrganisationSerializer."""

    class Meta(object):
        """meta Class."""
        model = Organisation
        fields = ('id', 'name', 'short_name')


class OrganisationSerializer(serializers.ModelSerializer, utilitySerializers.UpdatableSerializer):
    """class OrganisationSerializer."""

    class Meta(object):
        """meta Class."""

        model = Organisation
        fields = ['id', 'name', 'short_name', 'ands_url', 'notification_email']

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return Organisation.objects.create(**validated_data)


class FacultySerializer(serializers.ModelSerializer, utilitySerializers.UpdatableSerializer):
    """class FacultySerializer."""

    class Meta(object):
        """meta Class."""
        model = Faculty
        fields = ['id', 'faculty_code', 'name', 'organisation']

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return Faculty.objects.create(**validated_data)


class DepartmentSerializer(serializers.ModelSerializer,
                           utilitySerializers.UpdatableSerializer):
    """class DepartmentSerializer"""

    class Meta(object):
        """meta Class."""
        model = Department
        fields = ['id', 'department_code', 'name', 'faculty']

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return Department.objects.create(**validated_data)


class DepartmentListSerializer(serializers.ModelSerializer):
    """
    class DepartmentListSerializer
    Lists all department belonging to an faculty
    """
    departments = serializers.SerializerMethodField(
        method_name='get_department_list')

    class Meta(object):
        """meta Class"""
        model = Faculty
        fields = ['id', 'name', 'departments']

    # ordered by department name
    @classmethod
    def get_department_list(cls, obj):
        query_set = Department.objects.filter(
            faculty_id=obj.id).order_by('name')
        return DepartmentSerializer(query_set, many=True).data


class DepartmentParentSerializer(serializers.ModelSerializer):
    """
    class DepartmentParentSerializer
    Combines Organisation, Faculty and Department into 1
    """
    department = DepartmentSerializer
    faculty = serializers.SerializerMethodField(method_name='filter_faculty')
    organisation = \
        serializers.SerializerMethodField(method_name='filter_organisation')

    class Meta(object):
        """meta Class"""
        model = Department
        fields = ['id', 'department_code', 'name', 'faculty', 'organisation']

    @classmethod
    def filter_faculty(cls, dept_obj):
        serializer = FacultySerializer(dept_obj.faculty)

        return serializer.data

    @classmethod
    def filter_organisation(cls, dept_obj):
        serializer = OrganisationSerializer(dept_obj.faculty.organisation)

        return serializer.data
