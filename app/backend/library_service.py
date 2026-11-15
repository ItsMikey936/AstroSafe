"""Read items and procedure sections for the three library categories."""
from enum import Enum
from sqlite3 import Row

from app.backend.database import connect, fetch_all
from app.backend.models import LibraryDetail, LibraryItem, LibrarySection


class Category(str, Enum):
    """The categories used by the library screens."""

    DISEASES = "diseases"
    HAZARDS = "hazards"
    TREATMENTS = "treatments"


# SQL identifiers come only from this whitelist; values use placeholders.
_TABLES = {
    Category.DISEASES.value: ("disease", "disease_id"),
    Category.HAZARDS.value: ("hazard", "hazard_id"),
    Category.TREATMENTS.value: ("treatment", "treatment_id"),
}
CATEGORIES = tuple(_TABLES)


def _table_for(category: str) -> tuple[str, str]:
    try:
        return _TABLES[category]
    except (KeyError, TypeError):
        choices = ", ".join(CATEGORIES)
        raise ValueError(
            f"Unknown library category {category!r}. Choose from: {choices}"
        ) from None


def _to_item(row: Row) -> LibraryItem:
    return LibraryItem(
        item_id=row["item_id"],
        name=row["name"],
        description=row["description"],
        image_path=row["image_path"],
    )


def list_items(category: str) -> list[LibraryItem]:
    """Return the items in a category, ordered by name."""
    table, id_column = _table_for(category)
    rows = fetch_all(
        f"SELECT {id_column} AS item_id, name, description, image_path "
        f"FROM {table} ORDER BY name"
    )
    return [_to_item(row) for row in rows]


def get_item_detail(category: str, item_id: int) -> LibraryDetail | None:
    """Return the item and its ordered sections, or None if it is absent."""
    table, id_column = _table_for(category)
    section_table = f"{table}_section"
    with connect() as connection:
        row = connection.execute(
            f"SELECT {id_column} AS item_id, name, description, image_path "
            f"FROM {table} WHERE {id_column} = ?",
            (item_id,),
        ).fetchone()
        if row is None:
            return None

        section_rows = connection.execute(
            f"SELECT section_number, title, description "
            f"FROM {section_table} WHERE {id_column} = ? "
            "ORDER BY section_number",
            (item_id,),
        ).fetchall()

    sections = [
        LibrarySection(
            number=section["section_number"],
            title=section["title"],
            description=section["description"],
        )
        for section in section_rows
    ]
    return LibraryDetail(item=_to_item(row), sections=sections)


if __name__ == "__main__":
    # Quick check: python -m app.backend.library_service
    for category in CATEGORIES:
        items = list_items(category)
        print(f"{category}: {len(items)} item(s)")
        for item in items:
            print(f"  {item.item_id}: {item.name}")
        if items:
            print(get_item_detail(category, items[0].item_id))
        else:
            print("  No items found.")
