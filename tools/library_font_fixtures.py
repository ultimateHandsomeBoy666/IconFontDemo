#!/usr/bin/env python3
"""Build deterministic, real AAR/JAR fixtures. External TTFs never touch source directories."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GROUP = "com.example.iconfontfixtures"
VERSION = "1.0.0"
LEGACY = [
    "app/src/main/assets/fonts/fontawesome.ttf",
    "app/src/main/assets/fonts/material_icons.ttf",
    "app/src/main/res/font/material_icons.ttf",
    "iconfont-lib/src/main/assets/fonts/feather_icons.ttf",
    "iconfont-lib/src/main/res/font/feather_icons.ttf",
]


def tables(data):
    count = struct.unpack_from(">H", data, 4)[0]
    result = {}
    for i in range(count):
        tag, _, offset, size = struct.unpack_from(">4sIII", data, 12 + 16 * i)
        result[tag] = data[offset:offset + size]
    return result


def cmap(data):
    table = tables(data)[b"cmap"]
    result = {}
    for i in range(struct.unpack_from(">H", table, 2)[0]):
        platform, encoding, offset = struct.unpack_from(">HHI", table, 4 + 8 * i)
        if platform != 0 and (platform, encoding) not in ((3, 1), (3, 10)):
            continue
        fmt = struct.unpack_from(">H", table, offset)[0]
        if fmt == 4:
            segments = struct.unpack_from(">H", table, offset + 6)[0] // 2
            ends = struct.unpack_from(f">{segments}H", table, offset + 14)
            starts_at = offset + 16 + 2 * segments
            starts = struct.unpack_from(f">{segments}H", table, starts_at)
            deltas_at = starts_at + 2 * segments
            ranges_at = deltas_at + 2 * segments
            for j, (start, end) in enumerate(zip(starts, ends)):
                delta = struct.unpack_from(">h", table, deltas_at + 2 * j)[0]
                distance = struct.unpack_from(">H", table, ranges_at + 2 * j)[0]
                for cp in range(start, min(end, 0xFFFE) + 1):
                    glyph = (cp + delta) & 0xFFFF
                    if distance:
                        pos = ranges_at + 2 * j + distance + 2 * (cp - start)
                        glyph = struct.unpack_from(">H", table, pos)[0]
                        if glyph:
                            glyph = (glyph + delta) & 0xFFFF
                    if glyph:
                        result[cp] = glyph
        elif fmt == 12:
            count = struct.unpack_from(">I", table, offset + 12)[0]
            for j in range(count):
                start, end, glyph = struct.unpack_from(">III", table, offset + 16 + 12 * j)
                for cp in range(start, end + 1):
                    if glyph + cp - start:
                        result[cp] = glyph + cp - start
    return result


def checksum(data):
    padded = data + bytes(-len(data) % 4)
    return sum(struct.unpack(f">{len(padded) // 4}I", padded)) & 0xFFFFFFFF


def probe_font(original, codepoints, family):
    """Preserve original licensed outlines; expose ONLY the two case-specific codepoints."""
    original_map = cmap(original)
    glyphs = [original_map[0xE88A], original_map[0xE8B6]]  # home, search
    font_tables = tables(original)
    font_tables.pop(b"DSIG", None)
    segments = len(codepoints) + 1
    power = 2 ** (segments.bit_length() - 1)
    subtable = struct.pack(">7H", 4, 16 + 8 * segments, 0, 2 * segments,
                           2 * power, power.bit_length() - 1, 2 * segments - 2 * power)
    subtable += struct.pack(f">{segments}H", *codepoints, 0xFFFF) + b"\0\0"
    subtable += struct.pack(f">{segments}H", *codepoints, 0xFFFF)
    subtable += struct.pack(f">{segments}H", *[(g - cp) & 0xFFFF for cp, g in zip(codepoints, glyphs)], 1)
    subtable += bytes(2 * segments)
    font_tables[b"cmap"] = struct.pack(">HHHHI", 0, 1, 3, 1, 12) + subtable
    old_name = font_tables[b"name"]
    count, storage = struct.unpack_from(">HH", old_name, 2)
    records, strings = [], bytearray()
    replacements = {1: family, 2: "Regular", 3: family + "-1", 4: family, 6: family,
                    16: family, 17: "Regular", 18: family, 21: family, 22: "Regular"}
    for i in range(count):
        platform, encoding, language, name_id, length, offset = struct.unpack_from(">6H", old_name, 6 + 12 * i)
        value = old_name[storage + offset:storage + offset + length]
        if name_id in replacements:
            value = replacements[name_id].encode("utf-16-be" if platform in (0, 3) else "ascii")
        records.append(struct.pack(">6H", platform, encoding, language, name_id, len(value), len(strings)))
        strings.extend(value)
    font_tables[b"name"] = struct.pack(">3H", 0, len(records), 6 + 12 * len(records)) + b"".join(records) + strings
    head = bytearray(font_tables[b"head"])
    head[8:12] = bytes(4)
    font_tables[b"head"] = bytes(head)
    count = len(font_tables)
    power = 2 ** (count.bit_length() - 1)
    output = bytearray(struct.pack(">I4H", 0x10000, count, 16 * power,
                                   power.bit_length() - 1, 16 * (count - power)))
    offset = 12 + 16 * count
    body = bytearray()
    head_offset = None
    for tag, value in sorted(font_tables.items()):
        output.extend(struct.pack(">4sIII", tag, checksum(value), offset, len(value)))
        if tag == b"head":
            head_offset = offset
        padded = value + bytes(-len(value) % 4)
        body.extend(padded)
        offset += len(padded)
    output.extend(body)
    struct.pack_into(">I", output, head_offset + 8, (0xB1B0AFBA - checksum(output)) & 0xFFFFFFFF)
    return bytes(output)


def archive(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, value in entries.items():
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, value)
    return output.getvalue()


def build_payloads():
    original = (ROOT / LEGACY[1]).read_bytes()
    used = set().union(*(set(cmap((ROOT / path).read_bytes())) for path in LEGACY))
    available = iter(cp for cp in range(0xE900, 0xF8FF) if cp not in used)
    specs = [
        ("source_baseline", "source", "iconfont-lib/src/main/assets/test-probes/icon_probe_source_baseline.ttf"),
        ("aar_font", "path-fixtures", "res/font/icon_probe_font.ttf"),
        ("aar_qualified", "path-fixtures", "res/font-v26/icon_probe_qualified.ttf"),
        ("aar_raw", "path-fixtures", "res/raw/icon_probe_raw.ttf"),
        ("assets_root", "path-fixtures", "assets/icon_probe_assets_root.ttf"),
        ("assets_deep", "path-fixtures", "assets/custom/a/b/icon_probe_assets_deep.ttf"),
        ("classes_root", "path-fixtures", "classes.jar!/icon_probe_classes_root.ttf"),
        ("classes_deep", "path-fixtures", "classes.jar!/org/example/custom/icon_probe_classes_deep.ttf"),
        ("aar_extra_jar", "path-fixtures", "libs/extra-fonts.jar!/custom/icon_probe_extra.ttf"),
        ("nested_jar", "path-fixtures", "assets/payload/outer.jar!/libs/inner.jar!/deep/icon_probe_nested.ttf"),
        ("nested_after", "path-fixtures", "assets/payload/outer.jar!/after/icon_probe_after.ttf"),
        ("nested_aar", "path-fixtures", "assets/payload/inner.aar!/custom/icon_probe_nested_aar.ttf"),
        ("aar_custom", "path-fixtures", "custom/deep/icon_probe_custom.ttf"),
        ("uppercase", "path-fixtures", "assets/case/icon_probe_upper.TTF"),
        ("unicode_path", "path-fixtures", "assets/custom folder/中文/icon_probe_unicode.ttf"),
        ("same_name_a", "path-fixtures", "assets/a/icon_shared.ttf"),
        ("same_name_b", "path-fixtures", "assets/b/icon_shared.ttf"),
        ("manual_enable", "path-fixtures", "assets/custom/plainface.ttf"),
        ("library_resource", "path-fixtures", "assets/library/icon_probe_library_resource.ttf"),
        ("jar_root", "standalone-fonts", "icon_probe_jar_root.ttf"),
        ("jar_deep", "standalone-fonts", "org/example/deep/icon_probe_jar_deep.ttf"),
        ("transitive", "leaf-fonts", "custom/icon_probe_transitive.ttf"),
    ]
    cases, output = [], {}
    trees = {name: {} for name in ("path-fixtures", "standalone-fonts", "leaf-fonts")}
    for case_id, artifact, entry in specs:
        cps = [next(available), next(available)]
        family = "IconFontProbe_" + case_id
        case = dict(id=case_id, artifact=artifact, entry=entry, codepoints=cps, family=family,
                    resources=[f"probe_{case_id}_home", f"probe_{case_id}_search"],
                    default_enabled=case_id != "manual_enable", glyphs=["home", "search"])
        cases.append(case)
        font = probe_font(original, cps, family)
        if artifact == "source":
            output[entry] = font
        else:
            tree = trees[artifact]
            parts = entry.split("!/")
            for part in parts[:-1]:
                tree = tree.setdefault(part, {})
            tree[parts[-1]] = font

    def pack_tree(tree):
        return archive({name: pack_tree(value) if isinstance(value, dict) else value for name, value in tree.items()})

    lib = next(case for case in cases if case["id"] == "library_resource")
    library_xml = "<resources>\n" + "".join(
        f'    <string name="{name}">&#x{cp:X};</string>\n' for name, cp in zip(lib["resources"], lib["codepoints"])) + "</resources>\n"
    trees["path-fixtures"]["AndroidManifest.xml"] = b'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example.iconfontfixtures"><uses-sdk android:minSdkVersion="26"/></manifest>'
    trees["path-fixtures"]["assets/payload/inner.aar"]["AndroidManifest.xml"] = b'<manifest package="com.example.iconfontfixtures.nested"/>'
    trees["path-fixtures"]["res/values/probe_strings.xml"] = library_xml.encode()
    trees["path-fixtures"]["R.txt"] = "".join(f"int string {name} 0x0\n" for name in lib["resources"]).encode()
    trees["path-fixtures"]["assets/errors/icon_probe_corrupt.ttf"] = b"intentionally invalid TTF"
    trees["path-fixtures"]["assets/errors/broken.jar"] = b"intentionally invalid JAR"
    artifacts = []
    for artifact in ("path-fixtures", "standalone-fonts", "leaf-fonts", "wrapper-a", "wrapper-b"):
        extension = "aar" if artifact == "path-fixtures" else "jar"
        tree = trees.get(artifact, {"META-INF/MANIFEST.MF": b"Manifest-Version: 1.0\n\n"})
        data = pack_tree(tree)
        prefix = f"fixtures/repository/{GROUP.replace('.', '/')}/{artifact}/{VERSION}/{artifact}-{VERSION}"
        output[prefix + "." + extension] = data
        dependencies = ""
        if artifact.startswith("wrapper-"):
            dependencies = f"<dependencies><dependency><groupId>{GROUP}</groupId><artifactId>leaf-fonts</artifactId><version>{VERSION}</version></dependency></dependencies>"
        pom = f'<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>{GROUP}</groupId><artifactId>{artifact}</artifactId><version>{VERSION}</version><packaging>{extension}</packaging>{dependencies}</project>\n'
        output[prefix + ".pom"] = pom.encode()
        artifacts.append(dict(id=artifact, path=prefix + "." + extension, sha256=hashlib.sha256(data).hexdigest()))
    artifact_paths = {item["id"]: item["path"] for item in artifacts}
    for case in cases:
        case["path"] = case["entry"] if case["artifact"] == "source" else artifact_paths[case["artifact"]] + "!/" + case["entry"]
    manifest = dict(version=VERSION, cases=cases, artifacts=artifacts, legacy_fonts=LEGACY,
                    corrupt_font="assets/errors/icon_probe_corrupt.ttf", source_font=LEGACY[1],
                    provenance="Original font outlines and license records retained; cmap and family names replaced for isolation.")
    output["fixtures/library-font-cases.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    host = [case for case in cases if case["id"] != "library_resource"]
    output["app/src/main/res/values/library_font_probes.xml"] = ("<resources>\n" + "".join(
        f'    <string name="{name}">&#x{cp:X};</string>\n' for case in host for name, cp in zip(case["resources"], case["codepoints"])) + "</resources>\n").encode()
    kotlin = "package com.example.iconfontdemo\n\n// Generated probes: each font exposes only its own two codepoints.\nobject LibraryFontProbes {\n"
    kotlin += "".join(f'    val {case["id"]} = intArrayOf(\n        R.string.{case["resources"][0]},\n        R.string.{case["resources"][1]}\n    )\n' for case in host)
    output["app/src/main/java/com/example/iconfontdemo/LibraryFontProbes.kt"] = (kotlin + "}\n").encode()
    output["app/src/main/java/com/example/iconfontdemo/ExternalLibraryResourceProbes.kt"] = ("package com.example.iconfontdemo\n\nimport com.example.iconfontfixtures.R\n\nobject ExternalLibraryResourceProbes {\n" + "".join(f"    val glyph{i} = R.string.{name}\n" for i, name in enumerate(lib["resources"])) + "}\n").encode()
    output["app/src/main/java/com/example/iconfontdemo/ExternalLibraryJavaResourceProbes.java"] = ("package com.example.iconfontdemo;\n\nimport com.example.iconfontfixtures.R;\n\npublic final class ExternalLibraryJavaResourceProbes {\n" + "".join(f"    public static final int glyph{i} = R.string.{name};\n" for i, name in enumerate(lib["resources"])) + "}\n").encode()
    java = "package com.example.iconfontdemo;\n\npublic final class LibraryFontJavaProbes {\n"
    java += "".join(f'    public static final int[] {case["id"]} = {{\n        R.string.{case["resources"][0]},\n        R.string.{case["resources"][1]}\n    }};\n' for case in host)
    output["app/src/main/java/com/example/iconfontdemo/LibraryFontJavaProbes.java"] = (java + "}\n").encode()
    xml = '<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical">\n'
    xml += "".join(f'    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="@string/{name}" />\n' for case in cases for name in case["resources"])
    output["app/src/main/res/layout/library_font_probes.xml"] = (xml + "</LinearLayout>\n").encode()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", action="store_true", help="write fonts, archives and generated references")
    mode.add_argument("--check", action="store_true", help="verify generated outputs without writing")
    args = parser.parse_args()
    payloads = build_payloads()
    for relative, data in payloads.items():
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"Missing or stale generated file: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f'{"Verified" if args.check else "Generated"} {len(payloads)} files, 22 isolated font cases.')


if __name__ == "__main__":
    main()
