#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: storage_credential_info
short_description: List Unity Catalog storage credentials
description:
  - List all storage credentials in the metastore.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
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
  validate_certs:
    description: Validate SSL certificates.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: List storage credentials
  stevefulme1.databricks.storage_credential_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
"""

RETURN = r"""
credentials:
  description: List of storage credential objects.
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
        resp = client.get("unity-catalog/storage-credentials", api_version="2.1")
        module.exit_json(changed=False, credentials=resp.get("storage_credentials", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
