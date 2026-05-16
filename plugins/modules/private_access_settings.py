#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: private_access_settings
short_description: Manage private access settings
description:
  - Create, update, or delete private access settings for a Databricks workspace.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  private_access_settings_id:
    description: Existing settings ID.
    type: str
  private_access_settings_name:
    description: Settings name.
    type: str
  region:
    description: Cloud region.
    type: str
  public_access_enabled:
    description: Whether public access is enabled.
    type: bool
  private_access_level:
    description: Private access level.
    type: str
    choices: [ACCOUNT, ENDPOINT]
  allowed_vpc_endpoint_ids:
    description: Allowed VPC endpoint IDs.
    type: list
    elements: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create private access settings
  stevefulme1.databricks.private_access_settings:
    host: https://accounts.cloud.databricks.com
    token: dapi0123456789abcdef
    private_access_settings_name: my-pas
    region: us-east-1
    public_access_enabled: false
"""

RETURN = r"""
settings:
  description: Private access settings object.
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
        private_access_settings_id=dict(type="str"),
        private_access_settings_name=dict(type="str"),
        region=dict(type="str"),
        public_access_enabled=dict(type="bool"),
        private_access_level=dict(type="str", choices=["ACCOUNT", "ENDPOINT"]),
        allowed_vpc_endpoint_ids=dict(type="list", elements="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["private_access_settings_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    pas_id = module.params.get("private_access_settings_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete("accounts/private-access-settings/{0}".format(pas_id))
            module.exit_json(changed=True)

        payload = {}
        for key in (
            "private_access_settings_name",
            "region",
            "public_access_enabled",
            "private_access_level",
            "allowed_vpc_endpoint_ids",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if pas_id:
            if module.check_mode:
                module.exit_json(changed=True)
            client.put(
                "accounts/private-access-settings/{0}".format(pas_id),
                data=payload,
            )
            info = client.get("accounts/private-access-settings/{0}".format(pas_id))
            module.exit_json(changed=True, settings=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("accounts/private-access-settings", data=payload)
        module.exit_json(changed=True, settings=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
