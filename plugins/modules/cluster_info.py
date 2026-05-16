#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster_info
short_description: Get Databricks cluster details
description:
  - Retrieve detailed information about a specific Databricks cluster.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  cluster_id:
    description: The cluster ID to query.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Get cluster details
  stevefulme1.databricks.cluster_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    cluster_id: 0101-010101-abcde123
"""

RETURN = r"""
cluster:
  description: Cluster details.
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
        cluster_id=dict(type="str", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        info = client.get("clusters/get",
                          params={"cluster_id": module.params["cluster_id"]})
        module.exit_json(changed=False, cluster=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
