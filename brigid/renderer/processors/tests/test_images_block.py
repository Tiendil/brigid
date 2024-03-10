import uuid
from unittest.mock import MagicMock

import pytest
from brigid.renderer.processors.images_block import Image, ImageModel, ImagesBlock, ImagesModel


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


class TestImageModel:

    def test_alt_or_caption(self) -> None:
        with pytest.raises(ValueError):
            ImageModel(src="test.jpg")

        ImageModel(src="test.jpg", alt="alt_1")

        image = ImageModel(src="test.jpg", caption="caption_1")
        assert image.alt == "caption_1"

        ImageModel(src="test.jpg", alt="alt_1", caption="caption_1")


class TestImagesBlock:

    def test_root_css_classes(self) -> None:
        images = ImagesModel(caption="test_caption",
                             images=[Image(src="test.jpg", alt="alt_1"),
                                     Image(src="test2.jpg", alt="alt_2")])

        images_block = ImagesBlock(length=3,
                                   tracker={},
                                   block_mgr=MagicMock(),
                                   config={})

        assert set(images_block.root_css_classes(images)) == {"brigid-images", "brigid-images-2"}

    def test_process_data__images_model(self) -> None:
        images_block = ImagesBlock(length=3,
                                   tracker={},
                                   block_mgr=MagicMock(),
                                   config={})

        images = ImagesModel(caption="test_caption",
                             images=[Image(src="test.jpg", alt="alt_1"),
                                     Image(src="test2.jpg", alt="alt_2")])

        assert images_block.process_data(images.replace()) == images

    def test_process_data__image_model(self) -> None:
        images_block = ImagesBlock(length=3,
                                   tracker={},
                                   block_mgr=MagicMock(),
                                   config={})

        image = ImageModel(src="test.jpg",
                           alt="alt_1",
                           caption="test caption",
                           galery_class='test-galery')

        images = ImagesModel(caption="test caption",
                             galery_class='test-galery',
                             images=[Image(src="test.jpg", alt="alt_1")])

        assert images_block.process_data(image) == images
