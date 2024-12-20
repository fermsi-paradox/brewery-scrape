from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from pathlib import Path

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode (no GUI)
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the driver with options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
url = " " #INSERT WEBPAGE HERE

try:
    print("Loading page...")
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    
    # Function to scroll and get current company count
    def scroll_and_count():
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load
        return len(driver.find_elements(By.CLASS_NAME, "company-listing"))
    
    # Keep scrolling until no new companies are loaded
    print("Scrolling to load all breweries...")
    last_count = 0
    while True:
        current_count = scroll_and_count()
        print(f"Found {current_count} breweries so far...")
        if current_count == last_count:  # No new items loaded
            break
        last_count = current_count
    
    companies = driver.find_elements(By.CLASS_NAME, "company-listing")
    print(f"Found total of {len(companies)} companies")
    
    # Create a clean dataset with specific columns
    data = []
    for company in companies:
        try:
            content = company.find_element(By.CLASS_NAME, "company-content")
            brewery_data = {}
            
            # Get each field with error handling
            try:
                brewery_data['name'] = content.find_element(By.CSS_SELECTOR, "h2[itemprop='name']").text
            except: 
                brewery_data['name'] = "N/A"
                
            try:
                brewery_data['address'] = content.find_element(By.CSS_SELECTOR, "[itemprop='streetAddress']").text
            except:
                brewery_data['address'] = "N/A"
                
            try:
                brewery_data['city'] = content.find_element(By.CSS_SELECTOR, "[itemprop='addressLocality']").text
            except:
                brewery_data['city'] = "N/A"
                
            try:
                brewery_data['state'] = content.find_element(By.CSS_SELECTOR, "[itemprop='addressRegion']").text
            except:
                brewery_data['state'] = "N/A"
                
            try:
                brewery_data['phone'] = content.find_element(By.CSS_SELECTOR, "[itemprop='telephone']").text
            except:
                brewery_data['phone'] = "N/A"
            
            print(f"Found brewery: {brewery_data['name']}")
            data.append(brewery_data)
            
        except Exception as e:
            print(f"Error processing company: {e}")
            continue
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv('breweries_data.csv', index=False)
    print(f"Saved {len(data)} breweries to breweries_data.csv")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
