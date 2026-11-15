"""Library screens (diseases, hazards and treatments).

LibraryListScreen   -> prototypes "Informacion_Diseases",
                       "Information_Hazard", "Informacion_Treatments"
LibraryDetailScreen -> prototype "Structure_Information_1"
"""
import customtkinter as ctk

from app import config
from app.backend import file_service, library_service
from app.backend.library_service import Category
from app.frontend import theme
from app.frontend.widgets import (
    ListCard,
    MessageView,
    Screen,
    back_button,
    load_image,
)

# Text used on each list screen.
TITLES = {
    Category.DISEASES: "Diseases",
    Category.HAZARDS: "Hazards",
    Category.TREATMENTS: "Treatments",
}


def _category_icon_path(category: Category):
    """assets/icons/diseases.png, hazards.png or treatments.png."""
    return config.ICONS_DIR / f"{category.value}.png"


def _item_image_path(relative_path: str):
    """Real path of an item's image, or None if it is not valid."""
    try:
        return file_service.resolve_path(relative_path)
    except ValueError:
        return None


class LibraryListScreen(Screen):
    """One big card per disease, hazard or treatment."""

    def __init__(self, master, app, category: Category):
        super().__init__(master, app)
        items = library_service.list_items(category)
        title = TITLES[category]

        if not items:
            MessageView(self, f"No {title.lower()} yet",
                        f"Add {title.lower()} to the database to see "
                        f"them here.").pack(fill="x")
            return

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for item in items:
            # Prototype icon for the category first; if it is missing,
            # the item's own image; if that is missing, a placeholder.
            image = load_image(
                _category_icon_path(category),
                _item_image_path(item.image_path),
                size=110,
            )
            card = ListCard(
                scroll,
                title=item.name.upper(),
                image=image,
                command=lambda item_id=item.item_id:
                    app.open_library_detail(category, item_id),
            )
            card.pack(fill="x", padx=60, pady=14)


class LibraryDetailScreen(Screen):
    """Image, title, description and up to three sections."""

    def __init__(self, master, app, category: Category, item_id: int):
        super().__init__(master, app)
        detail = library_service.get_item_detail(category, item_id)
        title = TITLES[category]

        back_button(self, f"Back to {title.lower()}",
                    lambda: app.open_library(category)).pack(
            anchor="w", pady=(0, 8))
        if detail is None:
            MessageView(self, "Item not found",
                        "It may have been removed from the "
                        "database.").pack(fill="x")
            return

        card = ctk.CTkScrollableFrame(self, fg_color=theme.SURFACE,
                                      corner_radius=theme.CORNER_RADIUS)
        card.pack(fill="both", expand=True, padx=60)
        card.grid_columnconfigure((0, 1, 2), weight=1, uniform="section")

        # Top: round image + title and description
        image = load_image(_item_image_path(detail.item.image_path),
                           size=200, circle=True, fallback="circle")
        ctk.CTkLabel(card, text="", image=image).grid(
            row=0, column=0, padx=30, pady=30, sticky="nw")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=1, columnspan=2, sticky="nsew",
                    padx=(0, 30), pady=30)
        ctk.CTkLabel(header, text=detail.item.name,
                     font=theme.font(28, "bold"), text_color=theme.TEXT,
                     wraplength=620, justify="left").pack(anchor="w")
        ctk.CTkLabel(header, text=detail.item.description,
                     font=theme.font(17), text_color=theme.TEXT,
                     wraplength=620, justify="left").pack(
            anchor="w", pady=(14, 0))

        # Bottom: the sections in three columns
        for section in detail.sections:
            column = section.number - 1
            box = ctk.CTkFrame(card, fg_color="transparent")
            box.grid(row=1, column=column, sticky="new", padx=20,
                     pady=(10, 30))
            ctk.CTkLabel(box, text=section.title, font=theme.font(21),
                         text_color=theme.TEXT, wraplength=280).pack()
            ctk.CTkLabel(box, text=section.description,
                         font=theme.font(16), text_color=theme.TEXT_MUTED,
                         wraplength=280, justify="left").pack(pady=(18, 0))
