# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  host:
    description:
      - The Databricks workspace URL, e.g. C(https://adb-123.4.azuredatabricks.net).
    type: str
    required: true
  token:
    description:
      - Personal access token or service principal token for authentication.
    type: str
    required: true
    no_log: true
  validate_certs:
    description:
      - Whether to validate SSL certificates.
    type: bool
    default: true
"""
