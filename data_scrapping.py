
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# For test account
email = "czy199162@gmail.com"
password = "Wrestlin2021"

# open the url retrieved
# pls retrieve the respective driver file path and enter below
driver = webdriver.Chrome(r"C:\Users\user\Downloads\chromedriver")
driver.get('https://www.google.com/')
#driver.get('https://partners.redmart.com/login/index')

# To key in username and password
# 1. pls selct input box right click inspect
# 2. enter the respective element id naming

# //div[contains(@class,'password-group')]//following::div//input[@type='phone']
# element = driver.find_element_by_xpath("//input[contains(@placeholder = 'Email / Phone / Username')]")
# element.send_keys(user_name)
# element = driver.find_element_by_id("passwordInput")
# element.send_keys(password)

#element = driver.find_element_by_id("account")
#element.send_keys(email)

#element = driver.find_element_by_id("password")
#element.send_keys(password)
#element.send_keys(Keys.RETURN) #press Enter

# If enter button does not work then need to click the button
# for locating elements pls refer the the guide: https://selenium-python.readthedocs.io/locating-elements.html
# consider using id rather than css selector (id is unique)
# button = driver.find_element_by_css_selector('paste the CSS selector here')
# button.click()


# click confirm authorisation
# button = driver.find_element_by_css_selector('paste the CSS selector here')
# button.click()

# Retrieve url
#auth_access_token = driver.current_url
#driver.close()

