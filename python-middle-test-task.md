## Overview
Investigate and write a PDF text extraction processor. For the purpose of the task - limited to computer-generated PDFs only. The PDF samples attached below.

Compare different methods available in market, making quality of the result the highest priority (but also noticing the price, etc.).
Hint: this industry is evolving rapidly, the best method in April 2025 might be completely different from April 2024. Therefore, there is no single correct answer - much more important is your story and evaluation of the methods tried, and readiness of the code for future changes.

## OCR Requirements:
- Output format should be a text string, with all page texts combined. 
- Specific format of this string - up to you. Ideally, it should be able to highlight formatting (headers, bold, etc) and tables of the original file.
- Method should be able to parse two-column PDF layouts.
- Saving images not available for text parsing (e.g., charts or photos) is a nice-to-have feature.
- Performance requirement: it should process a 20-page PDF not longer than 1 minute. 

## Code requirements: 
- The solution should be extensible. If some company releases a better OCR solution - we should be able to plug it in without changing the rest of the code.
- Utilization of modern Python (3.13+) is highly recommended.
- No need to make the production production-perfect (e.g., cover 100% with tests). Instead, write a separate todo list with items you would do if you had more time.

## Code skeleton:
```
from dataclasses import dataclass
from pathlib import Path


@dataclass  # can be pydantic
class RecognizedDocument:
    text: str
    image_bytes_by_name: dict[str, bytes]
    # Feel free to add more attrs you consider important


class PdfRecognizer:  # Feel free to add more classes and change inheritance
    """
    Main OCR class
    """
    async def recognize(self, pdf_bytes: bytes) -> RecognizedDocument:
        raise NotImplementedError


def recognize_pdf_bytes_with_ocr(pdf_bytes: bytes) -> RecognizedDocument:
    """Convenience method to call PdfRecognizer for specific PDF bytes"""
    raise NotImplementedError


def recognize_pdf_file_with_ocr(pdf_path: Path | str) -> RecognizedDocument:
    """Convenience method to call PdfRecognizer for specific file in the file system"""
    raise NotImplementedError
```

P.S. If you face a paywall by some promising third-party service which and no trial is available - contact us.
