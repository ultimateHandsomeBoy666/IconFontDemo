#!/usr/bin/env python3
"""Open a disposable Demo copy in the plugin's isolated Android Studio sandbox."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-dir", type=Path, required=True)
    parser.add_argument("--gradle-jdk", type=Path, required=True, help="JDK 17 for Demo Gradle 8.4")
    parser.add_argument("--ide-jdk", type=Path, required=True, help="Bundled runtime used to launch Android Studio")
    parser.add_argument("--keep-open", action="store_true", help="Keep the sandbox open for a real gutter/popup UI smoke check")
    args = parser.parse_args()
    plugin = args.plugin_dir.resolve()
    work = plugin / "build/font-e2e"
    project = work / "project"
    report = work / "report.json"
    if project.exists():
        if not (project / ".font-e2e-sandbox").is_file():
            raise SystemExit(f"Refusing to replace an unmarked directory: {project}")
        shutil.rmtree(project)
    shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns(".git", ".idea", ".gradle", "build", "__pycache__"))
    (project / ".font-e2e-sandbox").write_text("Disposable fixture project. Safe to replace.\n")
    (project / ".gradle").mkdir()
    (project / ".gradle/config.properties").write_text(f"java.home={args.gradle_jdk.resolve()}\n")
    (project / ".idea").mkdir()
    (project / ".idea/gradle.xml").write_text('''<project version="4"><component name="GradleSettings"><option name="linkedExternalProjectsSettings"><GradleProjectSettings><option name="externalProjectPath" value="$PROJECT_DIR$"/><option name="gradleJvm" value="#GRADLE_LOCAL_JAVA_HOME"/><option name="modules"><set><option value="$PROJECT_DIR$"/><option value="$PROJECT_DIR$/app"/><option value="$PROJECT_DIR$/iconfont-lib"/></set></option></GradleProjectSettings></option></component></project>''')
    report.unlink(missing_ok=True)
    command = [str(plugin / "gradlew"), f"-Dorg.gradle.java.home={args.gradle_jdk.resolve()}", "runIde", "-PfontE2E",
               f"-PfontTestJava={args.ide_jdk.resolve() / 'bin/java'}",
               f"-PfontE2EProject={project}", f"-PfontE2EReport={report}"]
    if args.keep_open:
        command.append("-PfontE2EKeepOpen")
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
    if not report.is_file():
        raise SystemExit(f"No IDE report produced (Gradle exit {completed.returncode})")
    result = json.loads(report.read_text())
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
