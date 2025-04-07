import base64
from pathlib import Path
from typing import Union
from mistralai import Mistral

from Providers.base import Provider


class MistralOCR(Provider):
    """Mistral OCR implementation."""

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

        signed_url = self.client.files.get_signed_url(file_id=uploaded_pdf.id)

        return signed_url.url

    async def _parse_pdf_implementation(self, pdf_path: Union[str, Path]):
        document_url = await self._create_pdf_url(pdf_path)

        ocr_response = self.client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": document_url,
            },
            include_image_base64=True
        )

        return ocr_response.model_dump()
