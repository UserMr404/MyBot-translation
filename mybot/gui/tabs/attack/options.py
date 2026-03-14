"""Attack options subtab translated from Design Child Attack - Options-Attack.au3.

Attack behavior options: end battle, smart zap, drop order, CSV script selection.

Source: COCBot/GUI/MBR GUI Design Child Attack - Options-Attack.au3 (465 lines)
Source: COCBot/GUI/MBR GUI Design Child Attack - Options-Search.au3 (158 lines)
Source: COCBot/GUI/MBR GUI Design Child Attack - Deadbase Attack Scripted.au3
Source: COCBot/GUI/MBR GUI Design Child Attack - Activebase Attack Scripted.au3
Source: COCBot/GUI/MBR GUI Control Attack Scripted.au3 (614 lines)
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState
from mybot.utils.paths import get_base_dir


def _csv_attack_dir() -> Path:
    """Return the path to the CSV/Attack directory."""
    # In development: repo_root/MyBot/CSV/Attack
    # In frozen (PyInstaller): base_dir/CSV/Attack
    base = get_base_dir()
    dev_path = base / "MyBot" / "CSV" / "Attack"
    if dev_path.is_dir():
        return dev_path
    return base / "CSV" / "Attack"


def _list_csv_scripts(csv_dir: Path) -> list[str]:
    """List all CSV attack scripts (without extension) sorted alphabetically."""
    if not csv_dir.is_dir():
        return []
    return sorted(p.stem for p in csv_dir.glob("*.csv"))


def _read_csv_notes(csv_dir: Path, script_name: str) -> str:
    """Read NOTE lines from a CSV attack script."""
    if not script_name:
        return ""
    csv_path = csv_dir / f"{script_name}.csv"
    if not csv_path.is_file():
        return ""
    notes: list[str] = []
    try:
        with csv_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.strip().split("|")
                if parts and parts[0].strip().upper() == "NOTE":
                    # Join remaining parts as the note text
                    notes.append("|".join(parts[1:]).strip())
    except OSError:
        return ""
    return "\n".join(notes)


class _ScriptSelector(QGroupBox):
    """Reusable CSV script selector widget with dropdown and action buttons.

    Translated from MBR GUI Design Child Attack - Deadbase/Activebase Attack Scripted.au3.
    """

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self._csv_dir = _csv_attack_dir()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Script dropdown + action buttons row
        row = QHBoxLayout()
        self.cmb_script = QComboBox()
        self.cmb_script.setMinimumWidth(200)
        self.cmb_script.currentTextChanged.connect(self._on_script_changed)
        row.addWidget(self.cmb_script, stretch=1)

        self.btn_reload = QPushButton("Reload")
        self.btn_reload.setFixedWidth(60)
        self.btn_reload.setToolTip("Refresh script list from CSV/Attack folder")
        self.btn_reload.clicked.connect(self.reload_scripts)
        row.addWidget(self.btn_reload)

        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setFixedWidth(50)
        self.btn_edit.setToolTip("Open script in default text editor")
        self.btn_edit.clicked.connect(self._edit_script)
        row.addWidget(self.btn_edit)

        self.btn_new = QPushButton("New")
        self.btn_new.setFixedWidth(50)
        self.btn_new.setToolTip("Create a new empty CSV attack script")
        self.btn_new.clicked.connect(self._new_script)
        row.addWidget(self.btn_new)

        self.btn_copy = QPushButton("Copy")
        self.btn_copy.setFixedWidth(50)
        self.btn_copy.setToolTip("Duplicate the selected script")
        self.btn_copy.clicked.connect(self._copy_script)
        row.addWidget(self.btn_copy)

        layout.addLayout(row)

        # Redline implementation
        redline_row = QHBoxLayout()
        redline_row.addWidget(QLabel("Redline:"))
        self.cmb_redline = QComboBox()
        self.cmb_redline.addItems([
            "ImgLoc Raw Redline (default)",
            "ImgLoc Redline Drop Points",
            "Original Redline",
            "External Edges",
        ])
        redline_row.addWidget(self.cmb_redline, stretch=1)
        layout.addLayout(redline_row)

        # Dropline edge
        dropline_row = QHBoxLayout()
        dropline_row.addWidget(QLabel("Dropline:"))
        self.cmb_dropline = QComboBox()
        self.cmb_dropline.addItems([
            "Drop line fix outer corner",
            "Drop line first Redline point",
            "Full Drop line fix outer corner",
            "Full Drop line first Redline point",
            "No Drop line",
        ])
        dropline_row.addWidget(self.cmb_dropline, stretch=1)
        layout.addLayout(dropline_row)

        # Script notes display
        self.lbl_notes = QLabel("")
        self.lbl_notes.setWordWrap(True)
        self.lbl_notes.setStyleSheet(
            "QLabel { background-color: #2B2B2B; color: #CCCCCC; padding: 4px; "
            "border: 1px solid #555; font-size: 11px; }"
        )
        layout.addWidget(self.lbl_notes)

        # Populate
        self.reload_scripts()

    def reload_scripts(self) -> None:
        """Reload the script list from CSV/Attack directory."""
        self._csv_dir = _csv_attack_dir()
        current = self.cmb_script.currentText()
        self.cmb_script.blockSignals(True)
        self.cmb_script.clear()
        scripts = _list_csv_scripts(self._csv_dir)
        self.cmb_script.addItems(scripts)
        # Restore previous selection if still available
        idx = self.cmb_script.findText(current)
        if idx >= 0:
            self.cmb_script.setCurrentIndex(idx)
        self.cmb_script.blockSignals(False)
        self._on_script_changed(self.cmb_script.currentText())

    def _on_script_changed(self, name: str) -> None:
        """Update notes display when script selection changes."""
        notes = _read_csv_notes(self._csv_dir, name)
        self.lbl_notes.setText(notes if notes else "(No notes in script)")

    def _edit_script(self) -> None:
        """Open the selected script in the default text editor."""
        name = self.cmb_script.currentText()
        if not name:
            return
        path = self._csv_dir / f"{name}.csv"
        if path.is_file():
            try:
                subprocess.Popen(["xdg-open", str(path)])  # noqa: S603
            except FileNotFoundError:
                try:
                    subprocess.Popen(["notepad.exe", str(path)])  # noqa: S603
                except FileNotFoundError:
                    pass

    def _new_script(self) -> None:
        """Create a new empty CSV attack script."""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Script", "Script name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if not name.endswith(".csv"):
            name += ".csv"
        path = self._csv_dir / name
        if path.exists():
            QMessageBox.warning(self, "Exists", f"Script '{name}' already exists.")
            return
        try:
            path.write_text(
                "NOTE  |New attack script\n"
                "      |Customize this script\n",
                encoding="utf-8",
            )
        except OSError:
            return
        self.reload_scripts()
        idx = self.cmb_script.findText(path.stem)
        if idx >= 0:
            self.cmb_script.setCurrentIndex(idx)

    def _copy_script(self) -> None:
        """Duplicate the selected script."""
        name = self.cmb_script.currentText()
        if not name:
            return
        src = self._csv_dir / f"{name}.csv"
        if not src.is_file():
            return
        dest = self._csv_dir / f"{name} - Copy.csv"
        counter = 2
        while dest.exists():
            dest = self._csv_dir / f"{name} - Copy ({counter}).csv"
            counter += 1
        try:
            shutil.copy2(src, dest)
        except OSError:
            return
        self.reload_scripts()
        idx = self.cmb_script.findText(dest.stem)
        if idx >= 0:
            self.cmb_script.setCurrentIndex(idx)

    @property
    def selected_script(self) -> str:
        """Return the currently selected script name."""
        return self.cmb_script.currentText()

    def set_script(self, name: str) -> None:
        """Set the selected script by name (without extension)."""
        idx = self.cmb_script.findText(name)
        if idx >= 0:
            self.cmb_script.setCurrentIndex(idx)


class AttackOptionsSubTab(QWidget):
    """Attack behavior and options configuration."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        # ── End Battle Settings ────────────────────────────────────────
        end_group = QGroupBox("End Battle")
        end_layout = QFormLayout(end_group)

        self.cmb_end_battle = QComboBox()
        self.cmb_end_battle.addItems([
            "When All Troops Deployed",
            "On 1 Star", "On 2 Stars", "On 3 Stars",
            "At % Damage", "On Time Limit",
        ])
        end_layout.addRow("End Battle:", self.cmb_end_battle)

        self.spn_end_percent = QSpinBox()
        self.spn_end_percent.setRange(0, 100)
        self.spn_end_percent.setValue(50)
        self.spn_end_percent.setSuffix("%")
        end_layout.addRow("Damage %:", self.spn_end_percent)

        self.spn_end_time = QSpinBox()
        self.spn_end_time.setRange(10, 180)
        self.spn_end_time.setValue(60)
        self.spn_end_time.setSuffix(" sec")
        end_layout.addRow("Time Limit:", self.spn_end_time)

        self.chk_remain_troops = QCheckBox("Wait for Remaining Troops")
        end_layout.addRow(self.chk_remain_troops)

        layout.addWidget(end_group)

        # ── Smart Zap Settings ─────────────────────────────────────────
        zap_group = QGroupBox("Smart Zap")
        zap_layout = QFormLayout(zap_group)

        self.chk_smart_zap = QCheckBox("Enable Smart Zap")
        zap_layout.addRow(self.chk_smart_zap)

        self.spn_min_de = QSpinBox()
        self.spn_min_de.setRange(0, 10_000)
        self.spn_min_de.setSingleStep(100)
        self.spn_min_de.setValue(200)
        zap_layout.addRow("Min DE per Zap:", self.spn_min_de)

        self.chk_zap_after = QCheckBox("Zap After Attack (use remaining spells)")
        zap_layout.addRow(self.chk_zap_after)

        layout.addWidget(zap_group)

        # ── CSV Script Selection (Dead Base) ───────────────────────────
        self.csv_db = _ScriptSelector("Dead Base CSV Script")
        layout.addWidget(self.csv_db)

        # ── CSV Script Selection (Live Base) ───────────────────────────
        self.csv_lb = _ScriptSelector("Live Base CSV Script")
        layout.addWidget(self.csv_lb)

        # ── Drop Order ─────────────────────────────────────────────────
        drop_group = QGroupBox("Drop Order")
        drop_layout = QFormLayout(drop_group)

        self.chk_custom_drop = QCheckBox("Use Custom Drop Order")
        drop_layout.addRow(self.chk_custom_drop)

        layout.addWidget(drop_group)

        # ── Attack Timing ──────────────────────────────────────────────
        timing_group = QGroupBox("Attack Timing")
        timing_layout = QFormLayout(timing_group)

        self.spn_delay_min = QSpinBox()
        self.spn_delay_min.setRange(0, 300)
        self.spn_delay_min.setValue(0)
        self.spn_delay_min.setSuffix(" sec")
        timing_layout.addRow("Delay Between Attacks (min):", self.spn_delay_min)

        self.spn_delay_max = QSpinBox()
        self.spn_delay_max.setRange(0, 300)
        self.spn_delay_max.setValue(30)
        self.spn_delay_max.setSuffix(" sec")
        timing_layout.addRow("Delay Between Attacks (max):", self.spn_delay_max)

        self.spn_max_attacks = QSpinBox()
        self.spn_max_attacks.setRange(1, 100)
        self.spn_max_attacks.setValue(10)
        timing_layout.addRow("Max Attacks per Session:", self.spn_max_attacks)

        layout.addWidget(timing_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
