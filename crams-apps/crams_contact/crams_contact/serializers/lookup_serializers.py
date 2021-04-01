from crams_contact.models import Department, Faculty, Organisation
from crams.serializers import model_serializers
from rest_framework import serializers, exceptions
from django.db.models import Q


# copy from common.serializers.lookup_serializers.py d3_prod branch
class OrganisationLookupSerializer(model_serializers.ModelLookupSerializer):
    id = serializers.IntegerField(required=False)

    name = serializers.CharField(required=False)

    short_name = serializers.CharField(required=False)

    class Meta(object):
        model = Organisation
        fields = ['id', 'name', 'short_name', 'ands_url']
        pk_fields = ['name']

    def validate(self, attrs):
        super().validate(attrs)
        self.verify_field_value('name', attrs, ignore_case=True)
        self.verify_field_value('short_name', attrs, ignore_case=True)
        if self.instance:
            return self.instance
        return attrs


class FacultyLookupSerializer(model_serializers.ReadOnlyModelSerializer):
    organisation = serializers.SlugRelatedField(
        slug_field='name', required=True, queryset=Organisation.objects.all())

    class Meta(object):
        model = Faculty
        fields = ('id', 'name', 'organisation')

    def validate(self, data):
        if 'id' not in data:
            name = data.get('name')
            organisation = data.get('organisation')
            msg = 'Error fetching Faculty {} for organisation {}'
            try:
                faculty, created = Faculty.objects.get_or_create(
                    name=name, organisation=organisation)
                return faculty
            except Faculty.DoesNotExist:
                msg = 'Faculty {} does not exist for organisation {}'
            except Faculty.MultipleObjectsReturned:
                msg = 'Faculty {} not unique for organisation {} '

            raise exceptions.ValidationError(msg.format(name, organisation))
        else:
            msg = 'Error fetching Faculty for id {}'
            pk_str = data.get('id')
            try:
                pk = int(pk_str)
                return Faculty.objects.get(pk=pk)
            except ValueError:
                msg = 'Id param must be integer, got {}'
            except Faculty.DoesNotExist:
                msg = 'Faculty does not exist for id {}'

            raise exceptions.ValidationError(msg.format(pk_str))

    @classmethod
    def lookup_obj_qs(cls, data_dict):
        qs_filter = Q()
        if 'name' in data_dict:
            qs_filter &= Q(name__iexact=data_dict.get('name').lower())

        if 'name_contains' in data_dict:
            pattern = data_dict.get('name_contains').lower()
            qs_filter &= Q(name__icontains=pattern)

        if 'organisation' in data_dict:
            org = data_dict.get('organisation')
            if isinstance(org, Organisation):
                qs_filter &= Q(organisation__in=org)
            else:
                qs_filter &= Q(organisation__name__iexact=org.lower())

        return Faculty.objects.filter(qs_filter)


class DepartmentLookupSerializer(model_serializers.ReadOnlyModelSerializer):
    faculty = FacultyLookupSerializer(required=True)

    class Meta(object):
        model = Department
        fields = ('name', 'faculty')

    def validate(self, data):
        msg = 'Error fetching Department {} for {}'
        name = data.get('name')
        faculty = data.get('faculty')
        try:
            department, created = \
                Department.objects.get_or_create(name=name, faculty=faculty)
            return department
        except Department.DoesNotExist:
            msg = 'Department {} does not exist for {}'
        except Department.MultipleObjectsReturned:
            msg = 'Department {} cannot be uniquely determined for {}'

        raise exceptions.ValidationError(msg.format(name, faculty))

    @classmethod
    def lookup_obj_qs(self, data_dict):
        qs_filter = Q()
        if 'name' in data_dict:
            qs_filter &= Q(name__iexact=data_dict.get('name').lower())

        if 'name_contains' in data_dict:
            pattern = data_dict.get('name_contains').lower()
            qs_filter &= Q(name__icontains=pattern)

        if 'faculty' in data_dict:
            faculty = data_dict.get('faculty')
            if isinstance(faculty, Faculty):
                qs_filter &= Q(faculty=faculty)
            elif isinstance(faculty, dict):
                faculty_qs = FacultyLookupSerializer.lookup_obj_qs(faculty)
                if faculty_qs.count() > 0:
                    qs_filter &= Q(faculty__in=faculty_qs)
            else:
                err_msg = 'faculty must be dict or Faculty obj'
                raise exceptions.ValidationError(err_msg)

        return Department.objects.filter(qs_filter)


class DepartmentFlatSerializer(model_serializers.ReadOnlyModelSerializer):
    department_id = serializers.IntegerField(
        source='id', required=False)

    faculty_id = serializers.IntegerField(source='faculty.id', required=False)

    organisation_id = serializers.IntegerField(
        source='faculty.organisation.id', required=False)

    department = serializers.CharField(source='name', required=True)

    faculty = serializers.CharField(source='faculty.name', required=True)

    organisation = serializers.CharField(
        source='faculty.organisation.name', required=True)

    class Meta(object):
        model = Department
        fields = ('department', 'faculty', 'organisation',
                  'organisation_id', 'faculty_id', 'department_id')

    def validate(self, data):
        faculty_dict = data['faculty']
        faculty_dict['organisation'] = faculty_dict['organisation']['name']
        serializer = DepartmentLookupSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
