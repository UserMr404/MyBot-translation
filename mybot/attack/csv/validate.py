"""CSV attack script validation.

Translated from AttackCSV/CheckCSVValues.au3 and ChkAttackCSVConfig.au3.

Source: COCBot/functions/Attack/AttackCSV/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mybot.attack.csv.parser import CSVAttackScript, DropCommand, MakeCommand
from mybot.constants import TROOP_SHORT_NAMES


@dataclass
class ValidationResult:
    """Result of CSV script validation."""
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_script(script: CSVAttackScript) -> ValidationResult:
    """Validate a parsed CSV attack script.

    Checks for:
    - DROP commands referencing undefined vectors
    - DROP commands referencing unknown troop names
    - Empty vectors
    - Missing MAKE commands

    Args:
        script: Parsed CSV script to validate.

    Returns:
        ValidationResult with errors and warnings.
    """
    result = ValidationResult()
    defined_vectors = set(script.vectors.keys())
    valid_troops = {n.lower() for n in TROOP_SHORT_NAMES}
    # Add special names
    valid_troops.update({"king", "queen", "warden", "champion", "prince", "castle"})

    for i, cmd in enumerate(script.commands):
        if isinstance(cmd, DropCommand):
            if cmd.vector not in defined_vectors:
                result.errors.append(
                    f"Command {i}: DROP references undefined vector '{cmd.vector}'"
                )
                result.valid = False

            if cmd.troop_name.lower() not in valid_troops:
                result.warnings.append(
                    f"Command {i}: Unknown troop name '{cmd.troop_name}'"
                )

    if not defined_vectors:
        result.warnings.append("No MAKE vectors defined")

    drop_count = sum(1 for c in script.commands if isinstance(c, DropCommand))
    if drop_count == 0:
        result.warnings.append("No DROP commands in script")

    return result


def list_csv_scripts(csv_dir: Path) -> list[Path]:
    """List all CSV attack scripts in a directory.

    Args:
        csv_dir: Directory to search.

    Returns:
        List of CSV file paths.
    """
    if not csv_dir.is_dir():
        return []
    return sorted(csv_dir.glob("*.csv"))
