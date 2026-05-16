#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: metastore_assignment
short_description: Assign a metastore to a workspace
description:
  - Assign or unassign a Unity Catalog metastore to a workspace.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  workspace_id:
    description: Databricks workspace ID.
    type: str
    required: true
  metastore_id:
    description: Metastore ID to assign.
    type: str
    required: true
  default_catalog_name:
    description: Default catalog name for the workspace.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Assign metastore to workspace
  stevefulme1.databricks.metastore_assignment:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    workspace_id: "123456789"
    metastore_id: abc-def-ghi
"""

RETURN = r"""
assignment:
  description: Assignment details.
  type: dict
  returned: when state is present
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
        state=dict(type="str", default="present", choices=["present", "absent"]),
        workspace_id=dict(type="str", required=True),
        metastore_id=dict(type="str", required=True),
        default_catalog_name=dict(type="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    workspace_id = module.params["workspace_id"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(
                "unity-catalog/workspaces/{0}/metastore".format(workspace_id),
                api_version="2.1")
            module.exit_json(changed=True)

        payload = {"metastore_id": module.params["metastore_id"]}
        if module.params.get("default_catalog_name"):
            payload["default_catalog_name"] = module.params["default_catalog_name"]

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.put(
            "unity-catalog/workspaces/{0}/metastore".format(workspace_id),
            data=payload, api_version="2.1")
        module.exit_json(changed=True, assignment=resp)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
