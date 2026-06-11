#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: metastore_assignment_info
short_description: Get metastore assignment for a workspace
description:
  - Retrieve the Unity Catalog metastore assignment for a workspace.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  workspace_id:
    description: Databricks workspace ID.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Get metastore assignment
  stevefulme1.databricks.metastore_assignment_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    workspace_id: "123456789"
"""

RETURN = r"""
assignment:
  description: Metastore assignment details.
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
        workspace_id=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    workspace_id = module.params["workspace_id"]

    try:
        resp = client.get(
            f"unity-catalog/workspaces/{workspace_id}/metastore",
            api_version="2.1",
        )
        module.exit_json(changed=False, assignment=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
