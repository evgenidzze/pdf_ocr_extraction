import base64
import json
from pathlib import Path
from typing import Union

from reducto import Reducto

from Providers.base import Provider


class ReductoOCR(Provider):
    """Reducto OCR implementation."""

    def _create_client(self):
        return Reducto(api_key=self.api_key)

    async def _create_pdf_url(self, pdf_path: Union[str, Path]):
        path = self.validate_pdf_path(pdf_path)

        upload = self.client.upload(file=path)

        return upload.model_dump()

    async def _parse_pdf_implementation(self, pdf_path: Union[str, Path]):
        upload = await self._create_pdf_url(pdf_path)

        result = self.client.parse.run(
            document_url=upload,
            experimental_options={'return_figure_images': True})

        return result.model_dump()

    async def _save_text_and_img(self, result, doc_dir):
        result = result['result']
        pages = result['chunks']
        for page_num, page in enumerate(pages, 1):
            text = page['content']
            with open(f"{doc_dir}/page_{page_num}", "w", encoding="utf-8") as f:
                f.write(text)
        # for page_num, page in enumerate(pages, 1):
        #     # Save text
        #     text = page['markdown']
        #     with open(f"{doc_dir}/page_{page_num}", "w", encoding="utf-8") as f:
        #         f.write(text)
        #     # Save images
        #     image_bytes_list: list = page.get('images', [])
        #     for i, img_byte in enumerate(image_bytes_list):
        #         image_base64 = img_byte['image_base64']
        #
        #         if image_base64.startswith("data:image/jpeg;base64,"):
        #             image_base64 = image_base64.split(",", 1)[1]
        #
        #         image_data = base64.b64decode(image_base64)
        #         image_path = doc_dir / f"page_{page['index']}_im_{i}.jpeg"
        #         with open(image_path, 'wb') as f:
        #             f.write(image_data)