#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: job_list_info
short_description: List Databricks jobs
description:
  - List all jobs in the workspace with optional name filter.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Filter jobs by name (substring match).
    type: str

    limit:
        description:
            - Maximum number of results to return.
        type: int
        default: 100
    offset:
        description:
            - Number of results to skip for pagination.
        type: int
        default: 0
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: List all jobs
  stevefulme1.databricks.job_list_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
"""

RETURN = r"""
jobs:
  description: List of job objects.
  type: list
  elements: dict
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.databricks.plugins.module_utils.databricks_client import (
    DatabricksClient,
    DatabricksError,
    databricks_argument_spec,
)


def main():
    argument_spec = databricks_argument_spec()
    argument_spec.update(
        name=dict(type="str"),
    )
    argument_spec.update(
        limit=dict(type='int', default=100),
        offset=dict(type='int', default=0),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        params = {}
        if module.params.get("name"):
            params["name"] = module.params["name"]
        jobs = list(
            client.list_paginated(
                "jobs/list", params=params, results_key="jobs", api_version="2.1"
            )
        )
        module.exit_json(changed=False, jobs=jobs)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
