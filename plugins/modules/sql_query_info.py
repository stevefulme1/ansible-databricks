#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: sql_query_info
short_description: Get SQL query info
description:
  - Retrieve SQL analytics query details or list queries.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  query_id:
    description: ID of a specific query to retrieve.
    type: str
  page_size:
    description: Maximum number of queries to return.
    type: int
    default: 25
  page_token:
    description: Token for paginated results.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: List SQL queries
  stevefulme1.databricks.sql_query_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef

- name: Get a specific query
  stevefulme1.databricks.sql_query_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    query_id: "01234567-89ab-cdef-0123-456789abcdef"
"""

RETURN = r"""
query:
  description: A single SQL query object.
  type: dict
  returned: when query_id is provided
queries:
  description: List of SQL query objects.
  type: list
  elements: dict
  returned: when query_id is not provided
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
        query_id=dict(type="str"),
        page_size=dict(type="int", default=25),
        page_token=dict(type="str", no_log=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.params.get("query_id"):
            resp = client.get(
                "sql/queries/{}".format(module.params["query_id"]),
                api_version="2.0",
            )
            module.exit_json(changed=False, query=resp)
        else:
            params = {"page_size": module.params["page_size"]}
            if module.params.get("page_token"):
                params["page_token"] = module.params["page_token"]
            resp = client.get("sql/queries", params=params, api_version="2.0")
            module.exit_json(changed=False, queries=resp.get("results", []))

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
