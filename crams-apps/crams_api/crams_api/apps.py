# coding=utf-8
"""

"""
import importlib
import logging
from django.apps import AppConfig
from django.conf import settings


class CramsAPIConfig(AppConfig):
    name = 'crams_api'

    def ready(self):
        print(settings.INSTALLED_APPS)
        for aspect_settings in settings.CRAMS_ASPECT_CONFIG_LIST:
            try:
                print('.... importing', aspect_settings)
                importlib.import_module(aspect_settings)  # noqa
                print('     --> import done', aspect_settings)
            except ImportError:
                print("aspect config file not found: {}".format(aspect_settings))
                logging.debug("aspect config file not found: {}".format(aspect_settings))
