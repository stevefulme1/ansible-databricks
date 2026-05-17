#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: network_connectivity_config
short_description: Manage network connectivity configuration
description:
  - Create, update, or delete network connectivity configurations.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  network_connectivity_config_id:
    description: Existing NCC ID.
    type: str
  name:
    description: NCC name.
    type: str
  region:
    description: Cloud region.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create network connectivity config
  stevefulme1.databricks.network_connectivity_config:
    host: https://accounts.cloud.databricks.com
    token: dapi0123456789abcdef
    name: my-ncc
    region: us-east-1
"""

RETURN = r"""
config:
  description: Network connectivity configuration object.
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
        network_connectivity_config_id=dict(type="str"),
        name=dict(type="str"),
        region=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ["network_connectivity_config_id"]),
        ],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    ncc_id = module.params.get("network_connectivity_config_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"accounts/network-connectivity-configs/{ncc_id}")
            module.exit_json(changed=True)

        payload = {}
        for key in ("name", "region"):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("accounts/network-connectivity-configs", data=payload)
        module.exit_json(changed=True, config=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
