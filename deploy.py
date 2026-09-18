from pathlib import Path
import structlog
import jinja2

from config.DeployConfig import DeployConfig
from session.script import get_all_scripts_recursively
from session.DatabricksSession import DatabricksSession

logger = structlog.getLogger(__name__)


def sort_by_version(version: str):
    """Returns a tuple with the version of a specific script."""
    return tuple(map(int, version.split(".")))


def deploy(config: DeployConfig, session: DatabricksSession):

    logger.info(
        "Starting Databricks deployment..."
        , dry_run = config.dry_run
        , tracking_table = config.tracking_table.fully_qualified
    )

    # fetch  max version per object from tracking table where type = S
    sql_scripts_max_versions = session.get_scripts_metadata("S", config.create_tracking_table, config.dry_run)

    # fetch all files in the deployables folder
    root_path = Path(config.root_folder)
    all_scripts = get_all_scripts_recursively(root_path)

    # sort scripts based on expected deployment order and version of scripts
    all_scripts_sorted = sorted(
        all_scripts
        , key=lambda script: (
            config.deployment_order.index(script.object) if script.object in config.deployment_order else float('inf')
            , sort_by_version(script.version)
            )
    )

    scripts_skipped = 0
    scripts_applied = 0

    loader = jinja2.FileSystemLoader(".")
    environment = jinja2.Environment(
        loader=loader,
        variable_start_string="<<",
        variable_end_string=">>"
    )

    for script in all_scripts_sorted:
        script_log = logger.bind(
            a_script_name = script.name
            , script_object = script.object
            , script_version = script.version
        )

        # TBD: jinja process for config.vars in scripts
        posix_path = Path(script.file_path).as_posix()
        template = environment.get_template(posix_path)
        content = template.render(**config.vars)

        # deploy sql-scripts scripts
        if script.type == "S":
            if (
                sql_scripts_max_versions.get(script.object, None) is not None
                and sort_by_version(script.version) <= sort_by_version(sql_scripts_max_versions.get(script.object, None))
            ):
                script_log.debug(
                    "Script has already been applied",
                    max_version = sort_by_version(sql_scripts_max_versions[script.object])
                )
                scripts_skipped += 1
                continue

            session.apply_change_script(
                script = script
                , script_content = content
                , dry_run= config.dry_run
                , logger = script_log
            )
            scripts_applied += 1
        
        # deploy permissions: TBD
    
    logger.info(
        "Deployment completed successfully."
        , scripts_applied = scripts_applied
        , scripts_skipped = scripts_skipped
    )
        

