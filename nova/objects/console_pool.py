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

from nova import db
from nova import objects
from nova.objects import base
from nova.objects import fields


@base.NovaObjectRegistry.register
class ConsolePool(base.NovaPersistentObject, base.NovaObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(read_only=True),
        'address': fields.IPV4AndV6AddressField(),
        'username': fields.StringField(),
        'password': fields.StringField(),
        'console_type': fields.StringField(),
        'public_hostname': fields.StringField(),
        'host': fields.StringField(),
        'compute_host': fields.StringField(),
        'consoles': fields.ObjectField('ConsoleList', read_only=True),
    }

    @staticmethod
    def _from_db_object(context, console_pool, db_console_pool,
                        expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = []
        for field in console_pool.fields:
            if field == 'consoles':
                if field in expected_attrs:
                    console_pool.consoles = base.obj_make_list(
                        context, objects.ConsoleList(context), objects.Console,
                        db_console_pool['consoles'])
                continue
            setattr(console_pool, field, db_console_pool[field])
        console_pool._context = context
        console_pool.obj_reset_changes()
        return console_pool

    @base.remotable
    def create(self):
        updates = self.obj_get_changes()
        if 'address' in updates:
            updates['address'] = str(updates['address'])
        updates['consoles'] = []
        db_console_pool = db.console_pool_create(self._context, updates)
        self._from_db_object(self._context, self, db_console_pool,
                             expected_attrs=['consoles'])

    @base.remotable_classmethod
    def get_by_host_type(cls, context, compute_host, host, console_type,
                         expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = ['consoles']
        db_console_pool = db.console_pool_get_by_host_type(
            context, compute_host, host, console_type)
        return cls._from_db_object(context, cls(), db_console_pool,
                                   expected_attrs=expected_attrs)


@base.NovaObjectRegistry.register
class ConsolePoolList(base.ObjectListBase, base.NovaObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'objects': fields.ListOfObjectsField('ConsolePool'),
    }

    @base.remotable_classmethod
    def get_by_host_type(cls, context, host, console_type,
                         expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = ['consoles']
        db_console_pools = db.console_pool_get_all_by_host_type(
            context, host, console_type)
        return base.obj_make_list(context, cls(context), objects.ConsolePool,
                                  db_console_pools,
                                  expected_attrs=expected_attrs)
