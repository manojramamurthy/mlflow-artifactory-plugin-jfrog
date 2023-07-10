import logging
import os
import posixpath
from pathlib import Path
from urllib.parse import urlparse

import rtpy
from mlflow.entities.file_info import FileInfo
from mlflow.exceptions import MlflowException
from mlflow.store.artifact.artifact_repo import ArtifactRepository


class JFrogArtifactRepository(ArtifactRepository):
    """Stores artifacts as files in a JFrog Artifactory directory."""

    is_plugin = True

    def __init__(self, artifact_uri, repo_name=None, api_key=None):
        super(JFrogArtifactRepository, self).__init__(artifact_uri)

        if repo_name is not None:
            self.artifactory_repo = repo_name
            return

        if api_key is not None:
            self.api_key = api_key
            return

        self.artifactory_endpoint = os.environ.get("MLFLOW_ARTIFACTORY_ENDPOINT_URL")
        self.artifactory_api_key = os.environ.get("MLFLOW_ARTIFACTORY_KEY")
        self.artifactory_repo = urlparse(
            os.environ.get("MLFLOW_ARTIFACTORY_REPO")
        ).geturl()

        assert self.artifactory_endpoint, "please set MLFLOW_ARTIFACTORY_ENDPOINT_URL"
        assert self.artifactory_api_key, "please set MLFLOW_ARTIFACTORY_KEY"
        assert self.artifactory_repo, "please set MLFLOW_ARTIFACTORY_REPO"

        self.af = rtpy.Rtpy(
            {"af_url": self.artifactory_endpoint, "api_key": self.artifactory_api_key}
        )

    def ping(self):
        return self.af.system_and_configuration.system_health_ping()

    @staticmethod
    def parse_artifactory_uri(uri):
        """Parse an artifactory URI, returning (path)"""
        parsed = urlparse(uri)
        if parsed.scheme != "artifactory":
            raise Exception("Not an artifactory URI: %s" % uri)
        path = parsed.path
        if path.startswith("/"):
            path = path[1:]
        return parsed.netloc, path

    def log_artifact(self, local_file, artifact_path=None):
        (netloc, artifact_dir) = self.parse_artifactory_uri(self.artifact_uri)
        artifact_dir = (
            posixpath.join(netloc, artifact_path, artifact_dir)
            if artifact_path
            else posixpath.join(netloc, artifact_dir)
        )

        print("artifact_dir: ", artifact_dir)
        print("local_file: ", local_file)

        if Path(local_file).is_file():
            remote_file = posixpath.join(artifact_dir, Path(local_file).name)
            try:
                response = self.af.artifacts_and_storage.deploy_artifact(
                    self.artifactory_repo, local_file, remote_file
                )
            except self.af.AfApiError as error:
                print(error)
                raise RuntimeError(
                    f"""Unable to log {local_file} to repository
                        {self.artifactory_repo} with target destination {remote_file}"""
                )

    def log_artifacts(self, local_dir, artifact_path=None):
        p = Path(local_dir).glob("**/*")
        (netloc, artifact_dir) = self.parse_artifactory_uri(self.artifact_uri)
        artifact_dir = (
            posixpath.join(netloc, artifact_dir, artifact_path)
            if artifact_path
            else posixpath.join(netloc, artifact_dir)
        )

        print("artifact_dir: ", artifact_dir)
        print("local_dir: ", local_dir)
        
        for local_file in p:
            if local_file.is_file():
                remote_file = posixpath.join(artifact_dir, local_file.name)
                try:
                    response = self.af.artifacts_and_storage.deploy_artifact(
                        self.artifactory_repo, local_file, remote_file
                    )
                except self.af.AfApiError as error:
                    print(error)
                    raise RuntimeError(
                        f"""Unable to log {local_file} to repository
                            {self.artifactory_repo} with target destination {remote_file}"""
                        )

    def list_artifacts(self, path=None):
        (netloc, artifact_dir) = self.parse_artifactory_uri(self.artifact_uri)
        infos = []
        
        if path:
            full_path = "/" + netloc + "/" + artifact_dir + "/" + path
        else:
            full_path = "/" + netloc + "/" + artifact_dir

        print("full_path: ", full_path)
        
        for f in self._list_files(full_path, parent=path):
            infos.append(f)
        
        return sorted(infos, key=lambda f: f.path)

    def _list_files(self, directory, parent=None):
        r = self.af.artifacts_and_storage.folder_info(self.artifactory_repo, directory)
        if "children" in r:
            listdir = r["children"]
            
            for file in listdir:
                if file["folder"]:
                    sub_directory_rel = os.path.basename(file["uri"])
                    yield FileInfo(sub_directory_rel, True, None)
                else:
                    file_name = "/" + os.path.basename(file["uri"])
                    
                    if parent is None:
                        file_rel_path = os.path.basename(file["uri"])
                    else:
                        file_rel_path = parent + file_name
                    r_file = self.af.artifacts_and_storage.file_info(
                        self.artifactory_repo, directory + file_name
                    )
                    size = int(r_file["size"])
                    yield FileInfo(file_rel_path, False, size)  # todo: get size

    def _download_file(self, remote_file_path, local_path):
        (netloc, artifact_dir) = self.parse_artifactory_uri(self.artifact_uri)
        print("local_path: ", local_path)
        artifact_path = posixpath.join(netloc, artifact_dir, remote_file_path)
        print("artifact_path: ", artifact_path)
        r = self.af.artifacts_and_storage.retrieve_artifact(
            self.artifactory_repo, artifact_path
        )
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Save the file locally
        with open(local_path, "wb") as artifact:
            artifact.write(r.content)

    def delete_artifacts(self, artifact_path=None):
        raise MlflowException("delete_artifacts not implemented yet")
