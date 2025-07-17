import hashlib
from pathlib import Path
import structlog
import jinja2
from modules.dbxdeployer.script import get_all_scripts_recursively
from modules.dbxdeployer.session.DatabricksSession import DatabricksSession

logger = structlog.getLogger(__name__)


def sort_by_version(version: str):
    """Returns a tuple with the version of a specific script."""
    return tuple(map(int, version.split(".")))


def deploy(configs, api_configs, session: DatabricksSession):

    # create required variables
    create_tracking_table = configs["create_tracking_table"]
    dry_run = configs["dry_run"]
    deployment_order = configs['deployment_order']
    root_folder = configs['root_folder']
    variables = configs["vars"]

    logger.info(
        "Starting Databricks deployment"
        , dry_run = dry_run
        , tracking_table = configs["tracking_table"]
    )

    # fetch max version per object from tracking table where type = A
    api_scripts, api_scripts_max_versions = session.api_scripts_metadata(create_tracking_table, dry_run)

    # fetch  max version per object from tracking table where type = S
    sql_scripts, sql_scripts_max_versions = session.sql_scripts_metadata(create_tracking_table, dry_run)

    # fetch all files in the deployables folder
    root_path = Path(root_folder)
    all_scripts = get_all_scripts_recursively(root_path)

    # sort scripts based on expected deployment order and version of scripts
    all_scripts_sorted = sorted(
        all_scripts
        , key=lambda script: (
            deployment_order.index(script.object) if script.object in deployment_order else float('inf')
            , sort_by_version(script.version)
            )
    )

    scripts_skipped = 0
    scripts_applied = 0

    for script in all_scripts_sorted:
        script_log = logger.bind(
            a_script_name = script.name
            , script_object = script.object
            , script_version = script.version
        )

        # TBD: jinja process for variables in scripts
        loader = jinja2.FileSystemLoader(".")
        environment = jinja2.Environment(loader=loader)
        posix_path = Path(script.file_path).as_posix()
        template = environment.get_template(posix_path)
        content = template.render(**variables)

        checksum_current = hashlib.sha224(content.encode("utf-8")).hexdigest()

        # deploy api-configs scripts
        if script.type == "A":
            if (
                api_scripts_max_versions.get(script.object, None) is not None
                and sort_by_version(script.version) <= sort_by_version(api_scripts_max_versions.get(script.object, None))
            ):
                script_log.debug(
                    "Skipping script because it's older than the most recently applied change",
                    max_version = sort_by_version(api_scripts_max_versions.get(script.object, None))
                )
                scripts_skipped += 1
                continue

            # fetch API details for specific object and operation
            api_details = api_configs[script.object][script.operation]

            session.apply_api_script(script, content, dry_run, logger, api_details)
            
            scripts_applied += 1
        
        # deploy sql-scripts scripts
        if script.type == "S":
            if (
                sql_scripts_max_versions.get(script.object, None) is not None
                and sort_by_version(script.version) <= sort_by_version(sql_scripts_max_versions.get(script.object, None))
            ):
                script_log.debug(
                    "Skipping script because it's older than the most recently applied change",
                    max_version = sort_by_version(sql_scripts_max_versions[script.object])
                )
                scripts_skipped += 1
                continue

            session.apply_change_script(
                script = script
                , script_content = content
                , dry_run= dry_run
                , logger = script_log
            )
            scripts_applied += 1
        
        # deploy permissions: TBD
    
    logger.info(
        "Deployment completed successfully."
        , scripts_applied = scripts_applied
        , scripts_skipped = scripts_skipped
    )
        

