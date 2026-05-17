#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: secret_scope_info
short_description: List Databricks secret scopes
description:
  - List all secret scopes in the workspace.
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
- name: List secret scopes
  stevefulme1.databricks.secret_scope_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
"""

RETURN = r"""
scopes:
  description: List of secret scope objects.
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
        resp = client.get("secrets/scopes/list")
        module.exit_json(changed=False, scopes=resp.get("scopes", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
