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
from nova.tests.unit.objects import test_console_pool
from nova.tests.unit.objects import test_objects


fake_console = {
    'created_at': None,
    'updated_at': None,
    'deleted_at': None,
    'deleted': 0,
    'id': 1,
    'instance_name': 'fake-inst-name',
    'instance_uuid': 'fake-inst-uuid',
    'password': 'fake-password',
    'port': 123,
    'pool_id': 1,
    'pool': test_console_pool.fake_console_pool,
}


class _TestBase(object):
    def _pool_comparator(self, db_val, obj_val):
        self.assertIsInstance(obj_val, objects.ConsolePool)
        self.compare_obj(obj_val, db_val, allow_missing=['consoles'],
                         comparators={'address': self.str_comparator})


class _TestConsole(_TestBase):
    @mock.patch('nova.db.console_create', return_value=fake_console)
    def test_create(self, mock_create):
        console = objects.Console(context=self.context)
        console.create()
        mock_create.assert_called_once_with(self.context, {})
        self.compare_obj(console, fake_console, allow_missing=['pool'])

    @mock.patch('nova.db.console_create', return_value=fake_console)
    def test_create_with_pool(self, mock_create):
        db_pool = fake_console['pool'].copy()
        del db_pool['consoles']
        pool = objects.ConsolePool(**db_pool)
        console = objects.Console(context=self.context, pool=pool)
        console.create()
        mock_create.assert_called_once_with(self.context, {'pool_id': 1})
        self.compare_obj(console, fake_console,
                         comparators={'pool': self._pool_comparator})

    @mock.patch('nova.db.console_delete')
    def test_destroy(self, mock_delete):
        console = objects.Console(context=mock.sentinel.ctxt, id=1)
        console.destroy()
        mock_delete.assert_called_once_with(mock.sentinel.ctxt, 1)

    @mock.patch('nova.db.console_get', return_value=fake_console)
    def test_get(self, mock_get):
        console = objects.Console.get(mock.sentinel.ctxt, mock.sentinel.id,
                                      instance_uuid=mock.sentinel.uuid)
        mock_get.assert_called_once_with(mock.sentinel.ctxt, mock.sentinel.id,
                                         instance_uuid=mock.sentinel.uuid)
        self.compare_obj(console, fake_console,
                         comparators={'pool': self._pool_comparator})


class TestConsole(test_objects._LocalTest, _TestConsole):
    pass


class TestRemoteConsole(test_objects._RemoteTest, _TestConsole):
    pass


class _TestConsoleList(_TestBase):
    @mock.patch('nova.db.console_get_all_by_instance',
                return_value=[fake_console])
    def test_get_by_instance(self, mock_get):
        consoles = objects.ConsoleList.get_by_instance(
            mock.sentinel.context, mock.sentinel.uuid, expected_attrs=['pool'])
        mock_get.assert_called_once_with(
            mock.sentinel.context, mock.sentinel.uuid,
            columns_to_join=['pool'])
        self.assertEqual(1, len(consoles))
        self.compare_obj(consoles[0], fake_console,
                         comparators={'pool': self._pool_comparator})


class TestConsoleList(test_objects._LocalTest, _TestConsoleList):
    pass


class TestRemoteConsoleList(test_objects._RemoteTest, _TestConsoleList):
    pass
