"""CSV attack script parser translated from AttackCSV/ParseAttackCSV.au3.

Parses tab/pipe-delimited CSV attack scripts into structured commands.
Replaces AutoIt's Assign()/Eval() with a dict-based vector system.

**CRITICAL**: The original AutoIt code uses:
  Assign("ATTACKVECTOR_" & $vector_name, $data)
  Eval("ATTACKVECTOR_" & $vector_name)
These are replaced with CSVAttackScript.vectors dict.

Source: COCBot/functions/Attack/AttackCSV/ParseAttackCSV.au3

CSV Format:
  NOTE  | Description
  SIDE  | resource_type, forced_side, use_redline
  SIDEB | building_type, radius
  MAKE  | vector_name, side, num_points, offset, direction
  DROP  | vector, start_idx, end_idx, quantity, troop_name, delay_ms
  WAIT  | delay_ms
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from mybot.log import set_debug_log, set_log


@dataclass
class AttackVector:
    """A named deployment vector (set of drop points).

    Replaces Assign("ATTACKVECTOR_X", $points) in AutoIt.
    """
    name: str
    side: str = ""
    points: list[tuple[int, int]] = field(default_factory=list)
    num_points: int = 0
    offset: int = 0
    direction: str = "forward"  # "forward" or "reverse"


@dataclass
class SideConfig:
    """SIDE command configuration."""
    resource_type: str = ""  # "GOLD", "ELIXIR", "DARK"
    forced_side: str = ""
    use_redline: bool = True


@dataclass
class SideBConfig:
    """SIDEB command configuration for building targeting."""
    building_type: str = ""
    radius: int = 100


class CSVCommand:
    """Base class for CSV attack commands."""
    pass


@dataclass
class NoteCommand(CSVCommand):
    """NOTE command — comment/description."""
    text: str = ""


@dataclass
class MakeCommand(CSVCommand):
    """MAKE command — define a deployment vector."""
    vector_name: str = ""
    side: str = ""
    num_points: int = 5
    offset: int = 0
    direction: str = "forward"


@dataclass
class DropCommand(CSVCommand):
    """DROP command — deploy troops on a vector."""
    vector: str = ""
    start_index: int = 0
    end_index: int = -1  # -1 = all points
    quantity: int = 0
    troop_name: str = ""
    delay_ms: int = 0
    sleep_after: int = 0


@dataclass
class WaitCommand(CSVCommand):
    """WAIT command — delay between phases."""
    delay_ms: int = 0


class CSVAttackScript:
    """Parsed CSV attack script.

    Replaces the global variable system used by ParseAttackCSV.au3.
    All vectors are stored in self.vectors dict instead of using
    AutoIt's Assign()/Eval().
    """

    def __init__(self, path: Path | None = None) -> None:
        self.name: str = ""
        self.path: Path | None = path
        self.vectors: dict[str, AttackVector] = {}
        self.side_config: SideConfig = SideConfig()
        self.sideb_configs: list[SideBConfig] = []
        self.commands: list[CSVCommand] = []
        self.notes: list[str] = []

        if path is not None:
            self.parse(path)

    def parse(self, path: Path) -> None:
        """Parse a CSV attack script file.

        Args:
            path: Path to the CSV script file.
        """
        self.path = path
        self.name = path.stem
        self.commands.clear()
        self.vectors.clear()
        self.notes.clear()

        if not path.is_file():
            set_log(f"CSV script not found: {path}")
            return

        text = path.read_text(encoding="utf-8", errors="replace")

        for line_num, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith(";") or line.startswith("//"):
                continue

            # Split by pipe or tab
            parts = [p.strip() for p in line.replace("\t", "|").split("|")]
            if len(parts) < 2:
                continue

            cmd_type = parts[0].upper()

            try:
                if cmd_type == "NOTE":
                    note = parts[1] if len(parts) > 1 else ""
                    self.notes.append(note)
                    self.commands.append(NoteCommand(text=note))

                elif cmd_type == "SIDE":
                    self._parse_side(parts[1:])

                elif cmd_type == "SIDEB":
                    self._parse_sideb(parts[1:])

                elif cmd_type == "MAKE":
                    cmd = self._parse_make(parts[1:])
                    if cmd:
                        self.commands.append(cmd)

                elif cmd_type == "DROP":
                    cmd = self._parse_drop(parts[1:])
                    if cmd:
                        self.commands.append(cmd)

                elif cmd_type == "WAIT":
                    delay = _safe_int(parts[1]) if len(parts) > 1 else 0
                    self.commands.append(WaitCommand(delay_ms=delay))

            except Exception as e:
                set_debug_log(f"CSV parse error line {line_num}: {e}")

        set_debug_log(
            f"CSV parsed '{self.name}': {len(self.commands)} commands, "
            f"{len(self.vectors)} vectors"
        )

    def _parse_side(self, parts: list[str]) -> None:
        """Parse SIDE command."""
        self.side_config = SideConfig(
            resource_type=parts[0].upper() if len(parts) > 0 else "",
            forced_side=parts[1] if len(parts) > 1 else "",
            use_redline=parts[2].upper() != "FALSE" if len(parts) > 2 else True,
        )

    def _parse_sideb(self, parts: list[str]) -> None:
        """Parse SIDEB command."""
        self.sideb_configs.append(SideBConfig(
            building_type=parts[0] if len(parts) > 0 else "",
            radius=_safe_int(parts[1], 100) if len(parts) > 1 else 100,
        ))

    def _parse_make(self, parts: list[str]) -> MakeCommand | None:
        """Parse MAKE command — defines a deployment vector."""
        if len(parts) < 1:
            return None

        name = parts[0]
        cmd = MakeCommand(
            vector_name=name,
            side=parts[1] if len(parts) > 1 else "",
            num_points=_safe_int(parts[2], 5) if len(parts) > 2 else 5,
            offset=_safe_int(parts[3], 0) if len(parts) > 3 else 0,
            direction=parts[4].lower() if len(parts) > 4 else "forward",
        )

        # Create the vector entry (will be populated with actual points
        # during execution when the red area is available)
        self.vectors[name] = AttackVector(
            name=name,
            side=cmd.side,
            num_points=cmd.num_points,
            offset=cmd.offset,
            direction=cmd.direction,
        )

        return cmd

    def _parse_drop(self, parts: list[str]) -> DropCommand | None:
        """Parse DROP command."""
        if len(parts) < 5:
            return None

        return DropCommand(
            vector=parts[0],
            start_index=_safe_int(parts[1], 0),
            end_index=_safe_int(parts[2], -1),
            quantity=_safe_int(parts[3], 0),
            troop_name=parts[4],
            delay_ms=_safe_int(parts[5], 0) if len(parts) > 5 else 0,
            sleep_after=_safe_int(parts[6], 0) if len(parts) > 6 else 0,
        )


def _safe_int(s: str, default: int = 0) -> int:
    """Safely parse an integer string."""
    try:
        return int(s.strip())
    except (ValueError, AttributeError):
        return default
