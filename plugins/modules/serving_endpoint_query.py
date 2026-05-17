#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: serving_endpoint_query
short_description: Query a Databricks serving endpoint
description:
  - Send inference requests to a model serving endpoint.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Endpoint name.
    type: str
    required: true
  inputs:
    description: Input data for inference.
    type: raw
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Query a serving endpoint
  stevefulme1.databricks.serving_endpoint_query:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: fraud-model-endpoint
    inputs:
      - feature1: 0.5
        feature2: 1.2
"""

RETURN = r"""
predictions:
  description: Model predictions.
  type: raw
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
        inputs=dict(type="raw", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.check_mode:
            module.exit_json(changed=False)
        resp = client.post(
            "serving-endpoints/{}/invocations".format(module.params["name"]),
            data={"inputs": module.params["inputs"]},
        )
        module.exit_json(changed=False, predictions=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
