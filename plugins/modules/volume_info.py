#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: volume_info
short_description: List Unity Catalog volumes
description:
  - List all volumes in a schema.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  catalog_name:
    description: Catalog name.
    type: str
    required: true
  schema_name:
    description: Schema name.
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
- name: List volumes
  stevefulme1.databricks.volume_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    catalog_name: analytics
    schema_name: bronze
"""

RETURN = r"""
volumes:
  description: List of volume objects.
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
        catalog_name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
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
        resp = client.get(
            "unity-catalog/volumes",
            params={
                "catalog_name": module.params["catalog_name"],
                "schema_name": module.params["schema_name"],
            },
            api_version="2.1",
        )
        module.exit_json(changed=False, volumes=resp.get("volumes", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
