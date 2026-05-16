#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ip_access_list
short_description: Manage Databricks IP access lists
description:
  - Create, update, or delete IP access lists.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  list_id:
    description: Existing list ID. Required for update and delete.
    type: str
  label:
    description: Human-readable label.
    type: str
  list_type:
    description: List type.
    type: str
    choices: [ALLOW, BLOCK]
    default: ALLOW
  ip_addresses:
    description: List of IP addresses or CIDR ranges.
    type: list
    elements: str
  enabled:
    description: Whether the list is enabled.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create an IP allow list
  stevefulme1.databricks.ip_access_list:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    label: office-ips
    ip_addresses:
      - 203.0.113.0/24
"""

RETURN = r"""
ip_access_list:
  description: IP access list object.
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
        list_id=dict(type="str"),
        label=dict(type="str"),
        list_type=dict(type="str", default="ALLOW", choices=["ALLOW", "BLOCK"]),
        ip_addresses=dict(type="list", elements="str"),
        enabled=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["list_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    list_id = module.params.get("list_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete("ip-access-lists/{0}".format(list_id))
            module.exit_json(changed=True)

        payload = {
            "list_type": module.params["list_type"],
            "enabled": module.params["enabled"],
        }
        if module.params.get("label"):
            payload["label"] = module.params["label"]
        if module.params.get("ip_addresses"):
            payload["ip_addresses"] = module.params["ip_addresses"]

        if list_id:
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.put("ip-access-lists/{0}".format(list_id), data=payload)
            module.exit_json(changed=True, ip_access_list=resp)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("ip-access-lists", data=payload)
        module.exit_json(changed=True, ip_access_list=resp)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
