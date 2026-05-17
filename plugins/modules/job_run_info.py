#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: job_run_info
short_description: Get Databricks job run details
description:
  - Retrieve details about a specific job run.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  run_id:
    description: Run ID.
    type: int
    required: true

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
- name: Get run details
  stevefulme1.databricks.job_run_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    run_id: 67890
"""

RETURN = r"""
run:
  description: Run object.
  type: dict
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
        run_id=dict(type="int", required=True),
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
        info = client.get(
            "jobs/runs/get",
            params={"run_id": module.params["run_id"]},
            api_version="2.1",
        )
        module.exit_json(changed=False, run=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
