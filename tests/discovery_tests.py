# unit tests for src/dbxdeployer/planning/discovery.py
import pytest # type: ignore
from dbxdeployer.planning.discovery import discover_deployments


def test_discover_deployments_directory_not_found(tmp_path):
    missing_dir = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        discover_deployments(missing_dir)


def test_discover_deployments_empty_directory(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()

    deployments = discover_deployments(migrations_dir)
    assert deployments == []


def test_discover_valid_deployments(tmp_path):
    # Create a temporary migrations directory with valid deployment files
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "V000001__first.sql").write_text("-- First SQL")
    (migrations_dir / "V000002__second.sql").write_text("-- Second SQL")
    (migrations_dir / "V000003__third.sql").write_text("-- Third SQL")

    deployments = discover_deployments(migrations_dir)

    assert len(deployments) == 3

    assert [d.deployment_id for d in deployments] == ["V000001", "V000002", "V000003"]
    assert [d.version for d in deployments] == [1, 2, 3]
    assert [d.description for d in deployments] == ["first", "second", "third"]


# validate invalid deployment file names
def test_discover_deployments_invalid_file_names(tmp_path):
    # Create a temporary migrations directory with invalid file names
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "invalid_file.sql").write_text("-- Invalid SQL")
    (migrations_dir / "V000001__valid.sql").write_text("-- Valid SQL")

    with pytest.raises(ValueError) as excinfo:
        discover_deployments(migrations_dir)
    assert "Invalid deployment file discovered" in str(excinfo.value)


# validate duplicate deployment IDs
def test_discover_deployments_duplicate_ids(tmp_path):
    # Create a temporary migrations directory with duplicate deployment IDs
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "V000001__first.sql").write_text("-- First SQL")
    (migrations_dir / "V000001__second.sql").write_text("-- Second SQL")

    with pytest.raises(ValueError) as excinfo:
        discover_deployments(migrations_dir)
    assert "Duplicate deployment IDs found" in str(excinfo.value)
    assert "V000001" in str(excinfo.value)


# validate gaps in deployment versions
def test_discover_deployments_missing_versions(tmp_path):
    # Create a temporary migrations directory with missing deployment versions
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "V000001__first.sql").write_text("-- First SQL")
    (migrations_dir / "V000003__third.sql").write_text("-- Third SQL")

    with pytest.raises(ValueError) as excinfo:
        discover_deployments(migrations_dir)
    assert "V000002" in str(excinfo.value)