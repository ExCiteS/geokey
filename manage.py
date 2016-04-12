#!/usr/bin/env python
"""Default Django manager, when using local settings."""

import os
import sys


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'local_settings.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
