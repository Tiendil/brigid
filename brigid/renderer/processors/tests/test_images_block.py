import uuid

import pytest
from brigid.renderer.processors.images_block import Image


class TestImage:

    def test_escape_alt(self) -> None:
        image = Image(src="test.jpg",
                      alt="complex <p>test</p> bla-bla <<<")

        assert image.alt == "complex test bla-bla <<<"
