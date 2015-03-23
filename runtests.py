#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, "./geokey")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.project")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    args = sys.argv
    args.insert(1, "test")
    args.insert(2, "--nocapture")
    args.insert(3, "--nologcapture")
    args.insert(4, "-x")
    execute_from_command_line(args)
