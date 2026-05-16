#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: group
short_description: Manage Databricks workspace groups
description:
  - Create, update, or delete workspace groups via the SCIM API.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  group_id:
    description: Existing SCIM group ID.
    type: str
  display_name:
    description: Group display name.
    type: str
  members:
    description: List of member dicts with C(value) (user/group ID).
    type: list
    elements: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a group
  stevefulme1.databricks.group:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    display_name: data-engineers
"""

RETURN = r"""
group:
  description: Group object.
  type: dict
  returned: when state is present
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.databricks.plugins.module_utils.databricks_client import (
    DatabricksClient,
    DatabricksError,
    databricks_argument_spec,
)


def find_group_by_name(client, name):
    """Find a group by displayName via SCIM filter."""
    resp = client.get("preview/scim/v2/Groups", params={
        "filter": 'displayName eq "{0}"'.format(name),
    })
    resources = resp.get("Resources", [])
    return resources[0] if resources else None


def main():
    argument_spec = databricks_argument_spec()
    argument_spec.update(
        state=dict(type="str", default="present", choices=["present", "absent"]),
        group_id=dict(type="str"),
        display_name=dict(type="str"),
        members=dict(type="list", elements="dict"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    group_id = module.params.get("group_id")
    display_name = module.params.get("display_name")

    try:
        existing = None
        if group_id:
            existing = client.get("preview/scim/v2/Groups/{0}".format(group_id))
        elif display_name:
            existing = find_group_by_name(client, display_name)

        if state == "absent":
            if not existing:
                module.exit_json(changed=False)
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete("preview/scim/v2/Groups/{0}".format(existing["id"]))
            module.exit_json(changed=True)

        payload = {"schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"]}
        if display_name:
            payload["displayName"] = display_name
        if module.params.get("members"):
            payload["members"] = module.params["members"]

        if existing:
            if module.check_mode:
                module.exit_json(changed=True, group=existing)
            updated = client.put(
                "preview/scim/v2/Groups/{0}".format(existing["id"]),
                data=payload)
            module.exit_json(changed=True, group=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("preview/scim/v2/Groups", data=payload)
        module.exit_json(changed=True, group=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
