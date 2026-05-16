# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.databricks.plugins.modules import catalog


class TestCatalogDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert catalog.DOCUMENTATION

    def test_examples_exist(self):
        assert catalog.EXAMPLES

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.databricks" in catalog.EXAMPLES
