from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# LinkedIn credentials
EMAIL = "your_email"
PASSWORD = "your_password"
JOB_SEARCH_URL = "https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&location=India"

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 1️⃣ Login
driver.get("https://www.linkedin.com/login")
time.sleep(2)
driver.find_element(By.ID, "username").send_keys(EMAIL)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
driver.find_element(By.XPATH, '//button[@type="submit"]').click()
time.sleep(3)

# 2️⃣ Go to Job Search Page
driver.get(JOB_SEARCH_URL)
time.sleep(3)

# 3️⃣ Loop through jobs on the page
jobs = driver.find_elements(By.CLASS_NAME, "job-card-list__title")

for job in jobs[:5]:  # Apply to first 5 jobs for testing
    job.click()
    time.sleep(2)

    try:
        apply_button = driver.find_element(By.CSS_SELECTOR, "button.jobs-apply-button")
        apply_button.click()
        time.sleep(2)

        # Optional: Fill application form if required (example: phone number)
        phone_input = driver.find_element(By.CSS_SELECTOR, "input[name='phoneNumber']")
        phone_input.clear()
        phone_input.send_keys("9999999999")

        # Click Next / Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
        submit_button.click()
        time.sleep(2)

        print("Applied to:", job.text)
    except:
        print("Skipped (easy apply not available):", job.text)

time.sleep(5)
driver.quit()