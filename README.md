# JFrog Artifactory plugin for MLflow
This repository provides an MLflow plugin that allows users to use a JFrog Artifactory as the artifact store for MLflow.

## Implmentation overview
* `jfrogartifactoryplugin`: this package includes the `JFrogArtifactRepository` class that is used to read and write artifacts from JFrog Artifactory.
* `setup.py` file defines entrypoints that tell MLflow to automatically associate the `artifactory` URIs with the `JFrogArtifactRepository` implementation when the `jfrogartifactoryplugin` library is installed. The entrypoints are configured as follows:

```
entry_points={
        "mlflow.artifact_repository": [
            "artifactory=jfrogartifactoryplugin.store.artifact.jfrog_artifact_repository:JFrogArtifactRepository"
        ]
    }
```

## Usage
Install using pip on both your client and the tracking server and then use MLflow as normal. 

```
pip install -e .
```
The plugin implements all of the MLflow artifact store APIs calls. It expects JFrog Artifactory `API_KEY` and `REPO_NAME` in the `MLFLOW_ARTIFACTORY_KEY` and `MLFLOW_ARTIFACTORY_REPO` environment variables respectively. These variables must be set on both your client application and your MLflow tracking server. To use JFrog Artifactory as an artifact store, an Artifactory URI of the form `artifactory://<path>` must be provided, as shown in the example below:

```python
import mlflow
import mlflow.pyfunc

class Mod(mlflow.pyfunc.PythonModel):
    def predict(self, ctx, inp):
        return 7

exp_name = "myexp"
mlflow.create_experiment(exp_name, artifact_location="artifactory://mlflow-test/")
mlflow.set_experiment(exp_name)
mlflow.pyfunc.log_model('model_test', python_model=Mod())
```

Remember the `API_KEY` provided should be for a service account with access to the Artifactory repo on the MLflow Tracking Server. On the client side you can use your own `API_KEY` provided you have access to the repo.


## Environment variables
The following environment variables should be set in order to run the server.

```bash
export MLFLOW_ARTIFACTORY_ENDPOINT_URL="<JFrog_artifactory_URL>"
export MLFLOW_ARTIFACTORY_KEY="<YOUR_ARTIFACTORY_API_KEY>"
export MLFLOW_ARTIFACTORY_REPO="<JFrog_artifactory_REPO>"
export REQUESTS_CA_BUNDLE="<certificate>"
mlflow server --backend-store-uri /mlflow/mlruns --default-artifact-root artifactory://mlflow
```

Likewise, on the client-side you should have the following environment variables should be set

```python
import os
os.environ["MLFLOW_ARTIFACTORY_ENDPOINT_URL"] = "<JFrog_artifactory_URL>"
os.environ["MLFLOW_ARTIFACTORY_KEY"] = "<YOUR_ARTIFACTORY_API_KEY>"
os.environ["MLFLOW_ARTIFACTORY_REPO"] = "<JFrog_artifactory_REPO>"
os.environ["REQUESTS_CA_BUNDLE"] = "<certificate>"
```
