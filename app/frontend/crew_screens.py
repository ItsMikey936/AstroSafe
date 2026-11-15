"""Crew screens.

CrewListScreen   -> prototype "Tripulants_General_View"
CrewDetailScreen -> prototype "Tripulant_View_Normal_stats"

Data comes from the crew service (app/backend/crew_service.py) through
the classes in app/backend/models.py; these screens never touch the
database directly.
"""
import customtkinter as ctk

from app.backend.models import CrewDetail, CrewSummary
from app.frontend import theme
from app.frontend.formatting import (
    format_hours,
    format_number,
    format_with_unit,
)
from app.frontend.widgets import (
    ClickableCard,
    DoseRing,
    MessageView,
    ProfilePanel,
    Screen,
    StatPanel,
    back_button,
    icon_image,
    image_label,
    label_text,
    make_label,
)

# Words used to find each metric in the metric catalog. A metric is
# found when its name contains the word (case, spaces and underscores
# do not matter). If the catalog uses other names (for example in
# Spanish), change them here.
METRIC_KEYWORDS = {
    "pressure": "intracranial",
    "stress": "stress",
    "fatigue": "fatigue",
}

NOT_CONNECTED_TITLE = "Crew data is not connected yet"
NOT_CONNECTED_TEXT = (
    "The crew service (app/backend/crew_service.py) could not be "
    "loaded. Check that it is merged into your branch."
)


# ---------------------------------------------------------------------
# Crew general view
# ---------------------------------------------------------------------
class Badge(ctk.CTkFrame):
    """Small colored box with a value and a unit (98 / SpO2)."""

    def __init__(self, master, unit: str, color: str):
        super().__init__(master, width=96, height=82, fg_color=color,
                         corner_radius=theme.SMALL_RADIUS)
        self.pack_propagate(False)
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(expand=True)
        self.value_label = make_label(inner, "--", 26, height=34)
        self.value_label.pack()
        make_label(inner, unit, 16, height=22).pack()

    def set_value(self, text: str) -> None:
        self.value_label.configure(text=text)

    def value(self) -> str:
        return label_text(self.value_label)


class CrewCard(ClickableCard):
    """One astronaut: name, avatar, position, SpO2 and bpm."""

    def __init__(self, master, summary: CrewSummary, command=None):
        super().__init__(master, command=command)
        self.astronaut_id = summary.astronaut_id
        self.grid_columnconfigure((1, 2), weight=1)

        self.name_label = make_label(self, summary.name, 22, anchor="w")
        self.name_label.grid(row=0, column=0, columnspan=3, sticky="w",
                             padx=(20, 28), pady=(14, 0))
        divider = ctk.CTkFrame(self, width=130, height=2,
                               fg_color=theme.DIVIDER, corner_radius=0)
        divider.grid(row=1, column=0, padx=(20, 0), pady=4)
        self.position_label = make_label(self, summary.position, 17)
        self.position_label.grid(row=1, column=1, columnspan=2)
        image_label(self, icon_image("avatar", 110, fallback="avatar")
                    ).grid(row=2, column=0, sticky="s", padx=(20, 0),
                           pady=(4, 16))

        self.spo2_badge = Badge(self, "SpO2", theme.SPO2_BADGE)
        self.bpm_badge = Badge(self, "bpm", theme.BPM_BADGE)
        self.spo2_badge.grid(row=2, column=1, pady=(4, 16))
        self.bpm_badge.grid(row=2, column=2, padx=(0, 28), pady=(4, 16))

        self.update_values(summary)
        self.bind_click_to_children()

    def update_values(self, summary: CrewSummary) -> None:
        self.spo2_badge.set_value(format_number(summary.spo2, 0))
        self.bpm_badge.set_value(format_number(summary.bpm, 0))


class CrewListScreen(Screen):
    """All astronauts in a two-column grid. Values refresh by themselves."""

    def __init__(self, app, crew_source):
        super().__init__(app)
        self._source = crew_source
        self.cards: dict[int, CrewCard] = {}

        if crew_source is None:
            MessageView(self, NOT_CONNECTED_TITLE, NOT_CONNECTED_TEXT
                        ).pack(fill="x", anchor="n")
            return

        crew = list(crew_source.list_crew())
        if not crew:
            MessageView(self, "No crew members yet",
                        "Add astronauts to the database to see them here."
                        ).pack(fill="x", anchor="n")
            return

        content = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=theme.SURFACE,
            scrollbar_button_hover_color=theme.TEXT_MUTED)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure((0, 1), weight=1, uniform="crew")
        for index, summary in enumerate(crew):
            card = CrewCard(
                content, summary,
                command=lambda astronaut_id=summary.astronaut_id:
                    app.open_crew_detail(astronaut_id))
            row, column = divmod(index, 2)
            card.grid(row=row, column=column, sticky="ew", padx=20,
                      pady=16)
            self.cards[summary.astronaut_id] = card

        self.start_auto_refresh(self.refresh)

    def refresh(self) -> None:
        """Reload SpO2 and bpm without rebuilding the cards."""
        for summary in self._source.list_crew():
            card = self.cards.get(summary.astronaut_id)
            if card is not None:
                card.update_values(summary)


# ---------------------------------------------------------------------
# Crew detail view
# ---------------------------------------------------------------------
class DoseRow(ctk.CTkFrame):
    """'Cumulative Dose / mSv' text next to a dose ring."""

    def __init__(self, master, title: str, unit: str):
        super().__init__(master, fg_color="transparent")
        text = ctk.CTkFrame(self, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True)
        make_label(text, title, 20).pack()
        make_label(text, unit, 15, theme.LABEL_YELLOW).pack()
        self.ring = DoseRing(self)
        self.ring.pack(side="right", pady=8)


class CrewDetailScreen(Screen):
    """Every health value of one astronaut."""

    def __init__(self, app, crew_source, astronaut_id: int):
        super().__init__(app)
        self._source = crew_source
        self._astronaut_id = astronaut_id
        back_button(self, "Back to crew", app.open_crew_list).pack(
            anchor="w", pady=(0, 8))

        if crew_source is None:
            MessageView(self, NOT_CONNECTED_TITLE, NOT_CONNECTED_TEXT
                        ).pack(fill="x", anchor="n")
            return
        detail = crew_source.get_crew_detail(astronaut_id)
        if detail is None:
            MessageView(self, "Astronaut not found",
                        "This crew member is no longer in the database."
                        ).pack(fill="x", anchor="n")
            return

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left: profile and radiation doses
        profile = ProfilePanel(body, detail.name, detail.position)
        profile.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        make_label(profile.body, "Millisievert", 20,
                   theme.LABEL_YELLOW).pack()
        self.cumulative = DoseRow(profile.body, "Cumulative Dose", "mSv")
        self.cumulative.pack(fill="x")
        self.daily = DoseRow(profile.body, "Daily Dose", "mSv/day")
        self.daily.pack(fill="x")

        # Right: three panels of values
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        self.vitals = StatPanel(
            right,
            [("temperature", "Body Temperature"),
             ("pressure", "Intracranial Pressure")],
            theme.VALUE_BLUE)
        self.body_panel = StatPanel(
            right,
            [("muscle", "Muscle Mass"),
             ("bone", "Bone Mineral Density")],
            theme.VALUE_TEAL)
        self.wellness = StatPanel(
            right,
            [("stress", "Stress Level"),
             ("fatigue", "Fatigue Level"),
             ("sleep", "Sleep Duration")],
            theme.VALUE_PURPLE)
        for row, panel in enumerate(
                (self.vitals, self.body_panel, self.wellness)):
            right.grid_rowconfigure(row, weight=1)
            panel.grid(row=row, column=0, sticky="nsew",
                       pady=(0 if row == 0 else 10, 0 if row == 2 else 10))

        self.show_values(detail)
        self.start_auto_refresh(self.refresh)

    def refresh(self) -> None:
        detail = self._source.get_crew_detail(self._astronaut_id)
        if detail is not None:
            self.show_values(detail)

    def show_values(self, detail: CrewDetail) -> None:
        self.vitals.set_value(
            "temperature", format_with_unit(detail.body_temp_c, "°C"))
        self.vitals.set_value("pressure", _metric_text(detail, "pressure"))
        self.body_panel.set_value(
            "muscle", format_with_unit(detail.muscle_mass_kg, "kg"))
        self.body_panel.set_value(
            "bone", format_with_unit(detail.bone_density_g_cm2, "g/cm²", 2))
        self.wellness.set_value("stress", _metric_text(detail, "stress"))
        self.wellness.set_value("fatigue", _metric_text(detail, "fatigue"))
        self.wellness.set_value("sleep", format_hours(detail.sleep_hours))
        self.cumulative.ring.set_value(
            format_number(detail.cumulative_dose_msv, 2))
        self.daily.ring.set_value(format_number(detail.daily_dose_msv, 2))


def _metric_text(detail: CrewDetail, key: str) -> str:
    """Value + unit of a metric from the metric catalog, or '--'."""
    metric = detail.metric(METRIC_KEYWORDS[key])
    if metric is None:
        return format_number(None)
    return format_with_unit(metric.value, metric.unit)
