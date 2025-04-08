import base64
import logging
from pathlib import Path
from typing import Union
from mistralai import Mistral
from Providers.base import Provider, RecognizedDocument


class MistralOCR(Provider):
    """
    Mistral OCR implementation.
    8sec - 34 text pages
    4.5sec - 13 text pages with 4 (parsed) images
    """

    def _create_client(self):
        return Mistral(api_key=self.api_key)

    async def _create_pdf_url(self, pdf_path: Union[str, Path]):
        path = self.validate_pdf_path(pdf_path)
        with open(path, "rb") as file:
            file_content = file.read()

        uploaded_pdf = self.client.files.upload(
            file={
                "file_name": str(path),
                "content": file_content,
            },
            purpose="ocr"
        )

        document_url = self.client.files.get_signed_url(file_id=uploaded_pdf.id)
        logging.info('PDF URL CREATED')
        return document_url.url

    async def _parse_pdf_implementation(self, pdf_path: Union[str, Path]) -> RecognizedDocument:
        document_url = await self._create_pdf_url(pdf_path)

        ocr_response = self.client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": document_url,
            },
            include_image_base64=True
        ).model_dump()
        text = ""
        images: dict[str, bytes] = {}

        for page in ocr_response['pages']:
            page_num = page['index']
            text += page.get('markdown')

            for i, img in enumerate(page.get('images')):
                base64_data = img.get('image_base64', '')
                if base64_data.startswith("data:image/jpeg;base64,"):
                    base64_data = base64_data.split(",", 1)[1]
                image_bytes = base64.b64decode(base64_data)
                image_name = f"page_{page_num + 1}_im_{i + 1}.jpeg"
                images[image_name] = image_bytes
        print(text)
        return RecognizedDocument(
            text=text,
            image_bytes_by_name=images,
        )
