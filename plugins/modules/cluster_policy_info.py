#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster_policy_info
short_description: List Databricks cluster policies
description:
  - Retrieve all cluster policies in the workspace.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
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
"""

EXAMPLES = r"""
- name: List cluster policies
  stevefulme1.databricks.cluster_policy_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
"""

RETURN = r"""
policies:
  description: List of cluster policy objects.
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
        limit=dict(type='int', default=100),
        offset=dict(type='int', default=0),
    )
    module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True
    )
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        resp = client.get("policies/clusters/list")
        module.exit_json(changed=False, policies=resp.get("policies", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
