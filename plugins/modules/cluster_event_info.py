#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: cluster_event_info
short_description: Get Databricks cluster events
description:
  - Retrieve events for a specific cluster.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  cluster_id:
    description: Cluster ID to retrieve events for.
    type: str
    required: true
  limit:
    description: Maximum number of events to return.
    type: int
    default: 50
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
    offset:
        description:
            - Number of results to skip for pagination.
        type: int
        default: 0
"""

EXAMPLES = r"""
- name: Get cluster events
  stevefulme1.databricks.cluster_event_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    cluster_id: 0101-010101-abcde123
"""

RETURN = r"""
events:
  description: List of cluster events.
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
        cluster_id=dict(type="str", required=True),
        limit=dict(type="int", default=50),
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
        resp = client.post(
            "clusters/events",
            data={
                "cluster_id": module.params["cluster_id"],
                "limit": module.params["limit"],
            },
        )
        module.exit_json(changed=False, events=resp.get("events", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
