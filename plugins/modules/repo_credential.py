#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: repo_credential
short_description: Manage Git credentials for Databricks repos
description:
  - Create, update, or delete Git credentials used by Databricks repos.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  credential_id:
    description: Existing credential ID.
    type: int
  git_provider:
    description: Git provider name.
    type: str
  git_username:
    description: Git username.
    type: str
  personal_access_token:
    description: Personal access token for Git.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create Git credential
  stevefulme1.databricks.repo_credential:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    git_provider: gitHub
    git_username: myuser
    personal_access_token: ghp_xxxxxxxxxxxx
"""

RETURN = r"""
credential:
  description: Git credential object.
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
        credential_id=dict(type="int"),
        git_provider=dict(type="str"),
        git_username=dict(type="str"),
        personal_access_token=dict(type="str", no_log=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["credential_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    credential_id = module.params.get("credential_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"git-credentials/{credential_id}")
            module.exit_json(changed=True)

        payload = {}
        for key in ("git_provider", "git_username", "personal_access_token"):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if credential_id:
            if module.check_mode:
                module.exit_json(changed=True)
            client.patch(f"git-credentials/{credential_id}", data=payload)
            info = client.get(f"git-credentials/{credential_id}")
            module.exit_json(changed=True, credential=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("git-credentials", data=payload)
        module.exit_json(changed=True, credential=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
