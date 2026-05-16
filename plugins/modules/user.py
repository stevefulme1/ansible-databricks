#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: user
short_description: Manage Databricks workspace users
description:
  - Create, update, or remove workspace users via the SCIM API.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  user_id:
    description: Existing SCIM user ID. Required for updates and deletes.
    type: str
  user_name:
    description: User email / login name.
    type: str
  display_name:
    description: Display name.
    type: str
  active:
    description: Whether the user is active.
    type: bool
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a user
  stevefulme1.databricks.user:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    user_name: jane@example.com
    display_name: Jane Doe
"""

RETURN = r"""
user:
  description: User object.
  type: dict
  returned: when state is present
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.databricks.plugins.module_utils.databricks_client import (
    DatabricksClient,
    DatabricksError,
    databricks_argument_spec,
)


def find_user_by_name(client, user_name):
    """Find a user by userName via SCIM filter."""
    resp = client.get("preview/scim/v2/Users", params={
        "filter": 'userName eq "{0}"'.format(user_name),
    })
    resources = resp.get("Resources", [])
    return resources[0] if resources else None


def main():
    argument_spec = databricks_argument_spec()
    argument_spec.update(
        state=dict(type="str", default="present", choices=["present", "absent"]),
        user_id=dict(type="str"),
        user_name=dict(type="str"),
        display_name=dict(type="str"),
        active=dict(type="bool"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    user_id = module.params.get("user_id")
    user_name = module.params.get("user_name")

    try:
        existing = None
        if user_id:
            existing = client.get("preview/scim/v2/Users/{0}".format(user_id))
        elif user_name:
            existing = find_user_by_name(client, user_name)

        if state == "absent":
            if not existing:
                module.exit_json(changed=False)
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete("preview/scim/v2/Users/{0}".format(existing["id"]))
            module.exit_json(changed=True)

        payload = {"schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"]}
        if user_name:
            payload["userName"] = user_name
        if module.params.get("display_name"):
            payload["displayName"] = module.params["display_name"]
        if module.params.get("active") is not None:
            payload["active"] = module.params["active"]

        if existing:
            if module.check_mode:
                module.exit_json(changed=True, user=existing)
            updated = client.put(
                "preview/scim/v2/Users/{0}".format(existing["id"]),
                data=payload)
            module.exit_json(changed=True, user=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("preview/scim/v2/Users", data=payload)
        module.exit_json(changed=True, user=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
