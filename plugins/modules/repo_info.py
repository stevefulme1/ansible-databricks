#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: repo_info
short_description: Get Databricks Git repo details
description:
  - Retrieve details of a Databricks Git repository.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  repo_id:
    description: Repo ID to query.
    type: int
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
- name: Get repo details
  stevefulme1.databricks.repo_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    repo_id: 12345
"""

RETURN = r"""
repo:
  description: Repo details.
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
        repo_id=dict(type="int", required=True),
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
        info = client.get("repos/{}".format(module.params["repo_id"]))
        module.exit_json(changed=False, repo=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
