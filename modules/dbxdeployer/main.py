import structlog
import warnings
from urllib3.exceptions import InsecureRequestWarning

from utils.get_merged_config import get_merged_config
from session.DatabricksSession import DatabricksSession
from deploy import deploy


# metadata for the module
DBXDEPLOYER_VERSION = "0.1.0"
DBXDEPLOYER_MODULE_NAME = "dbxdeployer"
module_logger = structlog.get_logger(__name__)

# surpress warning related to SSL certificate verification
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


def main():
    module_logger.info(
        "dbxdeployer version: %(dbxdeployer_version)s"
        % {"dbxdeployer_version": DBXDEPLOYER_VERSION}
    )

    # Load configurations for deployment
    config = get_merged_config(logger=module_logger)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(config.log_level),  # won't show log levels beneath configured level: INFO
        processors=[
        structlog.contextvars.merge_contextvars,                                # ensure any context-local binds gets included in all logs messages.
        structlog.processors.add_log_level,                                     #
        structlog.processors.TimeStamper(fmt="iso"),                            # adds a timestamp in ISO format to the event.
        structlog.processors.dict_tracebacks,                                   #
        structlog.dev.ConsoleRenderer(force_colors=True),                       #
    ],
    )

    logger = structlog.getLogger()
    logger = logger.bind(dbxdeployer_version=DBXDEPLOYER_VERSION)

    config.log_details()

    # initiate Databricks session
    session = DatabricksSession(
        logger=logger,
        **config.get_session_kwargs(),
    )

    deploy(config, session)

if __name__ == "__main__":
    main()
