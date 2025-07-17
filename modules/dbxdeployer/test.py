import jinja2
from pathlib import Path

loader = jinja2.FileSystemLoader(".")
environment = jinja2.Environment(loader=loader)
posix_path = Path("deployables/sql-scripts/tables/S1.0_tables__cfg_sch.cfg_t_permission.sql").as_posix()
print(posix_path)
template = environment.get_template(posix_path)
