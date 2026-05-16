#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: system_schema
short_description: Enable Databricks system schemas
description:
  - Enable or disable system schemas in Unity Catalog.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  metastore_id:
    description: Metastore ID.
    type: str
    required: true
  schema_name:
    description: System schema name to enable.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Enable access system schema
  stevefulme1.databricks.system_schema:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    metastore_id: abc-123-def
    schema_name: access
"""

RETURN = r"""
schema:
  description: System schema status.
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
        state=dict(type="str", default="present", choices=["present", "absent"]),
        metastore_id=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    metastore_id = module.params["metastore_id"]
    schema_name = module.params["schema_name"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(
                "unity-catalog/metastores/{0}/systemschemas/{1}".format(
                    metastore_id, schema_name
                )
            )
            module.exit_json(changed=True)

        if module.check_mode:
            module.exit_json(changed=True)
        client.put(
            "unity-catalog/metastores/{0}/systemschemas/{1}".format(
                metastore_id, schema_name
            )
        )
        module.exit_json(
            changed=True,
            schema={"metastore_id": metastore_id, "schema": schema_name},
        )
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
