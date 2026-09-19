# deployment planner
from dbxdeployer.domain.deployment import Deployment
from dbxdeployer.domain.deployment_plan import DeploymentStatus, PlannedDeployment, DeploymentPlan
from dbxdeployer.domain.deployment_history import DeploymentHistoryEntry


def create_deployment_plan(
        deployments: list[Deployment],
        deployment_history: list[DeploymentHistoryEntry],
) -> DeploymentPlan:
    planned_deployments = []

    # Check if any deployments have already been applied based on the deployment history
    history_by_id = {entry.deployment_id: entry for entry in deployment_history}

    for deployment in deployments:
        history_entry = history_by_id.get(deployment.deployment_id)

        if history_entry is None:
            status = DeploymentStatus.PENDING
        elif (deployment.checksum != history_entry.checksum):
            status = DeploymentStatus.CHECKSUM_MISMATCH
        else:
            status = DeploymentStatus.APPLIED
        planned_deployments.append(PlannedDeployment(deployment=deployment, status=status))
    return DeploymentPlan(planned_deployments)