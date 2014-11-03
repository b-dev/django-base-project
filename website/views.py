# -*- coding: utf-8 -*-
# Useful Links:
# http://ccbv.co.uk/
# http://django-braces.readthedocs.org/en/latest/index.html
from django.views.generic import TemplateView

class HomepageView(TemplateView):
    template_name = 'homepage.html'
