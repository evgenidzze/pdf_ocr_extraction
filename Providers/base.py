import base64
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from typing import Any, Union, Dict


@dataclass
class RecognizedDocument:
    text: str
    image_bytes_by_name: dict[str, bytes] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class Provider:
    """Base OCR provider class with common functionality."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = self._create_client()
        self.provider_name = self.__class__.__name__.lower().replace("ocr", "")

    def _create_client(self):
        """Create and return client instance."""
        raise NotImplementedError

    async def _create_pdf_url(self, pdf_path: Union[str, Path]):
        """Upload PDF and return a URL or object for processing."""
        raise NotImplementedError

    async def parse_pdf(self, pdf_path: Union[str, Path]):
        """Run OCR parsing on the PDF file."""
        try:
            pdf_path = self.validate_pdf_path(pdf_path)
            return await self._parse_pdf_implementation(pdf_path)
        except Exception as e:
            logging.info(f"Error processing {pdf_path} with {self.__class__.__name__}: {str(e)}")
            return None

    async def _parse_pdf_implementation(self, pdf_path: Path):
        """Implementation of parse_run to be overridden by child classes."""
        raise NotImplementedError

    @staticmethod
    def validate_pdf_path(pdf_path: Union[str, Path]) -> Path:
        """Validate that the PDF path exists and is a file."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        return path

    async def process_folder(self, folder_path: Union[str, Path], output_dir: Union[str, Path]):
        """Process all PDF files in a folder and save results."""
        folder_path = Path(folder_path)
        output_dir = Path(output_dir)

        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Get all PDF files in the folder
        pdf_files = list(folder_path.glob("*.pdf"))
        if not pdf_files:
            logging.info(f"No PDF files found in {folder_path}")
            return

        logging.info(f"Found {len(pdf_files)} PDF files in {folder_path}")

        for pdf_file in pdf_files:
            try:
                logging.info(f"Processing {pdf_file.name} with {self.__class__.__name__}...")
                result = await self.parse_pdf(pdf_file)
                if result:
                    await self.save_results(result, pdf_file.stem, output_dir)
                    logging.info(f"Successfully processed {pdf_file.name}")
                else:
                    logging.info(f"Failed to process {pdf_file.name}")
            except Exception as e:
                logging.info(f"Error processing {pdf_file.name}: {str(e)}")

    async def save_results(self, result: Dict[str, Any], pdf_name: str, output_dir: Path):
        """Save OCR results to the output directory."""

        # Create provider-specific subdirectory
        provider_dir = output_dir / self.provider_name
        provider_dir.mkdir(exist_ok=True)

        # Create document-specific subdirectory
        doc_dir = provider_dir / pdf_name
        doc_dir.mkdir(exist_ok=True)

        await self._save_text_and_img(result, doc_dir)

    def _save_text_and_img(self, result, doc_dir):
        raise NotImplementedError

