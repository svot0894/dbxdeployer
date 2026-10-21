# unit tests for src/dbxdeployer/planning/planner.py

from pathlib import Path

from dbxdeployer.planning.planner import create_deployment_plan
from dbxdeployer.domain.deployment import Deployment
from dbxdeployer.domain.deployment_plan import DeploymentStatus, DeploymentPlan
from dbxdeployer.domain.deployment_history import DeploymentHistoryEntry


def create_deployment(
        deployment_id: str,
        version: int,
        description: str,
        checksum: str
) -> Deployment:
    return Deployment(
        deployment_id=deployment_id,
        version=version,
        description=description,
        file_path=Path(f"migrations/{deployment_id}__{description}.sql"),
        checksum=checksum
    )

def create_deployment_history_entry(
        deployment_id: str,
        version: int,
        checksum: str
) -> DeploymentHistoryEntry:
    return DeploymentHistoryEntry(
        deployment_id=deployment_id,
        version=version,
        checksum=checksum
    ) 


# Test the create_deployment_plan function
def test_create_deployment_plan_with_empty_list():
    plan = create_deployment_plan([], [])
    assert isinstance(plan, DeploymentPlan)
    assert plan.planned_deployments == ()


# Test the create_deployment_plan function with a single deployment
def test_create_deployment_plan_with_single_deployment():
    deployments = create_deployment(
        deployment_id="V000001",
        version=1,
        description="initial_deployment",
        checksum="initial_checksum"
    )

    plan = create_deployment_plan([deployments], [])

    assert len(plan.planned_deployments) == 1

    planned_deployment = plan.planned_deployments[0]
    assert planned_deployment.deployment == deployments
    assert planned_deployment.status == DeploymentStatus.PENDING


# Test the create_deployment_plan function with multiple deployments
def test_create_deployment_plan_with_multiple_deployments():
    deployments = [
        create_deployment(
            deployment_id="V000001",
            version=1,
            description="initial_deployment",
            checksum="initial_checksum"
        ),
        create_deployment(
            deployment_id="V000002",
            version=2,
            description="second_deployment",
            checksum="second_checksum"
        ),
        create_deployment(
            deployment_id="V000003",
            version=3,
            description="third_deployment",
            checksum="third_checksum"
        )
    ]
    plan = create_deployment_plan(deployments, [])

    assert len(plan.planned_deployments) == 3

    assert [plan.deployment_id for plan in plan.planned_deployments] == ["V000001", "V000002", "V000003"]
    assert all(plan.status == DeploymentStatus.PENDING for plan in plan.planned_deployments)


# Test the create_deployment_plan function with all possible cases
def test_create_deployment_plan_with_applied_deployment():
    deployments = [
        create_deployment(
            deployment_id="V000001",
            version=1,
            description="initial_deployment",
            checksum="initial_checksum"
        ),
        create_deployment(
            deployment_id="V000003",
            version=3,
            description="third_deployment",
            checksum="third_checksum"
        ),
        create_deployment(
            deployment_id="V000004",
            version=4,
            description="fourth_deployment",
            checksum="fourth_checksum"
        )
    ]
    deployment_history = [
        create_deployment_history_entry(
            deployment_id="V000001",
            version=1,
            checksum="initial_checksum"
        ),
        create_deployment_history_entry(
            deployment_id="V000002",
            version=2,
            checksum="second_checksum"
        ),
        create_deployment_history_entry(
            deployment_id="V000003",
            version=3,
            checksum="third_checksum"
        ),
    ]
    plan = create_deployment_plan(deployments, deployment_history)

    assert len(plan.planned_deployments) == 4
    assert [plan.deployment_id for plan in plan.planned_deployments] == ["V000001", "V000002", "V000003", "V000004"]

    assert plan.planned_deployments[0].status == DeploymentStatus.APPLIED
    assert plan.planned_deployments[1].status == DeploymentStatus.MISSING_LOCAL_DEPLOYMENT
    assert plan.planned_deployments[2].status == DeploymentStatus.APPLIED
    assert plan.planned_deployments[3].status == DeploymentStatus.PENDING


# validate that same file produces same checksum
def test_deployment_checksum_consistency(tmp_path: Path):
    file_path = tmp_path / "V000001__first.sql"
    file_path.write_text("SELECT 1;")

    first_deployment = Deployment.from_path(file_path)
    second_deployment = Deployment.from_path(file_path)

    assert first_deployment.checksum == second_deployment.checksum


# validate that different files produce different checksums
def test_deployment_checksum_changes_when_file_content_changes(tmp_path: Path):
    file_path = tmp_path / "V000001__first.sql"

    file_path.write_text("SELECT 1;")
    before = Deployment.from_path(file_path)

    file_path.write_text("SELECT 2;")
    after = Deployment.from_path(file_path)

    assert before.checksum != after.checksum