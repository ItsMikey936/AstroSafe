"""Crew screens.

CrewListScreen   -> prototype "Tripulants_General_View"
CrewDetailScreen -> prototype "Tripulant_View_Normal_stats"
"""
import customtkinter as ctk

from app.backend import crew_service
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
    icon,
)


# ---------------------------------------------------------------------
# Crew general view
# ---------------------------------------------------------------------
class Badge(ctk.CTkFrame):
    """Small colored box with a value and a unit (98 / SpO2)."""

    def __init__(self, master, unit: str, color: str):
        super().__init__(master, fg_color=color, width=96, height=82,
                         corner_radius=theme.SMALL_RADIUS)
        self.pack_propagate(False)
        self._value = ctk.CTkLabel(self, text="--", font=theme.font(26),
                                   text_color=theme.TEXT)
        self._value.pack(pady=(8, 0))
        ctk.CTkLabel(self, text=unit, font=theme.font(16),
                     text_color=theme.TEXT).pack()

    def set_value(self, text: str) -> None:
        self._value.configure(text=text)


class CrewCard(ClickableCard):
    """One astronaut: name, avatar, position, SpO2 and bpm."""

    def __init__(self, master, summary: CrewSummary, on_open):
        super().__init__(master, command=lambda: on_open(
            summary.astronaut_id))
        self.grid_columnconfigure((1, 2), weight=1)

        ctk.CTkLabel(self, text=summary.name, font=theme.font(22),
                     text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, columnspan=3, sticky="w",
            padx=20, pady=(14, 4))
        ctk.CTkFrame(self, height=2, fg_color=theme.TEXT_MUTED).grid(
            row=1, column=0, sticky="ew", padx=(20, 0))
        ctk.CTkLabel(self, text="",
                     image=icon("avatar", 110, fallback="avatar")).grid(
            row=2, column=0, rowspan=2, sticky="s", padx=(20, 10))
        ctk.CTkLabel(self, text=summary.position, font=theme.font(17),
                     text_color=theme.TEXT).grid(
            row=1, column=1, rowspan=2, columnspan=2, sticky="n",
            pady=(0, 6))

        self._spo2 = Badge(self, "SpO2", theme.SPO2_BADGE)
        self._spo2.grid(row=3, column=1, pady=(0, 16))
        self._bpm = Badge(self, "bpm", theme.BPM_BADGE)
        self._bpm.grid(row=3, column=2, pady=(0, 16))

        self.update_values(summary)
        self.make_clickable()

    def update_values(self, summary: CrewSummary) -> None:
        self._spo2.set_value(format_number(summary.spo2, 0))
        self._bpm.set_value(format_number(summary.bpm, 0))


class CrewListScreen(Screen):
    """All astronauts in a two-column grid. Values refresh by themselves."""

    def __init__(self, master, app):
        super().__init__(master, app)
        crew = crew_service.list_crew()
        if not crew:
            MessageView(self, "No crew members yet",
                        "Add astronauts to the database to see them "
                        "here.").pack(fill="x")
            return

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure((0, 1), weight=1, uniform="col")

        self._cards: dict[int, CrewCard] = {}
        for index, summary in enumerate(crew):
            card = CrewCard(scroll, summary, app.open_crew_detail)
            card.grid(row=index // 2, column=index % 2, sticky="ew",
                      padx=20, pady=16)
            self._cards[summary.astronaut_id] = card

        self.start_auto_refresh(self.refresh)

    def refresh(self) -> None:
        """Reload SpO2 and bpm without rebuilding the cards."""
        for summary in crew_service.list_crew():
            card = self._cards.get(summary.astronaut_id)
            if card is not None:
                card.update_values(summary)


# ---------------------------------------------------------------------
# Crew detail view
# ---------------------------------------------------------------------
class DoseRow(ctk.CTkFrame):
    """'Cumulative Dose / mSv' text next to a dose ring."""

    def __init__(self, master, title: str, unit: str):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        ctk.CTkLabel(self, text=title, font=theme.font(20),
                     text_color=theme.TEXT).grid(row=0, column=0,
                                                 sticky="s")
        ctk.CTkLabel(self, text=unit, font=theme.font(15),
                     text_color=theme.LABEL_YELLOW).grid(row=1, column=0,
                                                         sticky="n")
        self.ring = DoseRing(self)
        self.ring.grid(row=0, column=1, rowspan=2, padx=(12, 0))


class CrewDetailScreen(Screen):
    """Every health value of one astronaut."""

    def __init__(self, master, app, astronaut_id: int):
        super().__init__(master, app)
        self._astronaut_id = astronaut_id
        detail = crew_service.get_crew_detail(astronaut_id)

        back_button(self, "Back to crew", app.open_crew_list).pack(
            anchor="w", pady=(0, 8))
        if detail is None:
            MessageView(self, "Astronaut not found",
                        "This crew member is no longer in the "
                        "database.").pack(fill="x")
            return

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=400)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure((0, 1, 2), weight=1, uniform="row")

        # Left: profile and radiation doses
        profile = ProfilePanel(body, detail.name, detail.position)
        profile.grid(row=0, column=0, rowspan=3, sticky="nsew",
                     padx=(0, 20))
        ctk.CTkLabel(profile, text="Millisievert", font=theme.font(20),
                     text_color=theme.LABEL_YELLOW).pack(pady=(0, 12))
        self._cumulative = DoseRow(profile, "Cumulative Dose", "mSv")
        self._cumulative.pack(fill="x", padx=24, pady=8)
        self._daily = DoseRow(profile, "Daily Dose", "mSv/day")
        self._daily.pack(fill="x", padx=24, pady=(8, 24))

        # Right: three panels of values
        self._vitals = StatPanel(
            body,
            [("temperature", "Body Temperature"),
             ("pressure", "Intracranial Pressure")],
            theme.VALUE_BLUE)
        self._vitals.grid(row=0, column=1, sticky="nsew", pady=(0, 10))

        self._body = StatPanel(
            body,
            [("muscle", "Muscle Mass"),
             ("bone", "Bone Mineral Density")],
            theme.VALUE_TEAL)
        self._body.grid(row=1, column=1, sticky="nsew", pady=10)

        self._wellness = StatPanel(
            body,
            [("stress", "Stress Level"),
             ("fatigue", "Fatigue Level"),
             ("sleep", "Sleep Duration")],
            theme.VALUE_PURPLE)
        self._wellness.grid(row=2, column=1, sticky="nsew", pady=(10, 0))

        self._show_values(detail)
        self.start_auto_refresh(self.refresh)

    def refresh(self) -> None:
        detail = crew_service.get_crew_detail(self._astronaut_id)
        if detail is not None:
            self._show_values(detail)

    def _show_values(self, detail: CrewDetail) -> None:
        self._vitals.set_value(
            "temperature", format_with_unit(detail.body_temp_c, "°C"))
        self._vitals.set_value(
            "pressure", self._metric_text(detail, "intracranial"))
        self._body.set_value(
            "muscle", format_with_unit(detail.muscle_mass_kg, "kg"))
        self._body.set_value(
            "bone",
            format_with_unit(detail.bone_density_g_cm2, "g/cm²", 2))
        self._wellness.set_value("stress",
                                 self._metric_text(detail, "stress"))
        self._wellness.set_value("fatigue",
                                 self._metric_text(detail, "fatigue"))
        self._wellness.set_value("sleep", format_hours(detail.sleep_hours))
        self._cumulative.ring.set_value(
            format_number(detail.cumulative_dose_msv, 2))
        self._daily.ring.set_value(format_number(detail.daily_dose_msv, 2))

    @staticmethod
    def _metric_text(detail: CrewDetail, keyword: str) -> str:
        """Value + unit of a metric from the metric catalog."""
        metric = detail.metric(keyword)
        if metric is None:
            return format_number(None)
        return format_with_unit(metric.value, metric.unit)
