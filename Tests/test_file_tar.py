import signal

from PIL import Image, TarIO

from .helper import PillowTestCase, unittest

codecs = dir(Image.core)

# Sample tar archive
TEST_TAR_FILE = "Tests/images/hopper.tar"


class TestFileTar(PillowTestCase):
    def setUp(self):
        if "zip_decoder" not in codecs and "jpeg_decoder" not in codecs:
            self.skipTest("neither jpeg nor zip support available")

    def test_sanity(self):
        for codec, test_path, format in [
            ["zip_decoder", "hopper.png", "PNG"],
            ["jpeg_decoder", "hopper.jpg", "JPEG"],
        ]:
            if codec in codecs:
                tar = TarIO.TarIO(TEST_TAR_FILE, test_path)
                im = Image.open(tar)
                im.load()
                self.assertEqual(im.mode, "RGB")
                self.assertEqual(im.size, (128, 128))
                self.assertEqual(im.format, format)

    def test_close(self):
        tar = TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")
        tar.close()

    def test_contextmanager(self):
        with TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg"):
            pass

    @unittest.skipUnless(hasattr(signal, "SIGALRM"), "needs SIGALRM")
    def test_odd(self):
        with open(TEST_TAR_FILE, "rb") as f:
            data = bytearray(f.read())

        def timeout(signum, frame):
            raise AssertionError("timed out")

        for size in (b"-1", b"0", b"-1000"):
            data[124:135] = size.rjust(11)

            tmpfile = self.tempfile("temp.tar")
            with open(tmpfile, "wb") as f:
                f.write(data)

            old_handler = signal.signal(signal.SIGALRM, timeout)
            signal.alarm(5)
            try:
                with self.assertRaises(ValueError) as e:
                    TarIO.TarIO(tmpfile, "test")
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            self.assertEqual(str(e.exception), "offset must be positive")
