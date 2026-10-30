"""Guard the remote test against cache hits being mistaken for HTTP downloads."""
from functools import partial
import hashlib
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import urlopen

from run_library_font_e2e import FIXTURE_GROUP, RecordingHandler, prepare_remote_cache, verify_remote_downloads


class RemoteMavenEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.payload = b"isolated fixture artifact"
        self.relative = Path("com/example/iconfontfixtures/example/1.0.0/example-1.0.0.aar")
        self.manifest = {"version": "1.0.0", "artifacts": [{
            "id": "example", "path": "fixtures/repository/" + self.relative.as_posix(),
            "sha256": hashlib.sha256(self.payload).hexdigest()}]}
        self.home = self.root / "gradle-home"
        self.cached = self.home / "caches/modules-2/files-2.1" / FIXTURE_GROUP / "example/1.0.0/hash" / self.relative.name
        self.cached.parent.mkdir(parents=True)

    def successful_requests(self):
        return [{"method": "GET", "path": "/" + path.as_posix(), "status": 200}
                for path in (self.relative, self.relative.with_suffix(".pom"))]

    def test_cached_artifact_without_http_get_does_not_count(self):
        self.cached.write_bytes(self.payload)
        with self.assertRaisesRegex(RuntimeError, "No successful HTTP GET"):
            verify_remote_downloads(self.home, self.successful_requests()[1:], self.manifest)

    def test_http_success_with_wrong_cached_bytes_does_not_count(self):
        self.cached.write_bytes(b"stale or unrelated artifact")
        with self.assertRaisesRegex(RuntimeError, "bytes differ"):
            verify_remote_downloads(self.home, self.successful_requests(), self.manifest)

    def test_real_http_gets_and_matching_cached_bytes_are_recorded(self):
        repository = self.root / "repository"
        artifact = repository / self.relative
        artifact.parent.mkdir(parents=True)
        artifact.write_bytes(self.payload)
        artifact.with_suffix(".pom").write_text("<project/>")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(RecordingHandler, directory=str(repository)))
        server.requests = []
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}/"
            with urlopen(base + self.relative.as_posix(), timeout=5) as response:
                self.cached.write_bytes(response.read())
            with urlopen(base + self.relative.with_suffix(".pom").as_posix(), timeout=5) as response:
                self.assertEqual(response.read(), b"<project/>")
            evidence = verify_remote_downloads(self.home, server.requests, self.manifest)
            self.assertTrue(evidence[0]["artifact_and_pom_http_get"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_cache_seed_excludes_fixture_group_and_all_transforms(self):
        source = self.root / "shared-home"
        for relative in [f"caches/modules-2/files-2.1/{FIXTURE_GROUP}/example/old.aar",
                         f"caches/modules-2/metadata-2.1/descriptors/{FIXTURE_GROUP}/old.bin",
                         "caches/transforms-3/old/font.ttf", "caches/modules-2/files-2.1/other/lib.jar"]:
            file = source / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b"cached")
        destination = self.root / "new-home"
        prepare_remote_cache(source, destination)
        self.assertTrue((destination / "caches/modules-2/files-2.1/other/lib.jar").is_file())
        self.assertFalse((destination / "caches/transforms-3").exists())
        self.assertFalse(any(path.name == FIXTURE_GROUP for path in destination.rglob("*")))


if __name__ == "__main__":
    unittest.main()
