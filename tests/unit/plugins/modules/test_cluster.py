# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.stevefulme1.databricks.plugins.modules import cluster


class TestClusterDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert cluster.DOCUMENTATION

    def test_documentation_has_cluster_name(self):
        assert "cluster_name" in cluster.DOCUMENTATION or "name" in cluster.DOCUMENTATION

    def test_documentation_has_state(self):
        assert "state" in cluster.DOCUMENTATION

    def test_examples_exist(self):
        assert cluster.EXAMPLES

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.databricks" in cluster.EXAMPLES

    def test_return_exists(self):
        assert cluster.RETURN
