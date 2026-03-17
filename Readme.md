# Taobao Product Scraper

A Python-based web scraper that extracts product information from Taobao product listing pages.
The scraper automates login, dynamically scrolls through the page using Playwright, and collects product details in a structured format.

## Features

* Automated Taobao login
* Dynamic page scrolling for lazy-loaded products
* Extraction of product details including:

  * Product ID
  * Product Name
  * Product Image
  * Price
  * Discounted Price
* Structured data storage for further processing

## Performance

* Scraped approximately **300 products**
* Completed in around **15 minutes**

## Tech Stack

* Python
* Playwright

## Usage

Install dependencies:

```bash
pip install playwright
playwright install
```

Run the scraper:

```bash
python scraper.py
```

## Notes

This scraper handles dynamic content loading by automatically scrolling the page to ensure all products are captured.
