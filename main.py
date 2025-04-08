import logging
import os
from dotenv import load_dotenv
import asyncio
from Providers.mistral_provider import MistralOCR
from Providers.reducto_provider import ReductoOCR

load_dotenv()
MISTRAL_API_KEY = os.getenv('API_KEY_MISTRAL')
API_KEY_REDUCTO = os.getenv('API_KEY_REDUCTO')
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


async def main():
    """
    Main entry point for the OCR processing script.

    This function:
    - Prompts the user to select an OCR provider (Mistral or Reducto),
    - Initializes the selected provider with the corresponding API key,
    - Processes all PDF files in the input folder,
    - Saves the OCR results to the output folder.
    """
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
