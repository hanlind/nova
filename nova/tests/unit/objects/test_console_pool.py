#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from nova import objects
from nova.tests.unit.objects import test_objects


fake_console_pool = {
    'created_at': None,
    'updated_at': None,
    'deleted_at': None,
    'deleted': 0,
    'id': 1,
    'address': '127.0.0.1',
    'username': 'fake-username',
    'password': 'fake-password',
    'console_type': 'fake-type',
    'public_hostname': 'fake-hostname',
    'host': 'fake-host',
    'compute_host': 'fake-compute-host',
    'consoles': [],
}


class _TestBase(object):
    def _consoles_comparator(self, db_list_obj, obj_list):
        self.assertIsInstance(obj_list, objects.ConsoleList)
        self.assertEqual(len(db_list_obj), len(obj_list))


class _TestConsolePool(_TestBase):
    @mock.patch('nova.db.console_pool_create', return_value=fake_console_pool)
    def test_create(self, mock_create):
        console_pool = objects.ConsolePool(context=self.context)
        console_pool.create()
        mock_create.assert_called_once_with(self.context, {'consoles': []})
        self.compare_obj(console_pool, fake_console_pool,
                         comparators={'address': self.str_comparator,
                                      'consoles': self._consoles_comparator})

    @mock.patch('nova.db.console_pool_get_by_host_type',
                return_value=fake_console_pool)
    def test_get_by_host_type(self, mock_get):
        console_pool = objects.ConsolePool.get_by_host_type(
            mock.sentinel.ctxt, mock.sentinel.compute, mock.sentinel.host,
            mock.sentinel.type)
        mock_get.assert_called_once_with(
            mock.sentinel.ctxt, mock.sentinel.compute, mock.sentinel.host,
            mock.sentinel.type)
        self.compare_obj(console_pool, fake_console_pool,
                         comparators={'address': self.str_comparator,
                                      'consoles': self._consoles_comparator})


class TestConsolePool(test_objects._LocalTest, _TestConsolePool):
    pass


class TestRemoteConsolePool(test_objects._RemoteTest, _TestConsolePool):
    pass


class _TestConsolePoolList(_TestBase):
    @mock.patch('nova.db.console_pool_get_all_by_host_type',
                return_value=[fake_console_pool])
    def test_get_by_host_type(self, mock_get):
        console_pools = objects.ConsolePoolList.get_by_host_type(
            mock.sentinel.context, mock.sentinel.host, mock.sentinel.type)
        mock_get.assert_called_once_with(
            mock.sentinel.context, mock.sentinel.host, mock.sentinel.type)
        self.assertEqual(1, len(console_pools))
        self.compare_obj(console_pools[0], fake_console_pool,
                         comparators={'address': self.str_comparator,
                                      'consoles': self._consoles_comparator})


class TestConsolePoolList(test_objects._LocalTest, _TestConsolePoolList):
    pass


class TestRemoteConsolePoolList(test_objects._RemoteTest,
                                _TestConsolePoolList):
    pass
