import tempfile
import shutil
import os
import uuid
import pathlib

from yandex_images import YandexImages
from keywords_extractor import KeywordsExtractor
from text_on_image import TextOnImage
from keywords_db import KeywordsDB


class MyApp():

    def __init__(self, width, height):
        self.ya_images = YandexImages(width, height)
        self.text_on_image = TextOnImage(width)
        self.keywords_ext = KeywordsExtractor()
        self.keywords_db = KeywordsDB()
        self.temp_img_dir = pathlib.Path("./static/tmp_imgs/")
        self.img_sources = None

        self.temp_img_dir.mkdir(exist_ok=True)

    def __del__(self):
        # os.rmdir(self.temp_img_dir)
        shutil.rmtree(self.temp_img_dir, ignore_errors=True)

    def get_images(self, text, img_count):
        keywords = self.keywords_ext.get_keywords(text)
        keywords_count = len(keywords)

        self.keywords_db.add(text.lower(), keywords)

        if img_count > keywords_count:
            t = text.lower()
            if t not in keywords:
                keywords.append(t)
                keywords_count += 1

            images_for_keyword = img_count // keywords_count
            reminder = img_count % keywords_count
        else:
            images_for_keyword = 1
            reminder = 0
            keywords = keywords[:img_count]

        images = []
        for keyword in keywords:
            count = images_for_keyword + int(reminder > 0)
            reminder -= 1

            img_infos = self.ya_images.get_images_by_keyword(keyword, count)
            for img_info in img_infos:
                img_info["image"] = self.text_on_image.draw_text(text, img_info["image"])
            images.extend(img_infos)

        return self.__save_temp_images(images)

    def __save_temp_images(self, images):
        image_sources = []

        for image in images:
            image_name = uuid.uuid4().hex + image["format"]
            save_path = os.path.join(self.temp_img_dir, image_name)

            image["image"].save(save_path)

            image_sources.append(image_name)

        return image_sources
