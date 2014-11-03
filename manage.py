#!/usr/bin/env python
import os
import sys
import site

if __name__ == "__main__":
    repo_path = os.path.dirname(os.path.abspath(__file__))
    site.addsitedir(repo_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
