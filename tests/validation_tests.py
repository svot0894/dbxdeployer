from pathlib import Path

from dbxdeployer.domain.validation import validate_plan
from dbxdeployer.domain.deployment_plan import DeploymentPlan, DeploymentStatus, PlannedDeployment
from dbxdeployer.domain.deployment_history import DeploymentHistoryEntry
from dbxdeployer.domain.deployment import Deployment


# Test 1: No issues with the deployment plan
def test_validate_plan_returns_valid_when_no_blocking_statuses():

    plan = DeploymentPlan(
        planned_deployments=(
            PlannedDeployment(
                deployment=Deployment(
                    deployment_id="V000001",
                    version=1,
                    description="initial_deployment",
                    file_path=Path("migrations/V000001__initial_deployment.sql"),
                    checksum="checksum1"
                ),
                history_entry=DeploymentHistoryEntry(
                    deployment_id="V000001",
                    version=1,
                    checksum="checksum1"
                ),
                status=DeploymentStatus.APPLIED
            ),
            PlannedDeployment(
                deployment=Deployment(
                    deployment_id="V000002",
                    version=2,
                    description="second_deployment",
                    file_path=Path("migrations/V000002__second_deployment.sql"),
                    checksum="checksum2"
                ),
                history_entry=None,
                status=DeploymentStatus.PENDING,
            ),
        )
    )

    result = validate_plan(plan)

    assert result.is_valid is True
    assert result.issues == ()

# Test 2: Checksum mismatch between deployment and history entry
def test_validate_plan_returns_invalid_for_checksum_mismatch():
    plan = DeploymentPlan(
        planned_deployments=(
            PlannedDeployment(
                deployment=Deployment(
                    deployment_id="V000001",
                    version=1,
                    description="initial_deployment",
                    file_path=Path("migrations/V000001__initial_deployment.sql"),
                    checksum="checksum1"
                ),
                history_entry=DeploymentHistoryEntry(
                    deployment_id="V000001",
                    version=1,
                    checksum="different_checksum"
                ),
                status=DeploymentStatus.CHECKSUM_MISMATCH
            ),
        )
    )

    result = validate_plan(plan)

    assert result.is_valid is False
    assert len(result.issues) == 1
    assert result.issues[0].deployment_id == "V000001"
    assert result.issues[0].code == DeploymentStatus.CHECKSUM_MISMATCH

# Test 3: Missing local deployment for a history entry
def test_validate_plan_returns_invalid_for_missing_local_deployment():
    plan = DeploymentPlan(
        planned_deployments=(
            PlannedDeployment(
                deployment=None,
                history_entry=DeploymentHistoryEntry(
                    deployment_id="V000002",
                    version=2,
                    checksum="checksum2"
                ),
                status=DeploymentStatus.MISSING_LOCAL_DEPLOYMENT
            ),
        )
    )

    result = validate_plan(plan)

    assert result.is_valid is False
    assert len(result.issues) == 1
    assert result.issues[0].deployment_id == "V000002"
    assert result.issues[0].code == DeploymentStatus.MISSING_LOCAL_DEPLOYMENT

# Test 4: Multiple issues in the deployment plan
def test_validate_plan_returns_multiple_issues():
    plan = DeploymentPlan(
        planned_deployments=(
            PlannedDeployment(
                deployment=Deployment(
                    deployment_id="V000001",
                    version=1,
                    description="initial_deployment",
                    file_path=Path("migrations/V000001__initial_deployment.sql"),
                    checksum="checksum1"
                ),
                history_entry=DeploymentHistoryEntry(
                    deployment_id="V000001",
                    version=1,
                    checksum="different_checksum"
                ),
                status=DeploymentStatus.CHECKSUM_MISMATCH
            ),
            PlannedDeployment(
                deployment=None,
                history_entry=DeploymentHistoryEntry(
                    deployment_id="V000002",
                    version=2,
                    checksum="checksum2"
                ),
                status=DeploymentStatus.MISSING_LOCAL_DEPLOYMENT
            ),
        )
    )

    result = validate_plan(plan)

    assert result.is_valid is False
    assert len(result.issues) == 2
    assert result.issues[0].deployment_id == "V000001"
    assert result.issues[0].code == DeploymentStatus.CHECKSUM_MISMATCH
    assert result.issues[1].deployment_id == "V000002"
    assert result.issues[1].code == DeploymentStatus.MISSING_LOCAL_DEPLOYMENT

