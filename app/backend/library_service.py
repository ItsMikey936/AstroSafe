"""Library data: diseases, hazards and treatments.

The three tables have the same shape (id, name, description, image)
plus a *_section table with up to three titled sections, so one set of
functions serves all three screens.
"""
from enum import Enum

from app.backend.database import connect, fetch_all
from app.backend.models import LibraryDetail, LibraryItem, LibrarySection


class Category(str, Enum):
    """The three library screens."""

    DISEASES = "diseases"
    HAZARDS = "hazards"
    TREATMENTS = "treatments"


# Category -> (table, id column, section table).
# Table names cannot be passed as "?" parameters, so they come only
# from this fixed dictionary. Nothing typed by a user ever reaches
# the f-strings below, which keeps the queries safe.
_TABLES = {
    Category.DISEASES: ("disease", "disease_id", "disease_section"),
    Category.HAZARDS: ("hazard", "hazard_id", "hazard_section"),
    Category.TREATMENTS: ("treatment", "treatment_id", "treatment_section"),
}


def list_items(category: Category) -> list[LibraryItem]:
    """All items of one category, sorted by name."""
    table, id_column, _ = _TABLES[Category(category)]
    rows = fetch_all(
        f"SELECT {id_column} AS item_id, name, description, image_path "
        f"FROM {table} ORDER BY name"
    )
    return [_to_item(row) for row in rows]


def get_item_detail(category: Category, item_id: int) -> LibraryDetail | None:
    """One item with its sections, or None if it does not exist."""
    table, id_column, section_table = _TABLES[Category(category)]
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
            f"ORDER BY section_number",
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


def _to_item(row) -> LibraryItem:
    return LibraryItem(
        item_id=row["item_id"],
        name=row["name"],
        description=row["description"],
        image_path=row["image_path"],
    )


if __name__ == "__main__":
    # Quick check: python -m app.backend.library_service
    for category in Category:
        items = list_items(category)
        print(f"{category.value}: {len(items)} item(s)")
        if items:
            print("  ", get_item_detail(category, items[0].item_id))
