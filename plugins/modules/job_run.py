#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: job_run
short_description: Trigger a Databricks job run
description:
  - Trigger a one-time run of an existing job.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  job_id:
    description: Job ID to run.
    type: int
    required: true
  notebook_params:
    description: Parameters for notebook tasks.
    type: dict
  jar_params:
    description: Parameters for JAR tasks.
    type: list
    elements: str
  python_params:
    description: Parameters for Python tasks.
    type: list
    elements: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Trigger a job run
  stevefulme1.databricks.job_run:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    job_id: 12345
    notebook_params:
      date: "2024-01-01"
"""

RETURN = r"""
run_id:
  description: The triggered run ID.
  type: int
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
        job_id=dict(type="int", required=True),
        notebook_params=dict(type="dict"),
        jar_params=dict(type="list", elements="str"),
        python_params=dict(type="list", elements="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    payload = {"job_id": module.params["job_id"]}
    for key in ("notebook_params", "jar_params", "python_params"):
        val = module.params.get(key)
        if val is not None:
            payload[key] = val

    try:
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("jobs/run-now", data=payload, api_version="2.1")
        module.exit_json(changed=True, run_id=resp.get("run_id"))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
