#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: repo
short_description: Manage Databricks Git repos
description:
  - Create, update, or delete Databricks Git repository integrations.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  repo_id:
    description: Existing repo ID.
    type: int
  url:
    description: Git repository URL.
    type: str
  provider:
    description: Git provider.
    type: str
    choices: [gitHub, bitbucketCloud, gitLab, azureDevOpsServices, gitHubEnterprise, bitbucketServer, gitLabEnterpriseEdition]
  path:
    description: Workspace path for the repo.
    type: str
  branch:
    description: Branch to checkout.
    type: str
  tag:
    description: Tag to checkout.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Clone a repo
  stevefulme1.databricks.repo:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    url: https://github.com/org/repo.git
    provider: gitHub
    path: /Repos/user@example.com/my-repo
"""

RETURN = r"""
repo:
  description: Repo object.
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
        repo_id=dict(type="int"),
        url=dict(type="str"),
        provider=dict(
            type="str",
            choices=[
                "gitHub",
                "bitbucketCloud",
                "gitLab",
                "azureDevOpsServices",
                "gitHubEnterprise",
                "bitbucketServer",
                "gitLabEnterpriseEdition",
            ],
        ),
        path=dict(type="str"),
        branch=dict(type="str"),
        tag=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["repo_id"])],
        mutually_exclusive=[["branch", "tag"]],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    repo_id = module.params.get("repo_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete("repos/{0}".format(repo_id))
            module.exit_json(changed=True)

        if repo_id:
            payload = {}
            if module.params.get("branch"):
                payload["branch"] = module.params["branch"]
            if module.params.get("tag"):
                payload["tag"] = module.params["tag"]
            if module.check_mode:
                module.exit_json(changed=True)
            client.patch("repos/{0}".format(repo_id), data=payload)
            info = client.get("repos/{0}".format(repo_id))
            module.exit_json(changed=True, repo=info)

        payload = {}
        for key in ("url", "provider", "path"):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("repos", data=payload)
        module.exit_json(changed=True, repo=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
