from typing import Generic, Optional, Protocol, Sequence, Type, TypeVar
from gspread import Worksheet
from pydantic import BaseModel

from app.utils import unflatten_dict, flatten_dict

T = TypeVar("T", bound=BaseModel)


class SynchronizerStore(Protocol[T]):
    def upsert(self, item: T) -> None:
        ...

    def delete(self, item_id: str) -> bool:
        ...

    def fetch(self) -> list[T]:
        ...


class SpreadsheetSynchronizer(Generic[T]):
    def __init__(
            self,
            store: SynchronizerStore[T],
            worksheet: Worksheet,
            validation_type: Type[T],
            hide_cols: Optional[list[str]] = None,
    ):
        self.store = store
        self.worksheet = worksheet
        self.validation_type = validation_type
        self.hide_cols = hide_cols if hide_cols else []

    def get_sheet_values(self, ignore_mismatch: bool = False) -> list[T]:
        data = self.worksheet.get_all_values()
        sheet_headers = data[0]
        sheet_entries = [dict(zip(sheet_headers, row)) for row in data[1:]]

        validated_entries = []
        for e in sheet_entries:
            try:
                validated = self.validation_type.parse_obj(unflatten_dict(e))
                validated_entries.append(validated)
            except Exception as e:
                if not ignore_mismatch:
                    raise e

        return validated_entries

    def write_to_sheet(self, items: list[T]) -> None:
        data = [flatten_dict(d.dict()) for d in items]
        if len(data) == 0:
            return
        sheet_headers = list(data[0].keys())
        sheet_rows = [sheet_headers] + [list(entry.values()) for entry in data]

        range_to_update = f"A1:{chr(65 + len(sheet_headers) - 1)}{len(data) + 1}"
        self.worksheet.update(range_to_update, sheet_rows)

        # Compute the indices of the columns to hide
        hidden_col_indices = [sheet_headers.index(col) for col in self.hide_cols if col in sheet_headers]

        # Hide the computed columns
        for index in hidden_col_indices:
            self.worksheet.hide_columns(index, index + 1)

    def synchronize(self, overwrite_sheet: bool = True):
        store_items = self.store.fetch()
        sheet_items = self.get_sheet_values()

        store_item_id = set([e.id for e in store_items if e.id != ''])
        sheet_item_id = set([e.id for e in sheet_items if e.id != ''])

        items_to_upsert = [e for e in sheet_items if e.id != '']
        items_to_delete = store_item_id - store_item_id.intersection(sheet_item_id)

        for item in items_to_upsert:
            self.store.upsert(item)

        for item_id in items_to_delete:
            self.store.delete(item_id)

        if overwrite_sheet:
            all_store_items = self.store.fetch()
            self.write_to_sheet(all_store_items)
