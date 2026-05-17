#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: schema
short_description: Manage Unity Catalog schemas
description:
  - Create, update, or delete schemas within a catalog.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Schema name.
    type: str
    required: true
  catalog_name:
    description: Parent catalog name.
    type: str
    required: true
  comment:
    description: Free-form comment.
    type: str
  properties:
    description: Key-value properties.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a schema
  stevefulme1.databricks.schema:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    catalog_name: analytics
    name: bronze
"""

RETURN = r"""
schema:
  description: Schema object.
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
        catalog_name=dict(type="str", required=True),
        comment=dict(type="str"),
        properties=dict(type="dict"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    full_name = "{}.{}".format(module.params["catalog_name"], module.params["name"])

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"unity-catalog/schemas/{full_name}", api_version="2.1")
            module.exit_json(changed=True)

        existing = None
        try:
            existing = client.get(f"unity-catalog/schemas/{full_name}", api_version="2.1")
        except DatabricksError as e:
            if e.status_code != 404:
                raise

        payload = {
            "name": module.params["name"],
            "catalog_name": module.params["catalog_name"],
        }
        if module.params.get("comment") is not None:
            payload["comment"] = module.params["comment"]
        if module.params.get("properties"):
            payload["properties"] = module.params["properties"]

        if existing:
            if module.check_mode:
                module.exit_json(changed=True, schema=existing)
            updated = client.patch(
                f"unity-catalog/schemas/{full_name}",
                data=payload,
                api_version="2.1",
            )
            module.exit_json(changed=True, schema=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("unity-catalog/schemas", data=payload, api_version="2.1")
        module.exit_json(changed=True, schema=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
