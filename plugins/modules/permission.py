#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: permission
short_description: Set Databricks object permissions
description:
  - Set or update permissions on workspace objects (clusters, jobs, etc.).
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  object_type:
    description: Object type (clusters, jobs, notebooks, directories, etc.).
    type: str
    required: true
  object_id:
    description: Object ID.
    type: str
    required: true
  access_control_list:
    description: List of access control entries.
    type: list
    elements: dict
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Set cluster permissions
  stevefulme1.databricks.permission:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    object_type: clusters
    object_id: 0101-010101-abcde123
    access_control_list:
      - user_name: jane@example.com
        permission_level: CAN_RESTART
"""

RETURN = r"""
permissions:
  description: Updated permissions object.
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
        object_type=dict(type="str", required=True),
        object_id=dict(type="str", required=True),
        access_control_list=dict(type="list", elements="dict", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    path = "permissions/{0}/{1}".format(
        module.params["object_type"], module.params["object_id"]
    )

    try:
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.patch(
            path,
            data={
                "access_control_list": module.params["access_control_list"],
            },
        )
        module.exit_json(changed=True, permissions=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
