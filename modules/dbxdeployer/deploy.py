import hashlib
from pathlib import Path
import structlog
from modules.dbxdeployer.script import get_all_scripts_recursively
from modules.dbxdeployer.session.DatabricksSession import DatabricksSession

logger = structlog.getLogger(__name__)


def sort_by_version(version: str):
    """Returns a tuple with the version of a specific script."""
    return tuple(map(int, version.split(".")))


def deploy(configs, api_configs, session: DatabricksSession):

    logger.info(
        "Starting Databricks deployment"
        , dry_run = configs["dry_run"]
    )

    DEPLOYMENT_ORDER = configs['deployment_order']

    # fetch max version per object from tracking table where type = A
    api_scripts, api_scripts_max_versions = session.api_scripts_metadata()

    # fetch  max version per object from tracking table where type = S
    sql_scripts, sql_scripts_max_versions = session.sql_scripts_metadata()

    # fetch all files in the deployables folder
    root_path = Path(configs['root_folder'])
    all_scripts = get_all_scripts_recursively(root_path)

    # sort scripts based on expected deployment order and version of scripts
    all_scripts_sorted = sorted(
        all_scripts
        , key=lambda script: (
            DEPLOYMENT_ORDER.index(script.object) if script.object in DEPLOYMENT_ORDER else float('inf')
            , sort_by_version(script.version)
            )
    )

    scripts_skipped = 0
    scripts_applied = 0

    for script in all_scripts_sorted:
        script_log = logger.bind(
            a_script_name = script.name
            , script_version = script.version
        )

        #jinja process for variables in config files TBD
        content = ""

        checksum_current = hashlib.sha224(content.encode("utf-8")).hexdigest()

        ## different deployments depending on whether it's sql-script or api-configs
        if script.type == "A":
            if (
                api_scripts_max_versions[script.object] is not None
                and sort_by_version(script.version) <= sort_by_version(api_scripts_max_versions[script.object])
            ):
                script_log.debug(
                    "Skipping script because it's older than the most recently applied change",
                    max_version = sort_by_version(api_scripts_max_versions[script.object])
                )
                scripts_skipped += 1
                continue

            # Fetch API details for specific object and operation
            api_details = api_configs[script.object][script.operation]

            session.apply_api_script(script.object, script.operation, script, api_details)
            
            scripts_applied += 1
        
        if script.type == "S":
            if script.version > sql_scripts_max_versions[script.object]:
                session.apply_change_script(
                    script = script
                    , script_content = content
                    , logger = script_log
                )
                scripts_applied += 1
    
    logger.info(
        "Deployment completed successfully."
        , scripts_applied = scripts_applied
        , scripts_skipped = scripts_skipped
    )
        

