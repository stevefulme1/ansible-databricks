#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: network_connectivity_config_info
short_description: Get network connectivity configuration
description:
  - Retrieve network connectivity configuration details.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  network_connectivity_config_id:
    description: NCC ID to query.
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
- name: Get NCC details
  stevefulme1.databricks.network_connectivity_config_info:
    host: https://accounts.cloud.databricks.com
    token: dapi0123456789abcdef
    network_connectivity_config_id: abc123
"""

RETURN = r"""
config:
  description: Network connectivity configuration details.
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
        network_connectivity_config_id=dict(type="str", required=True),
    )
    argument_spec.update(
        limit=dict(type='int', default=100),
        offset=dict(type='int', default=0),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        info = client.get(
            "accounts/network-connectivity-configs/{0}".format(
                module.params["network_connectivity_config_id"]
            )
        )
        module.exit_json(changed=False, config=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
