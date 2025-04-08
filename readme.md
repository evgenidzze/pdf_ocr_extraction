# OCR Provider Project

This project allows you to run Optical Character Recognition (OCR) on PDF files using two different OCR providers: **Reducto** and **Mistral**. Easy integrating new providers. The results of OCR processing, including text and images, are saved in an `/output` folder for each processed file.

## Features

- **Reducto OCR**: More accurate, but slower, collects better images and text.
  - **Performance**: 18 seconds for 34 text pages, 19.5 seconds for 13 text pages with 19 parsed images.
  - Reducto allows up to **15,000 pages per month for 300$. [Pricing](https://reducto.ai/pricing)**
  
- **Mistral OCR**: Faster and cheaper, but less accurate compared to Reducto.
  - **Performance**: 8 seconds for 34 text pages, 4.5 seconds for 13 text pages with 4 parsed images.
  - **Pricing**: $1 per 1,000 pages (or $0.001 per page). Very affordable and competitive pricing.
  - Documents must be no larger than 50 MB and should not exceed 1,000 pages.
  
**Output**: All OCR results, including text and images, will be saved in the `output` folder.

### Documentation:
- [Reducto OCR Documentation](https://docs.reducto.ai/overview)
- [Mistral OCR Documentation](https://docs.mistral.ai/capabilities/document/#ocr-with-pdf)

## Installation

### Step 1: Clone the repository
First, clone this repository to your local machine:
```bash
git clone https://github.com/evgenidzze/pdf_ocr_extraction
cd pdf_ocr_extraction
```

### Step 2: Create a Virtual Environment
Make sure you have Python 3.7+ installed. Then, create a virtual environment for the project:

```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment
To activate the virtual environment, run the following command depending on your operating system:

#### On Windows:
```bash
venv\Scripts\activate
```

#### On macOS and Linux:
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
Install all the necessary dependencies using `pip`:

```bash
pip install -r requirements.txt
```


### Step 5: Set Up API Keys
Create a `.env` file in the root directory of the project and add the following lines:

```
API_KEY_MISTRAL=<your_mistral_api_key>
API_KEY_REDUCTO=<your_reducto_api_key>
```

You can obtain API keys from the official websites of **Mistral** and **Reducto**:
- [Mistral OCR API](https://console.mistral.ai/api-keys)
- [Reducto OCR API](https://app.reducto.ai/)

### Step 6: Running the Project
To start the OCR process, simply run the script:

```bash
python3 main.py
```

You will be prompted to choose an OCR provider:
- **1** for **Mistral** OCR
- **2** for **Reducto** OCR

The project will then process all the PDF files located in the `sample_files` folder and save the results in the `output` folder.

### Results
The output folder will contain:
- A `.txt` file with the extracted text from the PDF.
- Image files (JPEG) with parsed images from the document.
- A `metadata.json` file containing additional metadata from the OCR process.
