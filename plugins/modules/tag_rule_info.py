#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: tag_rule_info
short_description: List tag enforcement rules
description:
  - Retrieve all tag enforcement rules for a Unity Catalog metastore.
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
- name: List tag enforcement rules
  stevefulme1.databricks.tag_rule_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    metastore_id: abc-123-def
"""

RETURN = r"""
tag_rules:
  description: List of tag rule objects.
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
        resp = client.get(f"unity-catalog/metastores/{metastore_id}/tag-rules")
        module.exit_json(changed=False, tag_rules=resp.get("tag_rules", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
