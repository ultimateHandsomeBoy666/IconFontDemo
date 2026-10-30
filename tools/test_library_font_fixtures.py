import io
import json
import unittest
import xml.etree.ElementTree as ET
import zipfile

from library_font_fixtures import ROOT, LEGACY, archive, build_payloads, cmap, checksum


def read_entry(payloads, path):
    parts = path.split("!/")
    value = payloads[parts[0]]
    for entry in parts[1:]:
        with zipfile.ZipFile(io.BytesIO(value)) as z:
            value = z.read(entry)
    return value


class LibraryFontFixturesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads = build_payloads()
        cls.manifest = json.loads(cls.payloads["fixtures/library-font-cases.json"])

    def test_generated_files_are_current(self):
        for path, data in self.payloads.items():
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())
                self.assertEqual((ROOT / path).read_bytes(), data)

    def test_every_font_exposes_only_its_own_codepoints(self):
        used = set()
        for case in self.manifest["cases"]:
            with self.subTest(case=case["id"]):
                data = read_entry(self.payloads, case["path"])
                self.assertEqual(set(cmap(data)), set(case["codepoints"]))
                self.assertFalse(used.intersection(case["codepoints"]))
                used.update(case["codepoints"])
                self.assertEqual(checksum(data), 0xB1B0AFBA)
        for path in LEGACY:
            self.assertFalse(used.intersection(cmap((ROOT / path).read_bytes())), path)

    def test_no_external_probe_ttf_is_present_in_source(self):
        expected = set(LEGACY)
        expected.add(next(case["path"] for case in self.manifest["cases"] if case["artifact"] == "source"))
        actual = {str(path.relative_to(ROOT)) for folder in (ROOT / "app/src", ROOT / "iconfont-lib/src")
                  for path in folder.rglob("*") if path.is_file() and path.suffix.lower() == ".ttf"}
        self.assertEqual(expected, actual)

    def test_binary_library_strings_do_not_exist_in_host(self):
        lib = next(case for case in self.manifest["cases"] if case["id"] == "library_resource")
        host = ET.fromstring(self.payloads["app/src/main/res/values/library_font_probes.xml"])
        host_names = {tag.attrib["name"] for tag in host}
        self.assertFalse(host_names.intersection(lib["resources"]))
        artifact = next(a for a in self.manifest["artifacts"] if a["id"] == "path-fixtures")
        with zipfile.ZipFile(io.BytesIO(self.payloads[artifact["path"]])) as z:
            external = ET.fromstring(z.read("res/values/probe_strings.xml"))
            self.assertEqual(set(lib["resources"]), {tag.attrib["name"] for tag in external})

    def test_shared_leaf_is_only_a_transitive_dependency(self):
        app = (ROOT / "app/build.gradle").read_text()
        self.assertNotIn("implementation 'com.example.iconfontfixtures:leaf-fonts", app)
        for artifact in ("wrapper-a", "wrapper-b"):
            pom_path = next(path for path in self.payloads if path.endswith(f"{artifact}-1.0.0.pom"))
            pom = ET.fromstring(self.payloads[pom_path])
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            self.assertEqual(pom.find("m:dependencies/m:dependency/m:artifactId", ns).text, "leaf-fonts")

    def test_nested_child_precedes_sibling_so_premature_close_is_detectable(self):
        artifact = next(a for a in self.manifest["artifacts"] if a["id"] == "path-fixtures")
        with zipfile.ZipFile(io.BytesIO(self.payloads[artifact["path"]])) as aar:
            with zipfile.ZipFile(io.BytesIO(aar.read("assets/payload/outer.jar"))) as outer:
                self.assertEqual(outer.namelist(), ["libs/inner.jar", "after/icon_probe_after.ttf"])

    def test_archives_are_deterministic(self):
        self.assertEqual(archive({"a.ttf": b"a", "b.ttf": b"b"}), archive({"a.ttf": b"a", "b.ttf": b"b"}))

    def test_outer_and_nested_aars_have_the_mandatory_manifest(self):
        artifact = next(a for a in self.manifest["artifacts"] if a["id"] == "path-fixtures")
        for path in (artifact["path"], artifact["path"] + "!/assets/payload/inner.aar"):
            with zipfile.ZipFile(io.BytesIO(read_entry(self.payloads, path))) as aar:
                manifest = ET.fromstring(aar.read("AndroidManifest.xml"))
                self.assertEqual(manifest.tag, "manifest")
                self.assertTrue(manifest.attrib["package"])


if __name__ == "__main__":
    unittest.main()
