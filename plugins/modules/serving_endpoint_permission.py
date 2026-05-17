#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: serving_endpoint_permission
short_description: Manage serving endpoint permissions
description:
  - Set permissions on a model serving endpoint.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  endpoint_id:
    description: Serving endpoint ID.
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
- name: Set endpoint permissions
  stevefulme1.databricks.serving_endpoint_permission:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    endpoint_id: abc123
    access_control_list:
      - user_name: user@example.com
        permission_level: CAN_QUERY
"""

RETURN = r"""
permissions:
  description: Updated permissions.
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
        endpoint_id=dict(type="str", required=True),
        access_control_list=dict(type="list", elements="dict", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.put(
            "permissions/serving-endpoints/{}".format(module.params["endpoint_id"]),
            data={"access_control_list": module.params["access_control_list"]},
        )
        module.exit_json(changed=True, permissions=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
