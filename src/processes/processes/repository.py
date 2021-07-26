import json
from typing import Type, TypeVar, cast, Any, Optional

from sqlalchemy import Column, Table, Text, String
from sqlalchemy.engine import Connection

from foundation import serializing

from db_infrastructure import metadata, nanoid_generate
from processes.value_objects import ProcessId, PROCESS_ID_PREFIX, PROCESS_ID_KEYSIZE

T = TypeVar("T")


def new_process_id():
    return nanoid_generate(prefix=PROCESS_ID_PREFIX, key_size=PROCESS_ID_KEYSIZE)


process_manager_data_table = Table(
    'process_manager_data', metadata,
    Column('pid', String(60), primary_key=True),
    Column('tag', String(60)),
    Column('json', Text, nullable=False)
)


class ProcessManagerDataRepo:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get(self, process_id: ProcessId, data_cls: Type[T]) -> T:
        row = self._connection.execute(
            process_manager_data_table.select(process_manager_data_table.c.pid == process_id)
        ).first()
        return cast(T, serializing.from_json(json.loads(row.json), data_cls))

    def get_by_tag(self, tag: str, data_cls: Type[T]) -> T:
        rows = self._connection.execute(
            process_manager_data_table.select(process_manager_data_table.c.tag == tag)
        ).all()

        if len(rows) != 1:
            raise Exception('Too much proccesses have identical tag or no process found.')

        return cast(T, serializing.from_json(json.loads(rows[0].json), data_cls))

    def save(self, process_id: ProcessId, data: T) -> None:
        tag_id = getattr(data, 'tag_id', '')  # get tag from data
        data = serializing.to_json(data)

        row = self._connection.execute(
            process_manager_data_table.select(process_manager_data_table.c.pid == process_id)
        ).first()

        if row:
            self._connection.execute(
                process_manager_data_table.update(values={'json': data, 'tag': tag_id}).where(
                    process_manager_data_table.c.pid == process_id
                )
            )
        else:
            self._connection.execute(
                process_manager_data_table.insert(values={'pid': process_id, 'tag': tag_id, 'json': data})
            )
