import os
from dotenv import load_dotenv

from dataclasses import dataclass, field
from pathlib import Path
import asyncio
import base64
from typing import Any, Dict, Optional

import aiohttp

load_dotenv()
API_KEY = os.getenv('API_KEY')


@dataclass
class RecognizedDocument:
    text: str
    image_bytes_by_name: dict[str, bytes] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def save_images(self, output_dir: Path | str) -> Dict[str, Path]:
        """
        Save extracted images to the specified directory.

        Args:
            output_dir: Directory path where images will be saved.

        Returns:
            Dictionary mapping image names to their saved file paths.
        """
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = {}
        for image_name, image_data in self.image_bytes_by_name.items():
            # Create a safe filename from the image name
            safe_name = ''.join(c if c.isalnum() or c in '._- ' else '_' for c in image_name)
            file_path = output_dir / safe_name

            # Save the image to the file
            with open(file_path, 'wb') as f:
                f.write(image_data)

            saved_paths[image_name] = file_path

        return saved_paths


class MistralOCRProvider:
    """
    Implementation using Mistral AI's OCR capabilities for PDF text extraction.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1/document"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def process_document(self, pdf_bytes: bytes) -> RecognizedDocument:
        """
        Process a PDF document using Mistral AI's OCR.
        """
        # Convert PDF bytes to base64
        encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        # Prepare the payload for the Mistral API
        payload = {
            "file": encoded_pdf,
            "format": "pdf",
            "extraction_type": "text",
            "options": {
                "detect_format": True,
                "extract_tables": True,
                "extract_images": True,
                "handle_multi_column": True,
            }
        }

        # Make the API request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Mistral OCR API error: {response.status} - {error_text}")

                result = await response.json()

        # Process the response
        extracted_text = self._process_text_response(result)
        extracted_images = self._process_image_response(result)
        metadata = self._extract_metadata(result)

        return RecognizedDocument(
            text=extracted_text,
            image_bytes_by_name=extracted_images,
            metadata=metadata
        )

    def _process_text_response(self, result: dict) -> str:
        """Process the text part of the Mistral API response."""
        # This is a simplified implementation - in a real-world scenario,
        # you would need to handle the specific format of Mistral's response
        if 'text' in result:
            return result['text']

        # If the response format is different, you might need to process it differently
        # For example, combining text from multiple pages
        combined_text = ""

        if 'pages' in result:
            for page in result['pages']:
                if 'text' in page:
                    combined_text += page['text'] + "\n\n"

                # Process blocks (paragraphs, headers, etc.)
                if 'blocks' in page:
                    for block in page['blocks']:
                        if block.get('type') == 'heading':
                            combined_text += f"# {block.get('text', '')}\n"
                        elif block.get('type') == 'paragraph':
                            combined_text += f"{block.get('text', '')}\n"
                        elif block.get('type') == 'table':
                            combined_text += self._format_table(block) + "\n"

        return combined_text.strip()

    def _format_table(self, table_block: dict) -> str:
        """Format a table block into a string representation."""
        if 'cells' not in table_block:
            return ""

        # This is a simplified implementation
        # In a real implementation, you would need to reconstruct the table structure
        table_text = "TABLE:\n"
        for cell in table_block['cells']:
            row = cell.get('row', 0)
            col = cell.get('col', 0)
            text = cell.get('text', '')
            table_text += f"[{row},{col}]: {text}\n"

        return table_text

    def _process_image_response(self, result: dict) -> Dict[str, bytes]:
        """Process the image part of the Mistral API response."""
        images = {}

        # Example implementation - adjust based on actual API response format
        if 'images' in result:
            for i, img_data in enumerate(result['images']):
                if 'base64' in img_data:
                    image_bytes = base64.b64decode(img_data['base64'])
                    image_name = img_data.get('name', f"image_{i}.png")
                    images[image_name] = image_bytes

        return images

    def _extract_metadata(self, result: dict) -> Dict[str, Any]:
        """Extract metadata from the Mistral API response."""
        metadata = {}

        # Example implementation - adjust based on actual API response format
        if 'metadata' in result:
            metadata = result['metadata']

        return metadata


class PdfRecognizer:
    """
    Main OCR class that orchestrates the text extraction process.
    """

    def __init__(self, provider, api_key: str):
        """
        Initialize the PDF recognizer with a Mistral OCR provider.

        Args:
            api_key: Mistral API key for OCR processing.
        """
        self.provider = provider

    async def recognize(self, pdf_bytes: bytes) -> RecognizedDocument:
        """
        Recognize text in a PDF document using Mistral OCR.

        Args:
            pdf_bytes: The PDF file content as bytes.

        Returns:
            A RecognizedDocument object containing the extracted text and images.
        """
        return await self.provider.process_document(pdf_bytes)


async def recognize_pdf_bytes_with_ocr(
        pdf_bytes: bytes,
        api_key: str,
        save_images_to: Optional[Path | str] = None
) -> RecognizedDocument:
    """
    Convenience method to call PdfRecognizer for specific PDF bytes.

    Args:
        pdf_bytes: The PDF file content as bytes.
        api_key: Mistral API key.

    Returns:
        A RecognizedDocument object containing the extracted text and images.
        :param save_images_to:
    """
    recognizer = PdfRecognizer(provider=MistralOCRProvider, api_key=api_key)
    result = await recognizer.recognize(pdf_bytes)

    # Save images if requested
    if save_images_to is not None:
        result.save_images(save_images_to)

    return result


async def recognize_pdf_file_with_ocr(
        pdf_path: Path | str,
        api_key: str,
        save_images_to: Optional[Path | bool] = None
) -> RecognizedDocument:
    """
    Convenience method to call PdfRecognizer for a specific file in the file system.

    Args:
        pdf_path: Path to the PDF file.
        api_key: Mistral API key.

    Returns:
        A RecognizedDocument object containing the extracted text and images.
    """
    pdf_path = Path(pdf_path) if isinstance(pdf_path, str) else pdf_path
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Determine image save location
    if save_images_to is True:
        # Use the PDF filename to create an images folder
        images_folder = pdf_path.parent / f"{pdf_path.stem}_images"
    else:
        images_folder = save_images_to

    return await recognize_pdf_bytes_with_ocr(pdf_bytes, api_key, images_folder)


# Example usage:
async def main():
    # Replace with your Mistral API key

    # Process a PDF file
    pdf_path = Path("sample_files/1_quarterly_report.pdf")
    result = await recognize_pdf_file_with_ocr(
        pdf_path,
        API_KEY,
        save_images_to=True  # This will create example_images folder
    )
    print(f"Extracted text: {result.text}")
    print(f"Extracted {len(result.image_bytes_by_name)} images")
    print(f"Metadata: {result.metadata}")


if __name__ == "__main__":
    asyncio.run(main())
