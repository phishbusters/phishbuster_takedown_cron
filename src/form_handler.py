from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pdf_to_image import convert_pdf_to_jpg

import time
import os

def complete_impersonation_form(form_url, profile_id, company_name, path_to_pdf):
    print('Starting selenium process')
    driver = webdriver.Chrome()
    driver.get(form_url)
    wait = WebDriverWait(driver, 10)

    # Wait until page load
    element_present = EC.presence_of_element_located((By.XPATH, "//span[text()='What issue are you having?']/ancestor::div[@role='group']/descendant::select"))
    wait.until(element_present)

    # "What issue are you having?"
    select_issue = Select(driver.find_element(By.XPATH,
        "//span[text()='What issue are you having?']/ancestor::div[@role='group']/descendant::select"))
    select_issue.select_by_visible_text(
        "I'd like to report impersonation on Twitter")

    # "Please tell us more"
    select_more = Select(driver.find_element(By.XPATH,
        "//span[text()='Please tell us more']/ancestor::div[@role='group']/descendant::select"))
    select_more.select_by_visible_text("An account is pretending to be me")

    # "Your email address"
    wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Your email address']/following::input[@type='email']")))
    email_field = driver.find_element(By.XPATH,
        "//span[text()='Your email address']/following::input[@type='email']")
    
    email_field.send_keys("phishbusters@example.com")

    # An account is pretending to be me (RADIO)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='radio'][@value='Account']")))
    radio_button = driver.find_element(By.XPATH, "//input[@type='radio'][@value='Account']")
    radio_button.click()

    # "Username of the account you are reporting"
    wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Username of the account you are reporting']/following::input")))
    username_field = driver.find_element(By.XPATH, "//span[text()='Username of the account you are reporting']/following::input")
    username_field.send_keys("@" + profile_id)

    # The account is using multiple elements of my identity (name)...
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='radio'][@value='Self']")))
    pretending_radio_button = driver.find_element(By.XPATH, "//input[@type='radio'][@value='Self']")
    pretending_radio_button.click()

    # Description
    description_textarea = driver.find_element(By.XPATH,
        "//span[text()='Description of problem']/following::textarea[@name='DescriptionText']")
    description_text = "We are a company specializing in detecting impersonation on Twitter. We are representing our client and have attached the necessary documentation to perform this action."
    description_textarea.send_keys(description_text)
    driver.execute_script('document.getElementById("file-upload").removeAttribute("hidden");')

    # "Confirm your identity file upload"
    upload_field = driver.find_element(By.ID, 'file-upload')
    # Due to Twitter removing PDF, we need to parse the file into JPG
    image_path = convert_pdf_to_jpg(path_to_pdf, '/images')
    absolute_pdf_path = os.path.abspath(image_path)
    upload_field.send_keys(absolute_pdf_path)

    # submit
    print('Submitting form')
    submit_button = driver.find_element(By.XPATH, "//button[text()='Submit']")
    submit_button.click()

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h2[text()='Thank you!']"))
        )

        print("Sent successfully to Twitter, profile:", profile_id)
        driver.quit()
        return True
    except TimeoutError:
        driver.quit()
        print("Timeout error, profile:", profile_id)
        return False
    
    # time.sleep(15)

# if __name__ == "__main__":
#     complete_impersonation_form('https://help.twitter.com/en/forms/authenticity/impersonation', 'profile_id', 'company_name', 'path_to_a_pdf')