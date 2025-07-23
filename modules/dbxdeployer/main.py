import structlog

from utils.get_merged_config import get_merged_config
from session.DatabricksSession import DatabricksSession
from deploy import deploy

module_logger = structlog.get_logger(__name__)


def main():
    logger = structlog.getLogger()
    
    # Load configurations for deployment
    config = get_merged_config(logger=module_logger)

    # initiate Databricks session
    session = DatabricksSession(
        logger=logger,
        **config.get_session_kwargs(),
    )

    deploy(config, session)

if __name__ == "__main__":
    main()
