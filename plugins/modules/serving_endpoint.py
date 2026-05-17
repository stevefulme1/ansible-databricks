#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: serving_endpoint
short_description: Manage Databricks serving endpoints
description:
  - Create, update, or delete model serving endpoints.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Endpoint name.
    type: str
    required: true
  config:
    description: Endpoint serving configuration.
    type: dict
  tags:
    description: Endpoint tags.
    type: list
    elements: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a serving endpoint
  stevefulme1.databricks.serving_endpoint:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: fraud-model-endpoint
    config:
      served_models:
        - model_name: fraud-model
          model_version: "3"
          workload_size: Small
          scale_to_zero_enabled: true
"""

RETURN = r"""
endpoint:
  description: Serving endpoint object.
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
        name=dict(type="str", required=True),
        config=dict(type="dict"),
        tags=dict(type="list", elements="dict"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    name = module.params["name"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"serving-endpoints/{name}")
            module.exit_json(changed=True)

        payload = {"name": name}
        if module.params.get("config"):
            payload["config"] = module.params["config"]
        if module.params.get("tags"):
            payload["tags"] = module.params["tags"]

        try:
            existing = client.get(f"serving-endpoints/{name}")
            if module.check_mode:
                module.exit_json(changed=True, endpoint=existing)
            if module.params.get("config"):
                client.put(
                    f"serving-endpoints/{name}/config",
                    data={"served_models": module.params["config"].get("served_models", [])},
                )
            info = client.get(f"serving-endpoints/{name}")
            module.exit_json(changed=True, endpoint=info)
        except DatabricksError:
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.post("serving-endpoints", data=payload)
            module.exit_json(changed=True, endpoint=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
