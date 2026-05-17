#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: group_info
short_description: List Databricks workspace groups
description:
  - List all groups via the SCIM API.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  filter:
    description: SCIM filter expression.
    type: str

  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: List all groups
  stevefulme1.databricks.group_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
"""

RETURN = r"""
groups:
  description: List of group objects.
  type: list
  elements: dict
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
        filter=dict(type="str"),
    )
    argument_spec.update(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        params = {}
        if module.params.get("filter"):
            params["filter"] = module.params["filter"]
        resp = client.get("preview/scim/v2/Groups", params=params)
        module.exit_json(changed=False, groups=resp.get("Resources", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
