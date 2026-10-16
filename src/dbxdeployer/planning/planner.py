# deployment planner
from dbxdeployer.domain.deployment import Deployment
from dbxdeployer.domain.deployment_plan import DeploymentStatus, PlannedDeployment, DeploymentPlan
from dbxdeployer.domain.deployment_history import DeploymentHistoryEntry


def create_deployment_plan(
        deployments: list[Deployment],
        deployment_history: list[DeploymentHistoryEntry],
) -> DeploymentPlan:
    planned_deployments = []

    # map "deployments" to "deployment_history" by deployment_id
    # If a deployment is found in the history, it is considered "APPLIED" if the checksums match, otherwise it is considered "CHECKSUM_MISMATCH".
    # If a deployment is not found in the history, it is considered "PENDING".
    # If a deployment is found in the history but not in the local deployments, it is considered "MISSING_LOCAL_DEPLOYMENT".
    
    # Create a dictionary for quick lookup of deployments and history entries by deployment version
    deployment_dict = {d.deployment_id: d for d in deployments}
    history_dict = {h.deployment_id: h for h in deployment_history}
    all_deployments_ids = sorted(set(deployment_dict.keys()).union(set(history_dict.keys())), key=lambda x: int(x[1:]))  # Sort by version number

    # Iterate through all versions and determine the status of each deployment
    for deployment_id in all_deployments_ids:
        deployment = deployment_dict.get(deployment_id)
        history_entry = history_dict.get(deployment_id)

        if deployment and history_entry:
            if deployment.checksum == history_entry.checksum:
                status = DeploymentStatus.APPLIED
            else:
                status = DeploymentStatus.CHECKSUM_MISMATCH
        elif deployment and not history_entry:
            status = DeploymentStatus.PENDING
        elif not deployment and history_entry:
            status = DeploymentStatus.MISSING_LOCAL_DEPLOYMENT
        else:
            raise RuntimeError(f"Unexpected state: deployment_id {deployment_id} not found in either deployments or history.")

        planned_deployments.append(
            PlannedDeployment(
                deployment=deployment,
                history_entry=history_entry,
                status=status
            )
        )


    return DeploymentPlan(tuple(planned_deployments))