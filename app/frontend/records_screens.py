"""Records screens.

RecordsListScreen      -> prototype "Information_Records"
AstronautRecordsScreen -> prototype "Informacion_Records"
"""
import customtkinter as ctk

from app.backend import file_service, records_service
from app.backend.models import RecordEntry
from app.frontend import theme
from app.frontend.widgets import (
    ListCard,
    MessageView,
    ProfilePanel,
    Screen,
    back_button,
    icon,
    show_error,
)


class RecordsListScreen(Screen):
    """One card per astronaut; opening it shows their records."""

    def __init__(self, master, app):
        super().__init__(master, app)
        owners = records_service.list_record_owners()
        if not owners:
            MessageView(self, "No crew members yet",
                        "Records appear here once astronauts exist in "
                        "the database.").pack(fill="x")
            return

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        record_icon = icon("records", 110, fallback="record")
        for owner in owners:
            plural = "record" if owner.record_count == 1 else "records"
            card = ListCard(
                scroll,
                title=owner.name.upper(),
                subtitle=f"{owner.position}, "
                         f"{owner.record_count} {plural}",
                image=record_icon,
                command=lambda astronaut_id=owner.astronaut_id:
                    app.open_astronaut_records(astronaut_id),
            )
            card.pack(fill="x", padx=60, pady=14)


class AstronautRecordsScreen(Screen):
    """Voice records on the left, every other record on the right."""

    def __init__(self, master, app, astronaut_id: int):
        super().__init__(master, app)
        records = records_service.get_astronaut_records(astronaut_id)

        back_button(self, "Back to records", app.open_records).pack(
            anchor="w", pady=(0, 8))
        if records is None:
            MessageView(self, "Astronaut not found",
                        "This crew member is no longer in the "
                        "database.").pack(fill="x")
            return

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=400)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left: profile + voice records
        profile = ProfilePanel(body, records.name, records.position)
        profile.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        voice_box = ctk.CTkFrame(profile, fg_color=theme.ACCENT,
                                 corner_radius=theme.CORNER_RADIUS)
        voice_box.pack(fill="both", expand=True, padx=24, pady=(8, 24))
        ctk.CTkLabel(voice_box, text="Voice Records", font=theme.font(19),
                     text_color=theme.TEXT).pack(pady=(14, 6))
        voice_list = ctk.CTkScrollableFrame(voice_box,
                                            fg_color="transparent")
        voice_list.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        self._fill(voice_list, records.voice_records, compact=True,
                   empty_text="No voice records")

        # Right: other records
        other_panel = ctk.CTkFrame(body, fg_color=theme.SURFACE,
                                   corner_radius=theme.CORNER_RADIUS)
        other_panel.grid(row=0, column=1, sticky="nsew")
        other_list = ctk.CTkScrollableFrame(other_panel,
                                            fg_color="transparent")
        other_list.pack(fill="both", expand=True, padx=24, pady=40)
        self._fill(other_list, records.other_records, compact=False,
                   empty_text="No records yet")

    def _fill(self, master, entries: list[RecordEntry], compact: bool,
              empty_text: str) -> None:
        """Create one button per record (click opens the file)."""
        if not entries:
            ctk.CTkLabel(master, text=empty_text, font=theme.font(16),
                         text_color=theme.TEXT_MUTED).pack(pady=20)
            return
        for entry in entries:
            text = entry.record_date
            if not compact:
                text = f"{entry.record_date}    {entry.record_type}"
            ctk.CTkButton(
                master,
                text=text,
                height=60 if compact else 84,
                corner_radius=theme.SMALL_RADIUS,
                font=theme.font(18 if compact else 24),
                fg_color=theme.SURFACE if compact else theme.ACCENT,
                hover_color=theme.SURFACE_HOVER if compact
                else theme.ACCENT_HOVER,
                text_color=theme.TEXT,
                command=lambda selected=entry: self._open(selected),
            ).pack(fill="x", padx=8, pady=8 if compact else 12)

    @staticmethod
    def _open(entry: RecordEntry) -> None:
        """Open the record file with the computer's default program."""
        try:
            file_service.open_file(entry.file_path)
        except (FileNotFoundError, ValueError) as error:
            show_error("Cannot open record", str(error))
        except OSError as error:
            show_error("Cannot open record",
                       f"No program could open this file: {error}")
