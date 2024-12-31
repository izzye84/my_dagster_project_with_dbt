from setuptools import find_packages, setup

setup(
    name="my_example_dagster_project",
    version="0.0.1",
    packages=find_packages(),
    package_data={
        "my-dagster-code-location": [
            "dbt-project/**/*",
        ],
    },
    install_requires=[
        "boto3",
        "dagster",
        "dagster-cloud",
        "dagster-dbt",
        "dbt-duckdb<1.9",
        "matplotlib",
        "pandas",
        "textblob",
        "tweepy",
        "wordcloud",
    ],
    extras_require={
        "dev": [
            "dagster-webserver",
        ]
    },
)