from pathlib import Path
from typing import Union

import aiohttp
from reducto import Reducto

from Providers.base import Provider, RecognizedDocument


class ReductoOCR(Provider):
    """
    Reducto OCR implementation.
    18sec - 34 text pages
    19.5sec - 13 text pages with 19 (parsed) images
    """

    def _create_client(self):
        return Reducto(api_key=self.api_key)

    async def _create_pdf_url(self, pdf_path: Union[str, Path]):
        path = self.validate_pdf_path(pdf_path)
        document_url = self.client.upload(file=path)
        return document_url.model_dump()

    async def _parse_pdf_implementation(self, pdf_path: Union[str, Path]) -> RecognizedDocument:
        document_url = await self._create_pdf_url(pdf_path)

        result = self.client.parse.run(
            document_url=document_url,
            options={'chunking': {'chunk_mode': 'page'}},
            experimental_options={'return_figure_images': True}).model_dump()
        result = result['result']
        pages = result['chunks']
        text = ""
        images: dict[str, bytes] = {}
        for page_num, page in enumerate(pages, 1):
            text += page['content']
            for block_num, block in enumerate(page['blocks']):
                image_url = block.get('image_url')
                if image_url:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                image_name = f"page_{page_num}_im_{block_num + 1}.jpeg"
                                images[image_name] = image_data
        print(text)
        return RecognizedDocument(
            text=text,
            image_bytes_by_name=images,
        )
