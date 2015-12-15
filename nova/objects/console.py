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
class Console(base.NovaPersistentObject, base.NovaObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(read_only=True),
        'instance_name': fields.StringField(),
        'instance_uuid': fields.UUIDField(),
        'password': fields.StringField(),
        'port': fields.IntegerField(),
        'pool': fields.ObjectField('ConsolePool'),
    }

    @staticmethod
    def _from_db_object(context, console, db_console, expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = []
        for field in console.fields:
            if field == 'pool':
                if field in expected_attrs:
                    console.pool = objects.ConsolePool._from_db_object(
                        context, objects.ConsolePool(context),
                        db_console['pool'])
                continue
            setattr(console, field, db_console[field])
        console._context = context
        console.obj_reset_changes()
        return console

    @base.remotable
    def create(self):
        updates = self.obj_get_changes()
        pool = updates.pop('pool', None)
        if pool:
            updates['pool_id'] = pool.id
        db_console = db.console_create(self._context, updates)
        self._from_db_object(self._context, self, db_console)

    @base.remotable
    def destroy(self):
        db.console_delete(self._context, self.id)

    @base.remotable_classmethod
    def get(cls, context, console_id, instance_uuid=None, expected_attrs=None):
        if expected_attrs is None:
            expected_attrs = ['pool']
        db_console = db.console_get(context, console_id,
                                    instance_uuid=instance_uuid)
        return cls._from_db_object(context, cls(), db_console,
                                   expected_attrs=expected_attrs)


@base.NovaObjectRegistry.register
class ConsoleList(base.ObjectListBase, base.NovaObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'objects': fields.ListOfObjectsField('Console'),
    }

    @base.remotable_classmethod
    def get_by_instance(cls, context, instance_uuid, expected_attrs=None):
        db_consoles = db.console_get_all_by_instance(
            context, instance_uuid, columns_to_join=expected_attrs)
        return base.obj_make_list(context, cls(context), objects.Console,
                                  db_consoles, expected_attrs=expected_attrs)
