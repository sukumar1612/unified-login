import json
import os
from typing import Optional

import lmdb
from gspread import service_account

from app.services.genric_sheet_sync import SpreadsheetSynchronizer, SynchronizerStore
from app.services.models import User
from settings import Settings


class LMDBClient:
    def __init__(self, map_size=10485760 * 10):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "db")
        self.env = lmdb.open(self.db_path, map_size=map_size)

    def upsert(self, key, value):
        with self.env.begin(write=True) as txn:
            txn.put(key.encode(), value.encode())

    def read(self, key):
        with self.env.begin(write=False) as txn:
            value = txn.get(key.encode())
            if value is None:
                return None
            return value.decode()

    def delete(self, key):
        with self.env.begin(write=True) as txn:
            if not txn.get(key.encode()):
                raise ValueError(f"Key '{key}' doesn't exist.")
            txn.delete(key.encode())

    def fetch_all(self):
        with self.env.begin() as txn:
            with txn.cursor() as cursor:
                return [(key.decode(), value.decode()) for key, value in cursor]

    def close(self):
        if self.env:
            self.env.close()


class UserPermissionStore(SynchronizerStore):
    def __init__(self):
        self.store = LMDBClient()

    @staticmethod
    def parse_obj(json_value: str) -> User:
        return User.parse_obj(json.loads(json_value))

    def upsert(self, item: User) -> None:
        self.store.upsert(key=item.id, value=item.json())

    def delete(self, item_id: str) -> bool:
        self.store.delete(key=item_id)
        return True

    def fetch(self) -> list[User]:
        user_json = self.store.fetch_all()
        return [self.parse_obj(json_val[1]) for json_val in user_json]

    def fetch_one(self, item_id: str) -> str:
        user_json = self.store.read(key=item_id)
        if user_json:
            return json.loads(user_json)
        return "nil"

    def close(self):
        self.store.close()

    def __del__(self):
        self.store.close()


class UserPermissionSheet:
    def __init__(self, store: UserPermissionStore, settings: Settings):
        self.store = store
        self.settings = settings

    def synchronize(self):
        gspread_client = service_account("keys/key.json")
        sheet = gspread_client.open_by_key(self.settings.user_sheet_id)
        worksheet = sheet.get_worksheet(index=0)
        synchronizer = SpreadsheetSynchronizer(self.store, worksheet, User, hide_cols=[])
        synchronizer.synchronize(overwrite_sheet=False)
