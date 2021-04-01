from dictdiffer import diff
from rest_framework import serializers, exceptions

# TODO from crams_collection.models import Project
from crams.serializers import model_serializers
from crams_log.models import CramsLog


class EventLogSerializer(model_serializers.ReadOnlyModelSerializer):
    id = serializers.IntegerField()
    project_title = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    changes = serializers.SerializerMethodField()

    class Meta(object):
        model = CramsLog
        fields = ('id', 'project_title', 'event', 'changes', 'created_by', 'creation_ts')
        
    def get_project_title(self, obj):
        # prj_log = obj.project_logs.all().first()
        # if prj_log:
            # prj = Project.objects.get(pk=prj_log.crams_project_db_id)
            # return prj.title
        return 'TODO project title fetch'

        # alloc_log = obj.allocation_logs.all().first()
        # if alloc_log:
            # prj = Project.objects.get(pk=alloc_log.crams_project_db_id)
            # return prj.title
        return 'TODO alloc project title fetch'
        return None
    
    def get_event(self, obj):
        # message + action + type
        if obj:
            return obj.message + ' - ' + obj.action.name
        return None

    # TODO: once the before after json has been fixed in the db this function won't be needed
    def hack_fix_on_json_dates(self, dict_str):
        # the dict string datetime causes an syntax error when you try to convert it
        # back to a dict. this hack tries get output the date value back to a simple 
        # string so it can be converted back to a datetime obj in the dict
        import re
        # regex to find the index position of the datetime py obj
        # store index locations and values to fix_dates list
        fix_dates = []
        re_filter = "datetime.datetime\((.+?), tzinfo=\<UTC\>\)"
        for result in re.finditer(re_filter, dict_str):
            fd = [result.start(), result.end(), dict_str[result.start():result.end()]]
            fix_dates.append(fd)

        # iterate backwards through the fix dates and convert to date string
        if fix_dates:
            # init counter minus 1 coz index starts at 0
            i = len(fix_dates) - 1
            while i >= 0:
                fd = fix_dates[i]
                # convert to string date format: yyyymmddhhmmss
                d_lst = re.search(re_filter, fd[2]).group(1).split(',')
                date_str = "'{}-{}-{} {}:{}:{}:{}'".format(
                    d_lst[0].strip(),
                    d_lst[1].strip(),
                    d_lst[2].strip(),
                    d_lst[3].strip(),
                    d_lst[4].strip(),
                    d_lst[5].strip(),
                    d_lst[6].strip())

                # replace with date string
                dict_str = "".join((dict_str[:fd[0]], date_str, dict_str[fd[1]:]))
                i -= 1
        return dict_str

    def get_changes(self, obj):
        def is_filtered_field(in_result):
            for r in in_result:
                if 'id' in r:
                    return True
            return False
        
        if obj:
            if obj.before_json_data:
                try:
                    before_dict = self.hack_fix_on_json_dates(obj.before_json_data)
                    after_dict = self.hack_fix_on_json_dates(obj.after_json_data)
                    before = dict(eval(before_dict))
                    after = dict(eval(after_dict))
                except:
                    return "syntax error in before/after json in crams log id: " + str(obj.id)
                    # raise exceptions.ParseError("error: unable to convert json to dict for crams_log.id " + str(obj.id))
                    
                results = list(diff(before, after))
                
                # filter out unrelated changes from results
                results = [r for r in results if not is_filtered_field(r)]

                # formatted messages
                change_msgs = []
                for r in results:
                    if r[0] == 'change':
                        change_dict = {
                            'type': r[0],
                            'property': r[1],
                            'prev_value': r[2][0],
                            'changed_value': r[2][1]
                        }
                    else:
                        change_dict = {
                            'type': r[0],
                            'property': r[1],
                            'prev_value': None,
                            'changed_value': r[2][0]
                        }
                    change_msgs.append(change_dict)

                return change_msgs
            else:
                # new object being saved for the first time
                try:
                    result = dict(eval(obj.after_json_data))
                    return [{
                            'property': obj.type.name,
                            'prev_value': None,
                            'changed_value': [result]
                    }]
                except:
                    return "syntax error in before/after json in crams log id: " + str(obj.id)
        return None
