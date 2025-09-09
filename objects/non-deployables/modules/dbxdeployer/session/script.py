import dataclasses
import re
from abc import ABC
from pathlib import Path
from typing import ClassVar, Literal, Pattern, TypeVar, Optional

T = TypeVar("T", bound="Script")


@dataclasses.dataclass(frozen=True, kw_only=True)
class Script(ABC):
    pattern: ClassVar[Pattern[str]]
    type: ClassVar[Literal["S", "A"]]
    name: str
    object: str
    file_path: Path
    description: str
    operation: Optional[str] = None

    @classmethod
    def from_path(cls, file_path: Path, **kwargs):
        name = file_path.name
        name_parts = cls.pattern.search(file_path.name.strip())
        description = name_parts.group("description").replace("_", " ")

        return cls(
            name=name
            , file_path=file_path
            , description=description
            , **kwargs
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SqlScript(Script):
    pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^(S)(?P<version>.+?)_(?P<object>.+?)__(?P<description>.+)\."
        , re.IGNORECASE
    )
    type: ClassVar[Literal["S"]] = "S"
    version: str
    object: str

    @classmethod
    def from_path(cls, file_path: Path, **kwargs):
        name_parts = cls.pattern.search(file_path.name.strip())

        return super().from_path(
            file_path = file_path
            , version = name_parts.group("version")
            , object = name_parts.group("object")
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ApiConfigs(Script):
    pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^(A)(?P<version>.+?)?_(?P<object>.+?)_(?P<operation>.+?)__(?P<description>.+)\."
        , re.IGNORECASE
    )
    type: ClassVar[Literal["A"]] = "A"
    version: str
    object: str
    operation: str

    @classmethod
    def from_path(cls, file_path: Path, **kwargs):
        name_parts = cls.pattern.search(file_path.name.strip())

        return super().from_path(
            file_path = file_path
            , version = name_parts.group("version")
            , object = name_parts.group("object")
            , operation = name_parts.group("operation")
        )


def script_factory(file_path: Path):
    if SqlScript.pattern.search(file_path.name.strip()) is not None:
        return SqlScript.from_path(file_path=file_path)
    
    elif ApiConfigs.pattern.search(file_path.name.strip()) is not None:
        return ApiConfigs.from_path(file_path=file_path)
    else:
        raise ValueError("No match found.")


def get_all_scripts_recursively(root_dir: Path):
    all_files = []

    for entry in root_dir.iterdir():
        if entry.is_file():
            file_path = Path(entry)
            print(file_path)
            script = script_factory(file_path=file_path)
            if script is not None:
                all_files.append(script)
        elif entry.is_dir():
            sub_files = get_all_scripts_recursively(entry)
            all_files.extend(sub_files)
    
    return all_files