#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: serving_endpoint_config
short_description: Update serving endpoint configuration
description:
  - Update the served models configuration of a serving endpoint.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Endpoint name.
    type: str
    required: true
  served_models:
    description: List of served model configurations.
    type: list
    elements: dict
    required: true
  traffic_config:
    description: Traffic routing configuration.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Update endpoint config
  stevefulme1.databricks.serving_endpoint_config:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: fraud-model-endpoint
    served_models:
      - model_name: fraud-model
        model_version: "4"
        workload_size: Medium
"""

RETURN = r"""
config:
  description: Updated endpoint configuration.
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
        name=dict(type="str", required=True),
        served_models=dict(type="list", elements="dict", required=True),
        traffic_config=dict(type="dict"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        payload = {"served_models": module.params["served_models"]}
        if module.params.get("traffic_config"):
            payload["traffic_config"] = module.params["traffic_config"]
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.put(
            "serving-endpoints/{}/config".format(module.params["name"]),
            data=payload,
        )
        module.exit_json(changed=True, config=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
