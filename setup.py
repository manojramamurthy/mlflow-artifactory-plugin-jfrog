from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open("version.txt") as file:
    __version__ = file.readline().strip()


setup(
    name="mlflow-artifactory-plugin-jfrog",
    version=__version__,
    description="Plugin that provides JFrog Artifactory Artifact Store functionality for MLflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Manoj Kumar R",
    author_email="manojrammurthy@gmail.com",
    url="https://github.com/manojramamurthy/mlflow-artifactory-plugin-jfrog",
    # Require MLflow as a dependency of the plugin, so that plugin users can simply install
    # the plugin and then immediately use it with MLflow
    install_requires=["mlflow==2.4.1", "rtpy==1.4.9"],
    packages=find_packages(),
    entry_points={
        # Define a ArtifactRepository plugin for artifact URIs with scheme 'file-plugin'
        "mlflow.artifact_repository": "artifactory=jfrogartifactoryplugin.store.artifact.jfrog_artifact_repository:JFrogArtifactRepository",
    },
    license="Apache License 2.0",
)
