# encoding: utf-8


import os


class TemplateMgr:

    def __init__(self):

        self.standard = os.path.join(os.path.dirname(__file__), "standard_data.yaml")
        self.external = os.path.join(os.path.dirname(__file__), "external_data.yaml")


template_manager = TemplateMgr()