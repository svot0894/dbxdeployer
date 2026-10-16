from enum import Enum
from dataclasses import dataclass

# ValidationIssueType
# is an enumeration that defines the types of validation issues that can occur during the validation process. It includes the following types:
class ValidationIssueType(Enum):
    MISSING_LOCAL_DEPLOYMENT = "MISSING_LOCAL_DEPLOYMENT"
    OUT_OF_ORDER_HISTORY = "OUT_OF_ORDER_HISTORY"

# ValidationIssue:
# is a class that represents a validation issue. It contains information about the issue, such as its type, message, and any additional details.
@dataclass(frozen=True)
class ValidationIssue:
    issue_type: ValidationIssueType
    deployment_id: str
    message: str

# ValidationResult:
@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0