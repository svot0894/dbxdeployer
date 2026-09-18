# unit tests for src/dbxdeployer/planning/planner.py

from pathlib import Path

from dbxdeployer.planning.planner import create_deployment_plan
from dbxdeployer.domain.deployment import Deployment
from dbxdeployer.domain.deployment_plan import DeploymentStatus, PlannedDeployment, DeploymentPlan


def create_deployment(
        deployment_id: str,
        version: int,
        description: str
) -> Deployment:
    return Deployment(
        deployment_id=deployment_id,
        version=version,
        description=description,
        file_path=Path(f"migrations/{deployment_id}__{description}.sql")
    )


# Test the create_deployment_plan function
def test_create_deployment_plan_with_empty_list():
    plan = create_deployment_plan([])
    assert isinstance(plan, DeploymentPlan)
    assert plan.planned_deployments == []


# Test the create_deployment_plan function with a single deployment
def test_create_deployment_plan_with_single_deployment():
    deployments = create_deployment(
        deployment_id="V000001",
        version=1,
        description="initial_deployment"
    )
    plan = create_deployment_plan([deployments])

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
            description="initial_deployment"
        ),
        create_deployment(
            deployment_id="V000002",
            version=2,
            description="second_deployment"
        ),
        create_deployment(
            deployment_id="V000003",
            version=3,
            description="third_deployment"
        )
    ]
    plan = create_deployment_plan(deployments)

    assert len(plan.planned_deployments) == 3

    assert [plan.deployment.deployment_id for plan in plan.planned_deployments] == ["V000001", "V000002", "V000003"]
    assert all(plan.status == DeploymentStatus.PENDING for plan in plan.planned_deployments)