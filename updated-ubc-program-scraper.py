import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_ubc_programs(output_csv="ubc_programs2.csv"):
    # Set up Selenium WebDriver with Chrome in normal mode
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment if you want headless mode
    
    print("Initializing WebDriver...")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), 
        options=options
    )
    
    try:
        url = "https://you.ubc.ca/programs"
        print(f"Navigating to {url}...")
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        # Adjust the CSS selector based on your observation of the page
        dropdown_selector = "#ProgramLanding > div > div > ul > li > i"
        print("Waiting for dropdown elements to load...")
        dropdowns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, dropdown_selector)))
        print(f"Found {len(dropdowns)} dropdown elements.")

        # Open the CSV file for writing
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Program Name", "Campus", "Duration (years), Description"])

            # Iterate over each dropdown
            for index in range(len(dropdowns)):
                # Because the DOM might change when you click dropdowns,
                # refetch the list of dropdowns each time.
                dropdowns = driver.find_elements(By.CSS_SELECTOR, dropdown_selector)
                dropdown = dropdowns[index]
                print(f"Clicking dropdown {index + 1}...")
                driver.execute_script("arguments[0].click();", dropdown)
                time.sleep(2)  # Wait for animation/expansion

                print("Scrolling to the bottom of the page...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for the page to load additional content

                # Now locate program cards within the current section
                section_container_selector = f"#ProgramLanding > div > div > ul > li.topic-section-control.match.expanded.list-view > div > ul > li > ul > li"  
                try:
                    programs = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, section_container_selector))
                    )
                    print(f"Found {len(programs)} program(s) under dropdown {index + 1}")
                    for prog in programs:
                        try:
                            program_name = prog.find_element(By.CSS_SELECTOR, ".program-name a").text
                            program_campus = prog.find_element(By.CSS_SELECTOR, ".program-campuses li").text
                            program_duration = prog.find_element(By.CSS_SELECTOR, ".program-duration").text.split()[0]

                            program_dropdown = prog.find_element(By.CSS_SELECTOR, ".program-section-state")
                            driver.execute_script("arguments[0].click();", program_dropdown)
                            time.sleep(1)  # Wait for the description to load

                            description_selector = ".program-section-control.expanded > div.program-summary > div.program-summary-inner > p"
                            program_description = prog.find_element(By.CSS_SELECTOR, description_selector).text

                            # Print the HTML of the program element
                            print(f"Program Name: {program_name}")
                            print(f"Program Campus: {program_campus}")
                            print(f"Program Duration: {program_duration} years")
                            print(f"Program Description: {program_description}")
                            print("\n")

                            # Write the program details to the CSV file
                            writer.writerow([program_name, program_campus, program_duration, program_description])
                        except Exception as e:
                            print(f"Error extracting program details: {e}")
                except Exception as e:
                    print(f"No programs found under dropdown {index + 1}: {e}")

    finally:
        print("Quitting WebDriver...")
        driver.quit()

if __name__ == "__main__":
    scrape_ubc_programs("ubc_programs2.csv")