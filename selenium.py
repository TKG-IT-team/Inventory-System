from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# For test account
user_name = "SANDBOX.43722dfaf0a24acbb0cf"
password = "856a2e675f662ee0"

# If live account
# user_name = "ziwei@thekettlegourmet.com"
# password = "Wrestlin2021"

# open the url retrieved
# pls retrieve the respective driver file path and enter below
# e.g. r"C:\Users\user\Downloads\chromedriver"
driver = webdriver.Chrome(r"enter filepath~\chromedriver")
driver.get('enter auth_url here')

# To key in username and password
# 1. pls selct input box right click inspect
# 2. enter the respective element id naming

element = driver.find_element_by_id("userNameInput")
element.send_keys(user_name)
element = driver.find_element_by_id("passwordInput")
element.send_keys(password)
element.send_keys(Keys.RETURN) # press enter
# If enter button does not work then need to click the button
# for locating elements pls refer the the guide: https://selenium-python.readthedocs.io/locating-elements.html
# consider using id rather than css selector (id is unique)
# button = driver.find_element_by_css_selector('paste the CSS selector here')
# button.click()


# click confirm authorisation
button = driver.find_element_by_css_selector('paste the CSS selector here')
button.click()

# Retrieve url
auth_access_token = driver.current_url
# print (auth_access_token)

# store retrieved key and close browser
driver.close()

