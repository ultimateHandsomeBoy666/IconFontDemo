#!/usr/bin/env python3
"""Open a disposable Demo copy in the plugin's isolated Android Studio sandbox."""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_GROUP = "com.example.iconfontfixtures"


class RecordingHandler(SimpleHTTPRequestHandler):
    def log_request(self, code="-", size="-"):
        self.server.requests.append({"method": self.command, "path": self.path, "status": int(code)})

    def log_message(self, format, *args):
        pass


def prepare_remote_cache(source, destination):
    """Reuse immutable non-fixture downloads; never reuse transforms or fixture artifacts."""
    def ignore(directory, names):
        return [name for name in names if name == FIXTURE_GROUP or name.endswith((".lock", ".lck"))]

    def link_artifact(src, dst):
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
        return dst

    modules = source / "caches/modules-2"
    if modules.is_dir():
        for entry in modules.iterdir():
            if entry.is_dir() and (entry.name == "files-2.1" or entry.name.startswith("metadata-")):
                # Artifact bytes are immutable. Metadata is copied because Gradle updates it.
                shutil.copytree(entry, destination / "caches/modules-2" / entry.name,
                                ignore=ignore, copy_function=link_artifact if entry.name == "files-2.1" else shutil.copy2)
    wrapper = source / "wrapper/dists/gradle-8.4-bin"
    if wrapper.is_dir():
        shutil.copytree(wrapper, destination / "wrapper/dists/gradle-8.4-bin",
                        ignore=ignore, copy_function=link_artifact)
    fixture_cache = destination / "caches/modules-2/files-2.1" / FIXTURE_GROUP
    if fixture_cache.exists():
        raise RuntimeError("Fixture artifacts must start with an empty download cache")


def configure_remote_repository(project, repository_url):
    script = project / "build.gradle"
    original = r"maven\s*\{\s*url = uri\(rootProject.file\('fixtures/repository'\)\)\s*content \{ includeGroup 'com.example.iconfontfixtures' \}\s*\}"
    replacement = """exclusiveContent {
            forRepository {
                maven {
                    url = uri('%s')
                    allowInsecureProtocol = true
                }
            }
            filter { includeGroup '%s' }
        }""" % (repository_url, FIXTURE_GROUP)
    updated, count = re.subn(original, replacement, script.read_text())
    if count != 1:
        raise RuntimeError("Could not replace exactly one fixture repository in the sandbox")
    script.write_text(updated)
    if (project / "fixtures/repository").exists():
        raise RuntimeError("Remote sandbox must not contain the local fixture repository")


def verify_remote_downloads(gradle_home, requests, manifest):
    downloads = []
    successful = {unquote(urlsplit(r["path"]).path) for r in requests
                  if r["method"] == "GET" and r["status"] == 200}
    for artifact in manifest["artifacts"]:
        relative = Path(artifact["path"]).relative_to("fixtures/repository")
        for resource in (relative, relative.with_suffix(".pom")):
            if "/" + resource.as_posix() not in successful:
                raise RuntimeError(f"No successful HTTP GET for {resource}")
        cache = gradle_home / "caches/modules-2/files-2.1" / FIXTURE_GROUP / artifact["id"] / manifest["version"]
        matches = list(cache.glob("*/" + relative.name))
        if len(matches) != 1:
            raise RuntimeError(f"Expected one downloaded artifact for {artifact['id']}: {matches}")
        digest = hashlib.sha256(matches[0].read_bytes()).hexdigest()
        if digest != artifact["sha256"]:
            raise RuntimeError(f"HTTP artifact bytes differ from the fixture: {artifact['id']}")
        downloads.append({"artifact": artifact["id"], "path": str(matches[0]), "sha256": digest,
                          "artifact_and_pom_http_get": True})
    return downloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-dir", type=Path, required=True)
    parser.add_argument("--gradle-jdk", type=Path, required=True, help="JDK 17 for Demo Gradle 8.4")
    parser.add_argument("--ide-jdk", type=Path, required=True, help="Bundled runtime used to launch Android Studio")
    parser.add_argument("--keep-open", action="store_true", help="Keep the sandbox open for a real gutter/popup UI smoke check")
    parser.add_argument("--remote-maven", action="store_true", help="Serve fixtures over loopback HTTP outside the project and use an isolated Gradle cache")
    args = parser.parse_args()
    plugin = args.plugin_dir.resolve()
    work = plugin / ("build/font-e2e-remote" if args.remote_maven else "build/font-e2e")
    project = work / "project"
    report = work / "report.json"
    if project.exists():
        if not (project / ".font-e2e-sandbox").is_file():
            raise SystemExit(f"Refusing to replace an unmarked directory: {project}")
        shutil.rmtree(project)
    def ignore_project(directory, names):
        ignored = shutil.ignore_patterns(".git", ".idea", ".gradle", "build", "__pycache__")(directory, names)
        if args.remote_maven and Path(directory) == ROOT / "fixtures":
            ignored.add("repository")
        return ignored

    shutil.copytree(ROOT, project, ignore=ignore_project)
    (project / ".font-e2e-sandbox").write_text("Disposable fixture project. Safe to replace.\n")
    (project / ".gradle").mkdir()
    (project / ".gradle/config.properties").write_text(f"java.home={args.gradle_jdk.resolve()}\n")
    (project / ".idea").mkdir()
    gradle_xml = ET.fromstring('''<project version="4"><component name="GradleSettings"><option name="linkedExternalProjectsSettings"><GradleProjectSettings><option name="externalProjectPath" value="$PROJECT_DIR$"/><option name="gradleJvm" value="#GRADLE_LOCAL_JAVA_HOME"/><option name="modules"><set><option value="$PROJECT_DIR$"/><option value="$PROJECT_DIR$/app"/><option value="$PROJECT_DIR$/iconfont-lib"/></set></option></GradleProjectSettings></option></component></project>''')
    report.unlink(missing_ok=True)
    command = [str(plugin / "gradlew"), f"-Dorg.gradle.java.home={args.gradle_jdk.resolve()}", "runIde", "-PfontE2E",
               f"-PfontTestJava={args.ide_jdk.resolve() / 'bin/java'}",
               f"-PfontE2EProject={project}", f"-PfontE2EReport={report}"]
    if args.keep_open:
        command.append("-PfontE2EKeepOpen")
    server = None
    transport = None
    manifest = json.loads((ROOT / "fixtures/library-font-cases.json").read_text())
    if args.remote_maven:
        outside = Path(tempfile.mkdtemp(prefix="iconfont-http-maven-")).resolve()
        repository = outside / "repository"
        gradle_home = outside / "gradle-home"
        shutil.copytree(ROOT / "fixtures/repository", repository)
        prepare_remote_cache(Path(os.environ.get("GRADLE_USER_HOME", Path.home() / ".gradle")), gradle_home)
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(RecordingHandler, directory=str(repository)))
        server.requests = []
        server.daemon_threads = True
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        repository_url = f"http://127.0.0.1:{server.server_port}/"
        configure_remote_repository(project, repository_url)
        command += [f"-PfontE2EGradleHome={gradle_home}", f"-PfontE2ERepositoryRoot={repository}"]
        transport = {"mode": "http_maven", "repository_url": repository_url, "repository_root": str(repository),
                     "gradle_user_home": str(gradle_home), "project": str(project),
                     "project_fixture_repository_absent": True, "initial_fixture_cache_empty": True,
                     "non_fixture_downloads_reused": True, "transforms_reused": False}
        (work / "transport.json").write_text(json.dumps(transport, indent=2) + "\n")
        server_thread.start()
    ET.ElementTree(gradle_xml).write(project / ".idea/gradle.xml", encoding="unicode")
    print("Launching isolated IDE test:", command, flush=True)
    try:
        completed = subprocess.run(command, cwd=plugin, timeout=None if args.keep_open else 600)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            java = str(args.ide_jdk.resolve() / "bin/java") + " "
            for row in subprocess.check_output(["ps", "-axo", "pid=,args="], text=True).splitlines():
                pid, process = row.strip().split(None, 1)
                if process.startswith(java) and f"-Diconfontviewer.e2e.project={project}" in process:
                    os.kill(int(pid), signal.SIGTERM)
        raise SystemExit(f"IDE test exceeded 10 minutes; inspect {report}")
    finally:
        if server:
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=5)
            (work / "http-requests.json").write_text(json.dumps(server.requests, indent=2) + "\n")
            stop_environment = dict(os.environ, JAVA_HOME=str(args.gradle_jdk.resolve()))
            try:
                stopped = subprocess.run([str(project / "gradlew"), "--stop", f"--gradle-user-home={gradle_home}"],
                                         cwd=project, env=stop_environment, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, text=True, timeout=30)
                (work / "gradle-stop.log").write_text(stopped.stdout)
                transport["gradle_daemons_stopped"] = stopped.returncode == 0
            except subprocess.TimeoutExpired:
                transport["gradle_daemons_stopped"] = False
    if not report.is_file():
        raise SystemExit(f"No IDE report produced (Gradle exit {completed.returncode})")
    result = json.loads(report.read_text())
    if transport is not None:
        try:
            transport["downloads"] = verify_remote_downloads(gradle_home, server.requests, manifest)
            transport["http_downloads_verified"] = True
        except RuntimeError as failure:
            result["status"] = "failed"
            transport["error"] = str(failure)
        result["transport"] = transport
        report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
