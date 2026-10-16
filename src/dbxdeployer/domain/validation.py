# Validator tells us whether a deployment plan is safe to execute, and if not, what the issues are.
from dataclasses import dataclass
from dbxdeployer.domain.deployment_plan import DeploymentStatus
from dbxdeployer.domain.deployment_plan import DeploymentPlan


@dataclass(frozen=True)
class ValidationIssue:
    deployment_id: str | None
    code: DeploymentStatus
    message: str

# ValidationResult:
@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0

def validate_plan(plan: DeploymentPlan) -> ValidationResult:
    issues: list[ValidationIssue] = []

    for deployment in plan.planned_deployments:
        # check for any deployments with CHECKSUM_MISMATCH or MISSING_LOCAL_DEPLOYMENT
        if deployment.status in (DeploymentStatus.CHECKSUM_MISMATCH, DeploymentStatus.MISSING_LOCAL_DEPLOYMENT):
            issues.append(
                ValidationIssue(
                    deployment_id=deployment.deployment_id,
                    code=deployment.status,
                    message=f"Deployment {deployment.deployment_id} has status {deployment.status}.",
                ),
            )

    return ValidationResult(
        issues=tuple(issues)
    )