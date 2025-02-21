import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_ubc_programs(output_csv="ubc_programs3.csv"):
    # Set up Selenium WebDriver with Chrome in headless mode
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Runs Chrome in headless mode (no GUI)
    
    print("Initializing WebDriver...")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), 
        options=options
    )
    
    try:
        # Go to the UBC Programs page
        url = "https://you.ubc.ca/programs/#mode=by-topic&viewMode=list&categories[]=1284&categories[]=1294&categories[]=1301&categories[]=1293&categories[]=1295&categories[]=1296&categories[]=1297&categories[]=1300&categories[]=1298&categories[]=1299"
        print(f"Navigating to {url}...")
        driver.get(url)

                # Click on the drop-down to load the program items
        dropdown_selector = "#ProgramLanding > div > div > ul > li.topic-section-control.match.expanded.list-view > i"
        try:
            print("Waiting for the drop-down element to be clickable...")
            dropdown = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector))
            )
            print("Clicking the drop-down element to reveal program items...")
            dropdown.click()
            time.sleep(2)  # Allow time for items to load after clicking
        except Exception as e:
            print("Error clicking the drop-down:", e)

        # Wait for the program cards to be present
        print("Waiting for the page to load...")
        # WebDriverWait(driver, 20).until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#ProgramLanding > div > div > ul > li:nth-child(1) > div > ul > li:nth-child(2)"))
        # )

        time.sleep(10)

        # Find all program cards by their container class
        print("Finding program cards...")
        program_cards = driver.find_elements(By.CSS_SELECTOR, "#ProgramLanding > div > div > ul > li:nth-child(1) > div > ul > li:nth-child(2)")  # Use a more general selector
        print(f"Found {len(program_cards)} program cards.")

        for card in program_cards:
            # Print the entire HTML of the program card
            card_html = card.get_attribute('outerHTML')
            print("Program Card HTML:")
            print(card_html)
            print("\n")

        # The rest of your code to extract data and write to CSV can go here

    finally:
        print("Quitting WebDriver...")
        driver.quit()

if __name__ == "__main__":
    scrape_ubc_programs("ubc_programs3.csv")
