import re

from django.core.exceptions import ValidationError


def validate_orcid(value):
    pattern = re.compile("http://orcid.org/\w{4}-\w{4}-\w{4}-\w{4}")
    https_pattern = re.compile("https://orcid.org/\w{4}-\w{4}-\w{4}-\w{4}")
    if not pattern.match(value) and not https_pattern.match(value):
        err_msg = 'required format: http://orcid.org/XXXX-XXXX-XXXX-XXXX, ' \
                  'where X is [0-9,a-z,A-Z]'
        raise ValidationError(err_msg)
    else:
        return
