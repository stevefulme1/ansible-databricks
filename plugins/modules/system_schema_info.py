#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: system_schema_info
short_description: List enabled system schemas
description:
  - Retrieve all enabled system schemas in Unity Catalog for a metastore.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  metastore_id:
    description: Metastore ID.
    type: str
    required: true
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
- name: List enabled system schemas
  stevefulme1.databricks.system_schema_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    metastore_id: abc-123-def
"""

RETURN = r"""
system_schemas:
  description: List of enabled system schema names.
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
        metastore_id=dict(type="str", required=True),
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    metastore_id = module.params["metastore_id"]

    try:
        resp = client.get(f"unity-catalog/metastores/{metastore_id}/systemschemas")
        module.exit_json(changed=False, system_schemas=resp.get("schemas", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
