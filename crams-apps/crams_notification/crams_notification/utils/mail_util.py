from django.template.loader import get_template


# give a template name and mail content json to render the mail body message
def render_mail_content(template_name, mail_content_json):
    message = mail_content_json

    if template_name:
        template = get_template(template_name)
        message = template.render({'request': mail_content_json})
    return message
