# Library font regression corpus

The source-module baseline remains `implementation project(':iconfont-lib')`. The additional dependencies are real AAR/JAR artifacts from `fixtures/repository`; the fixture producer is a Python script, not another imported Gradle module.

`fixtures/library-font-cases.json` is the case manifest. It records the artifact, complete archive entry path, two exclusive codepoints, expected font family and expected default enabled state for each case. All probe fonts retain the Material Icons outlines and license records from `app/src/main/assets/fonts/material_icons.ttf`, but expose only their case-specific home/search codepoints. External probe TTFs are generated in memory and written directly into archives. The only additional loose source TTF is the source-module baseline, which has different codepoints.

The corpus covers `res/font`, `res/font-v26`, `res/raw`, assets root/deep/custom directories, uppercase extensions, spaces and Unicode paths, equal filenames in different directories, `classes.jar`, additional `libs/*.jar`, standalone JARs, nested JAR/AAR entries, a valid sibling after a nested archive, a nonstandard AAR custom directory, a font without auto-enable keywords, AAR-owned strings, and a shared transitive JAR reached through two wrapper dependencies. Both outer and nested AARs contain their required manifest. Invalid TTF/JAR payloads live under assets so Gradle can import the valid enclosing AAR.

## Generate and check

From the Demo root:

```sh
python3 -B tools/library_font_fixtures.py --generate
python3 -B tools/library_font_fixtures.py --check
python3 -B -m unittest discover -s tools -p 'test_library_font_fixtures.py' -v
```

Generation is explicit and is not attached to Gradle sync. Generated binaries and source references are checked in together. For later corpus revisions, bump its Maven version and the dependency coordinates together to avoid cached artifacts with reused versions.

The Python tests check real output bytes, font checksums and cmap exclusivity, the absence of loose external fonts in source, AAR-owned strings, transitive-only dependency wiring and nested archive entry order. They do not execute the Kotlin plugin.

## Plugin unit tests

From IconFontViewer:

```sh
./gradlew test -PfontFixturesDir=../IconFontDemo
```

`FontFileAccessTest` exercises the production directory/archive scanner, including direct TTFs under a synthetic `jars/` tree, overlapping roots, symlink loops, nested entry streams, missing entries, invalid archives and cancellation. `LibraryFontCorpusTest` loads each real generated font with `Font.createFont`, renders its glyphs and checks that no other probe or legacy source font can render its codepoints. Without `fontFixturesDir`, only the independent scanner tests run.

## Real Android Studio integration

Unit tests cannot prove that Android Studio exposes the expected roots after Gradle sync, resolves external Android string resources, or supplies the expected PSI for Kotlin/Java/XML. Run the IDE integration suite as well:

```sh
python3 -B tools/run_library_font_e2e.py \
  --plugin-dir ../IconFontViewer \
  --gradle-jdk /path/to/jdk17 \
  --ide-jdk '/Applications/Android Studio.app/Contents/jbr/Contents/Home'
```

The runner creates `IconFontViewer/build/font-e2e/project`, excluding user IDE settings, Git metadata and build output, and opens that copy in the plugin's isolated `runIde` sandbox. It does not modify the original Demo settings or install an Android app. JDK 17 runs Gradle; the IDE uses its bundled runtime independently.

The opt-in `-PfontE2E` build compiles `src/e2e/kotlin` and registers its startup activity only for that test build. Normal plugin artifacts explicitly exclude the E2E package and startup activity. The runner fails after 10 minutes if startup/import never completes; `--keep-open` is available for a manual UI session.

After a real Gradle import and source-baseline indexing, the suite invokes the production scanner, checks each expected path, and enables only one exact font path at a time. Waiting for the indexed source baseline prevents a brief smart-mode gap after model import from starting the checks too early. It checks Kotlin/Java/XML definition/layout line markers, selected font identity, nonempty gutter icon rendering, popup candidate names and the absence of markers when disabled. Original AAR and extracted copies are tested separately when both exist. It also verifies repeat scanning, preserved explicit enabled state and same-path font replacement/reload. The final JSON report is `IconFontViewer/build/font-e2e/report.json`; failure or a missing report produces a failing runner exit code.

This is IDE integration automation. Physical mouse clicks, keyboard navigation and actual popup selection/replacement remain a separate UI smoke check; the automatic suite checks the real line-marker provider and popup data rather than simulating those mouse events.

For a manual smoke check, open `LibraryFontProbes.kt`, `LibraryFontJavaProbes.java`, `ExternalLibraryResourceProbes.kt`, `res/values/library_font_probes.xml` and `res/layout/library_font_probes.xml`. Disable every other font in Tools → IconFontViewer and enable only the exact path under test. Confirm home/search previews, open the popup, replace one reference, and undo. A source module preview alone does not count as an AAR/JAR pass.

## HTTP Maven comparison

Use the same command with `--remote-maven` to test actual Maven downloads rather than loading the binary artifacts from a repository directory inside the project:

```sh
python3 -B tools/run_library_font_e2e.py --remote-maven \
  --plugin-dir ../IconFontViewer \
  --gradle-jdk /path/to/jdk17 \
  --ide-jdk '/Applications/Android Studio.app/Contents/jbr/Contents/Home'
```

The runner serves an identical copy of the Maven repository from an OS temporary directory outside the project, bound only to `127.0.0.1` on an ephemeral port. The disposable project omits `fixtures/repository` and uses an exclusive HTTP repository for `com.example.iconfontfixtures`, preventing fallback to the checked-in files or other repositories. This does not publish any artifacts to a company or public Maven service.

The IDE receives a separate `GRADLE_USER_HOME`. Existing non-fixture downloads and Gradle 8.4 distribution files may be reused to avoid unrelated downloads; fixture artifacts and all transform outputs are excluded. Thus the fixture namespace starts empty while the normal Gradle home remains untouched. The runner requires successful HTTP GETs for all five binary artifacts and their POMs and verifies the SHA-256 of the downloaded files in `caches/modules-2/files-2.1` against the corpus manifest.

Inside the real IDE, the suite requires the original cached AAR/JAR path for every external font case, separately checks extracted copies exposed by the Android dependency model, and rejects matching probe fonts from the project or shared cache. Each exact font path still runs the isolated Kotlin/Java/XML checks, disabled-font assertions and rescan/cache checks. The source-module baseline remains in the project with its own codepoints.

The remote project and report are under `IconFontViewer/build/font-e2e-remote/`. `report.json` contains editor checks and HTTP/download evidence; `http-requests.json` contains the HTTP request log; `transport.json` records the temporary repository and Gradle-home locations. The HTTP server and the isolated Gradle daemons are stopped after the run. Temporary downloaded files are retained for inspection. The HTTP mode covers transport, download-cache and transformed-cache paths; repository authentication and company proxy policies are outside this comparison.

The additional evidence guards can be run without launching Gradle or the IDE:

```sh
python3 -B -m unittest discover -s tools -p 'test_library_font_e2e.py' -v
```

## Verified on 2026-10-30

- Fixture contract tests: 8 passed.
- Production scanner and real-font JVM tests: 9 passed.
- Demo Kotlin and Java compilation: passed with the binary fixtures, including AAR-owned `R` resources.
- Real Android Studio integration on `AI-262.10968.63.2622.16730706`: 22 cases, 40 exact font paths (13 physical, 27 archive paths), 158 editor-surface checks, plus isolated popup candidates, disabled-font checks and rescan/cache checks passed.
- Native UI smoke via computer-use mouse/keyboard control: Kotlin, Java and XML layout passed with only the standalone JAR-root probe font enabled. Each gutter click opened the real home/search popup; selecting search replaced the saved reference and updated the gutter. Java popup search filtering also passed. Undo and save restored all three files byte-for-byte. These checks ran in a disposable Demo copy; the original probe files stayed unchanged.
- HTTP Maven comparison on the same IDE: 22 cases, 40 exact font paths and 158 editor-surface checks passed with the project-local fixture repository absent. All 21 binary-font cases were required to resolve from the isolated download/transform caches. Successful HTTP GETs for all five binary artifacts and five POMs and matching downloaded SHA-256 values were verified. The four HTTP/cache evidence guard tests also passed.
- The local-Maven baseline was rerun with the updated harness and passed with identical case, path-representation and editor-surface coverage. Comparison evidence is in `build/library-font-maven-comparison.json`; the remote IDE report and HTTP log are copied to `build/library-font-remote-ide-report.json` and `build/library-font-http-requests.json`.
- The normal plugin descriptor and class entries were checked separately to exclude the opt-in test harness.

The IDE report is also copied to `build/library-font-ide-report.json` in the Demo. UI smoke evidence (saved-file hashes, replacement details and undo results) is in `build/library-font-ui-smoke-report.json`. The UI smoke is an agent-driven session, not a repeatable scripted suite covering every font location. Other IDE versions were not tested. No Android app was installed or launched.
