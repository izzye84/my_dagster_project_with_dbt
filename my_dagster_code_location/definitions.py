from dagster import Definitions
from dagster_dbt import DbtCliResource
from .assets import my_dbt_assets
from .hackernews import hackernews_topstories, hackernews_topstory_ids, hackernews_topstories_word_cloud
from .project import my_dbt_project
from .schedules import schedules

defs = Definitions(
    assets=[
        my_dbt_assets,
        hackernews_topstories,
        hackernews_topstory_ids,
        hackernews_topstories_word_cloud,
    ],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(project_dir=my_dbt_project),
    },
)

