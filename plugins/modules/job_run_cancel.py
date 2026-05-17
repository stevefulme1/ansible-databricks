#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: job_run_cancel
short_description: Cancel a Databricks job run
description:
  - Cancel a currently active job run.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  run_id:
    description: Run ID to cancel.
    type: int
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Cancel a run
  stevefulme1.databricks.job_run_cancel:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    run_id: 67890
"""

RETURN = r"""
msg:
  description: Result message.
  type: str
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

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.check_mode:
            module.exit_json(changed=True, msg="Run would be cancelled")
        client.post(
            "jobs/runs/cancel",
            data={"run_id": module.params["run_id"]},
            api_version="2.1",
        )
        module.exit_json(changed=True, msg="Run cancelled")
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
