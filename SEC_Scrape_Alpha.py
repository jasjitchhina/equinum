import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_sec_filings(ticker):
    # Set up Selenium with ChromeDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # Enable headless mode

    # Specify download directory (optional)
    # options.add_experimental_option("prefs", {"download.default_directory": "/path/to/download/directory"})
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.sec.gov/edgar/search/")

    try:
        # Click on the 'more search options' link
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "show-full-search-form"))
        ).click()

        # Wait for the full search form to be visible
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "entity-full-form"))
        )

        # Enter the ticker in the search box
        search_box = driver.find_element(By.ID, "entity-full-form")
        search_box.send_keys(ticker)
        time.sleep(1)  # Wait for 1 second before submitting the form
        search_box.send_keys(Keys.RETURN)

        # Wait for the search results to load
        time.sleep(3)

        # Find the first 10-K link
        first_ten_k_link = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.preview-file[data-file-name$='htm']"))
        )

        # Click on the link to open the preview
        first_ten_k_link.click()

        # Wait for the iframe to load and extract the 'src' attribute
        iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "ipreviewer"))
        )
        document_url = iframe.get_attribute('src')

        # Navigate to the document URL
        driver.get(document_url)

        # Wait for the document to load and get its content
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        document_content = driver.find_element(By.TAG_NAME, "body").text

        # Save the content to a .txt file
        file_name = f"{ticker}_10K.txt"
        with open(file_name, "w") as file:
            file.write(document_content)

        return file_name, document_url

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_sec_filings('AAPL')  # Replace 'AAPL' with the ticker symbol you want to scrape