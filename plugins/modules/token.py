#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: token
short_description: Manage Databricks personal access tokens
description:
  - Create or revoke personal access tokens.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  token_id:
    description: Token ID to revoke. Required for absent.
    type: str
  comment:
    description: Comment for the new token.
    type: str
  lifetime_seconds:
    description: Token lifetime in seconds. -1 for no expiry.
    type: int
    default: 7776000
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a token
  stevefulme1.databricks.token:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    comment: CI/CD token
    lifetime_seconds: 86400
"""

RETURN = r"""
token_value:
  description: The token string (only on creation).
  type: str
  returned: when state is present
token_info:
  description: Token metadata.
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
        token_id=dict(type="str", no_log=False),
        comment=dict(type="str"),
        lifetime_seconds=dict(type="int", default=7776000),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["token_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("token/delete", data={"token_id": module.params["token_id"]})
            module.exit_json(changed=True)

        payload = {"lifetime_seconds": module.params["lifetime_seconds"]}
        if module.params.get("comment"):
            payload["comment"] = module.params["comment"]

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("token/create", data=payload)
        module.exit_json(
            changed=True,
            token_value=resp.get("token_value"),
            token_info=resp.get("token_info"),
        )

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
