# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.databricks.plugins.modules import user


class TestUserDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert user.DOCUMENTATION

    def test_documentation_has_user_name(self):
        assert "user_name" in user.DOCUMENTATION or "name" in user.DOCUMENTATION

    def test_examples_exist(self):
        assert user.EXAMPLES

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.databricks" in user.EXAMPLES
