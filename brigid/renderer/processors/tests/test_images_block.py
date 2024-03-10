import uuid

import pytest
from brigid.renderer.processors.images_block import Image, ImagesModel


class TestImage:

    def test_escape_alt(self) -> None:
        image = Image(src="test.jpg",
                      alt="complex <p>test</p> bla-bla <<<")

        assert image.alt == "complex test bla-bla <<<"


class TestImagesModel:

    def test_minimum_1_image(self) -> None:
        with pytest.raises(ValueError):
            ImagesModel(caption="test", images=[])

    def test_first_image_alt_from_caption(self) -> None:
        images = ImagesModel(caption="test_caption", images=[Image(src="test.jpg")])
        assert images.images[0].alt == "test_caption"

        images = ImagesModel(caption="test_caption", images=[Image(src="test.jpg"),
                                                             Image(src="test2.jpg", alt="alt_2")])
        assert images.images[0].alt == "test_caption"
        assert images.images[1].alt == "alt_2"

    def test_all_images_must_have_alts(self) -> None:
        with pytest.raises(ValueError):
            ImagesModel(caption="test_caption",
                        images=[Image(src="test.jpg"),
                                Image(src="test2.jpg")])

        ImagesModel(caption="test_caption",
                    images=[Image(src="test.jpg", alt="alt_1"),
                            Image(src="test2.jpg", alt="alt_2")])

    def test_all_images_must_have_alts_besides_the_first_one(self) -> None:
        ImagesModel(caption="test_caption",
                    images=[Image(src="test.jpg"),
                            Image(src="test2.jpg", alt="alt_1")])

    def test_default_galery_class(self) -> None:
        images = ImagesModel(caption="test_caption", images=[Image(src="test.jpg")])
        assert images.galery_class == "brigid-images-1"

        images = ImagesModel(caption="test_caption",
                             images=[Image(src="test.jpg", alt="alt_1"),
                                     Image(src="test2.jpg", alt="alt_2")])
        assert images.galery_class == "brigid-images-2"

    def test_galery_class(self) -> None:
        images = ImagesModel(caption="test_caption", images=[Image(src="test.jpg")],
                             galery_class="test-galery")
        assert images.galery_class == "test-galery"
