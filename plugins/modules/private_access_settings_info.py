#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: private_access_settings_info
short_description: Get private access settings
description:
  - Retrieve private access settings details.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  private_access_settings_id:
    description: Settings ID to query.
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
- name: Get private access settings
  stevefulme1.databricks.private_access_settings_info:
    host: https://accounts.cloud.databricks.com
    token: dapi0123456789abcdef
    private_access_settings_id: abc123
"""

RETURN = r"""
settings:
  description: Private access settings details.
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
        private_access_settings_id=dict(type="str", required=True),
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
        info = client.get("accounts/private-access-settings/{}".format(module.params["private_access_settings_id"]))
        module.exit_json(changed=False, settings=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
