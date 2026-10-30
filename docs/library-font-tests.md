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

## Verified on 2026-10-30

- Fixture contract tests: 8 passed.
- Production scanner and real-font JVM tests: 9 passed.
- Demo Kotlin and Java compilation: passed with the binary fixtures, including AAR-owned `R` resources.
- Real Android Studio integration on `AI-262.10968.63.2622.16730706`: 22 cases, 40 exact font paths (13 physical, 27 archive paths), 158 editor-surface checks, plus isolated popup candidates, disabled-font checks and rescan/cache checks passed.
- Native UI smoke via computer-use mouse/keyboard control: Kotlin, Java and XML layout passed with only the standalone JAR-root probe font enabled. Each gutter click opened the real home/search popup; selecting search replaced the saved reference and updated the gutter. Java popup search filtering also passed. Undo and save restored all three files byte-for-byte. These checks ran in a disposable Demo copy; the original probe files stayed unchanged.
- The normal plugin descriptor and class entries were checked separately to exclude the opt-in test harness.

The IDE report is also copied to `build/library-font-ide-report.json` in the Demo. UI smoke evidence (saved-file hashes, replacement details and undo results) is in `build/library-font-ui-smoke-report.json`. The UI smoke is an agent-driven session, not a repeatable scripted suite covering every font location. Other IDE versions were not tested. No Android app was installed or launched.
