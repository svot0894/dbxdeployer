# deployment planner
from dbxdeployer.domain.deployment import Deployment
from dbxdeployer.domain.deployment_plan import DeploymentStatus, PlannedDeployment, DeploymentPlan


def create_deployment_plan(deployments: list[Deployment]) -> DeploymentPlan:
    planned_deployments = []

    for deployment in deployments:
        planned_deployment = PlannedDeployment(deployment=deployment, status=DeploymentStatus.PENDING)
        planned_deployments.append(planned_deployment)

    return DeploymentPlan(planned_deployments)