import os
from urllib.parse import urlparse

import httpx
import json
from bs4 import BeautifulSoup


IMG_FORMAT_TO_MAGIC_BYTES = {
    ".jpeg": b"\xFF\xD8\xFF\xE0",
    ".jpg": b"\xFF\xD8\xFF\xE0",
    ".png": b"\x89\x50\x4E\x47",
    ".bmp": b"\x42\x4D",
}

BASE_URI = "https://yandex.ru/images/search"

REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
}


class FuckinCaptchaError(Exception):
    """Raised when fuckin captcha pops up

    Attributes:
        html_captcha -- html page with captcha
    """

    def __init__(self, html_captcha):
        self.html_captcha = html_captcha


class YandexImages():

    def __init__(self, width, height):
        self.http_client = httpx.AsyncClient(timeout=5.0)
        self.query_params = self.__init_query_params(width, height)

    async def get_images_by_keyword(self, keyword, img_count):
        self.query_params["text"] = keyword

        img_uris = await self.__get_image_uris_from_page()
        print(f'img_uris: {len(img_uris)}')
        image_infos = await self.__get_images_from_uris(img_uris, img_count)
        print(f'image_infos: {len(image_infos)}')

        return image_infos

    async def __get_image_uris_from_page(self):
        page_response = await self.http_client.get(BASE_URI, params=self.query_params)
        soup = self.__get_soup_or_get_fucked(page_response)

        tag_sepr_item = soup.find_all("div", class_="serp-item")
        serp_items = [
            json.loads(item.attrs["data-bem"])["serp-item"]
            for item in tag_sepr_item
        ]

        img_hrefs = [key["img_href"] for key in serp_items]

        return img_hrefs

    async def __get_images_from_uris(self, img_uris, img_count):
        image_infos = []

        for img_uri in img_uris:
            if len(image_infos) >= img_count:
                break

            img_format = self.__get_img_format(img_uri)
            if not img_format:
                continue

            try:
                img = (await self.http_client.get(img_uri, headers=REQUEST_HEADER)).content
            except (httpx._exceptions.ReadTimeout, httpx._exceptions.ConnectError):
                continue
            if self.__validate_image_format(img, img_format) == False:
                continue

            print(f"URI {img_uri}")

            img_info = {
                "format": img_format,
                "image": img
            }

            image_infos.append(img_info)

        return image_infos

    @staticmethod
    def __get_img_format(img_uri):
        path = urlparse(img_uri).path
        ext = os.path.splitext(path)[1]

        print(f'__get_img_format() img_uri: {img_uri}')
        print(f'__get_img_format() path: {path}')
        print(f"__get_img_format: {ext}")

        if ext in IMG_FORMAT_TO_MAGIC_BYTES:
            return ext

        return None

    @staticmethod
    def __validate_image_format(image, img_format):
        print(f"img_format: {img_format} lower: {img_format.lower()}")
        magic_bytes = IMG_FORMAT_TO_MAGIC_BYTES[img_format.lower()]

        return image[:len(magic_bytes)] == magic_bytes

    @staticmethod
    def __get_soup_or_get_fucked(page_response):
        soup = BeautifulSoup(page_response.text, "lxml")

        if soup.find("div", class_="captcha__image"):
            raise FuckinCaptchaError(page_response.content)

        return soup

    @staticmethod
    def __init_query_params(width, height):
        params = {
            # "nomisspell": 1,
            "text": None,
            "isize": "eq",
            "iw": width,
            "ih": height,
        }

        return params
