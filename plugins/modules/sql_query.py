#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: sql_query
short_description: Manage SQL analytics queries
description:
  - Create, update, or delete SQL analytics queries.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  query_id:
    description:
      - ID of the query to update or delete.
      - Required when state is absent.
    type: str
  name:
    description: Display name for the query.
    type: str
  description:
    description: Description of the query.
    type: str
  query_text:
    description: SQL query text.
    type: str
  warehouse_id:
    description: SQL warehouse to execute the query.
    type: str
  catalog:
    description: Default catalog for the query.
    type: str
  schema:
    description: Default schema for the query.
    type: str
  parent:
    description: Workspace path for the query location.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a SQL query
  stevefulme1.databricks.sql_query:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: Daily Revenue Report
    query_text: "SELECT date, SUM(revenue) FROM sales GROUP BY date"
    warehouse_id: abc123def456

- name: Delete a SQL query
  stevefulme1.databricks.sql_query:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    query_id: "01234567-89ab-cdef-0123-456789abcdef"
    state: absent
"""

RETURN = r"""
query:
  description: SQL query object.
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
        query_id=dict(type="str"),
        name=dict(type="str"),
        description=dict(type="str"),
        query_text=dict(type="str"),
        warehouse_id=dict(type="str"),
        catalog=dict(type="str"),
        schema=dict(type="str"),
        parent=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[("state", "absent", ["query_id"])],
        supports_check_mode=True,
    )
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    query_id = module.params.get("query_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"sql/queries/{query_id}", api_version="2.0")
            module.exit_json(changed=True)

        payload = {}
        for key in ("name", "description", "query_text", "warehouse_id", "catalog", "schema", "parent"):
            if module.params.get(key) is not None:
                payload[key] = module.params[key]

        if query_id:
            if module.check_mode:
                module.exit_json(changed=True)
            updated = client.patch(
                f"sql/queries/{query_id}",
                data=payload,
                api_version="2.0",
            )
            module.exit_json(changed=True, query=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("sql/queries", data=payload, api_version="2.0")
        module.exit_json(changed=True, query=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
