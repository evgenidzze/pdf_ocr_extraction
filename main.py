import logging
import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio
from typing import Union

from Providers.base import Provider
from Providers.mistral_provider import MistralOCR
from Providers.reducto_provider import ReductoOCR

load_dotenv()
MISTRAL_API_KEY = os.getenv('API_KEY_MISTRAL')
API_KEY_REDUCTO = os.getenv('API_KEY_REDUCTO')


async def main():

    input_folder = 'sample_files'
    output_folder = 'output'
    provider_choice = input("Choose OCR provider (1 for Mistral, 2 for Reducto): ")

    # Create provider based on user choice
    if provider_choice == "1":
        provider = MistralOCR(api_key=MISTRAL_API_KEY)
    elif provider_choice == "2":
        provider = ReductoOCR(api_key=API_KEY_REDUCTO)
    else:
        logging.info("Invalid choice. Using Mistral OCR as default.")
        provider = MistralOCR(api_key=MISTRAL_API_KEY)

    # Process folder
    await provider.process_folder(input_folder, output_folder)
    logging.info(f"Processing complete. Results saved to {output_folder}")


if __name__ == "__main__":
    asyncio.run(main())
