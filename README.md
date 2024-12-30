# Using dbt with Dagster's local agent in a hybrid deployment

## Add dbt to your Dagster project

1. **Project Setup**
   - Copy your dbt project into the root of your Dagster repository
   - Add `profiles.yml` to the root of your dbt project
   - Update the `profiles.yml` with the appropriate [`dbt adapter`](https://docs.getdbt.com/docs/supported-data-platforms) connection info
     - We recommend using environment variables—[see example configuration](https://github.com/dagster-io/hooli-data-eng-pipelines/blob/master/dbt_project/profiles.yml)

2. **Update Dependencies**
   - Add the following packages to your `setup.py`:
     - `dagster-dbt`
     - `dbt-<your_adapter>`
   - Add the following package_data config to the `setup.py`:

     ```python
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
         ...
     ```

3. **Configure the `dagster-dbt` (dbt Core) integration**
   - Create a `project.py` file with the following code to your existing code location:
  
     ```python
     from pathlib import Path

     from dagster_dbt import DbtProject
      
     my_dbt_project = DbtProject(
         project_dir=Path(__file__).joinpath("..", "..", "my_dbt_project").resolve(),
         packaged_project_dir=Path(__file__).joinpath("..", "dbt-project").resolve(),
     )
     my_dbt_project.prepare_if_dev()
     ```

   - Be sure to update the `project_dir` variable with your dbt project name

4. **Create dbt Assets**
   - Either:
     - Copy the provided `assets.py` file, or
    
     ```python
     from dagster import AssetExecutionContext
     from dagster_dbt import DbtCliResource, dbt_assets
    
     from .project import my_dbt_project
    
    
     @dbt_assets(manifest=my_dbt_project.manifest_path)
     def my_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
         yield from dbt.cli(["build"], context=context).stream()  
     ```
   
     - Add the `dbt_assets` code to an existing asset file
   - Ensure the dbt assets and resource are included with your other asset definitions:
  
     ```python
     from dagster import Definitions
     from dagster_dbt import DbtCliResource
     from .assets import my_dbt_assets
     from .project import my_dbt_project
     
     defs = Definitions(
         assets=[my_dbt_assets],
         resources={
             "dbt": DbtCliResource(project_dir=my_dbt_project),
         },
     )
     ```

## Configure SSH

The CI/CD example in this guide uses SSH authentication to interact with the remote machine hosting the local agent.

1. **Create a new SSH key pair for GitHub Actions**
   - Open the terminal and run the following bash command on the remote machine hosting the local agent:

      ```bash
      ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
      ```
     - When prompted for a passphrase, leave it empty for automated access.

   -  Add the public key to authorized keys:

      ```bash
      cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
      ```
   - Retrieve the private key — it will be saved as a GitHub repository secret in a subsequent step:

      ```bash
      cat ~/.ssh/github_actions
      ```
     - Be sure to copy the entire output (including the BEGIN and END lines)

## Configure CI/CD

Dagster's local agent is unique from the other hybrid agents in that user code does not need to be packaged into a Docker image—instead, we will use virtual environments to ensure dependency isolation between deployments.

1. **Set up GitHub Actions workflow**
   - Create a new file `dagster-cloud-deploy.yml` and save it under the `.github/workflows` directory (create the directory if it does not already exist)
   - Copy the following GitHub Action template into the newly created `dagster-cloud-deploy.yml` file:

     https://github.com/izzye84/my_dagster_project_with_dbt/blob/main/.github/workflows/dagster-cloud-deploy.yml
    
      - Be sure to update the `DAGSTER_CLOUD_ORGANIZATION` environment variable in the template to reflect your Dagster organization name.

2. **Create GitHub repository secrets**
   - Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions → New repository secret):
     - `SSH_PRIVATE_KEY`: The private key generated in the SSH configuration step
     - `SSH_HOST`: The hostname or IP address of your remote machine
     - `SSH_USER`: The username on the remote machine
     - `DAGSTER_PROJECT_PATH`: The directory on the remote machine where you keep your Dagster project; e.g., `path/to/my_dagster_project`

3. **Add an `executable_path` to the `dagster_cloud.yaml`**
   - Update your [`dagster_cloud.yaml`](https://docs.dagster.io/dagster-plus/managing-deployments/dagster-cloud-yaml#python-executable) with the following configuration, replacing `<absolute/path/to/my_dagster_project>` with the full path where your project is deployed on the remote machine:
   
     ```yaml
     locations:
     - location_name: my_dagster_code_location
       code_source:
         module_name: my_dagster_code_location.definitions
       executable_path: <absolute/path/to/my_dagster_project>/venvs/current_venv/bin/python
     ```
   - For example, if your project is deployed to /home/user/my_dagster_project, your path would be:
     ```yaml
     executable_path: /home/user/my_dagster_project/venvs/current_venv/bin/python
     ```
       - Note: The virtual environment path (`venvs/current_venv`) is managed automatically by the GitHub Action and ensures the `executable_path` always points to the latest virtual environment.

4. **Testing**
   - Test the dbt Core integration locally using `dagster dev`
   - If everything works as expected, open a Pull Request
