#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: job_run_list_info
short_description: List Databricks job runs
description:
  - List runs for a job or all runs in the workspace.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  job_id:
    description: Filter runs by job ID.
    type: int
  active_only:
    description: Only return active runs.
    type: bool
    default: false
  limit:
    description: Maximum number of runs to return.
    type: int
    default: 100
  offset:
    description: Number of results to skip for pagination.
    type: int
    default: 0
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: List runs for a job
  stevefulme1.databricks.job_run_list_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    job_id: 12345
"""

RETURN = r"""
runs:
  description: List of run objects.
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
        job_id=dict(type="int"),
        active_only=dict(type="bool", default=False),
        limit=dict(type="int", default=25),
    )
    argument_spec.update(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        params = {
            "active_only": module.params["active_only"],
            "limit": module.params["limit"],
        }
        if module.params.get("job_id"):
            params["job_id"] = module.params["job_id"]
        resp = client.get("jobs/runs/list", params=params, api_version="2.1")
        module.exit_json(changed=False, runs=resp.get("runs", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
