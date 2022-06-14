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
driver = webdriver.Chrome(r"C:\Users\user\Downloads\chromedriver")
driver.get('https://partner.test-stable.shopeemobile.com/api/v2/shop/auth_partner?partner_id=1007820&timestamp=1655088262&sign=d4aa63bc6084d8e78e84081cc52ff624cfddf412bcd993381e37af4e9266270d&redirect=https://www.google.com/')

# To key in username and password
# 1. pls selct input box right click inspect
# 2. enter the respective element id naming

# <div class="shopee-input__inner shopee-input__inner--normal"><!----> <input type="text" placeholder="Email / Phone / Username" resize="vertical" rows="2" minrows="2" autocomplete="off" restrictiontype="input" class="shopee-input__input"> <!----></div>
# <input type="text" placeholder="Email / Phone / Username" resize="vertical" rows="2" minrows="2" autocomplete="off" restrictiontype="input" class="shopee-input__input">
# //div[contains(@class,'password-group')]//following::div//input[@type='phone']

element = driver.find_element_by_xpath("//input[contains(@placeholder = 'Email / Phone / Username')]")
element.send_keys(user_name)
# element = driver.find_element_by_id("passwordInput")
# element.send_keys(password)
# element.send_keys(Keys.RETURN) # press enter
# If enter button does not work then need to click the button
# for locating elements pls refer the the guide: https://selenium-python.readthedocs.io/locating-elements.html
# consider using id rather than css selector (id is unique)
# button = driver.find_element_by_css_selector('paste the CSS selector here')
# button.click()


# click confirm authorisation
# button = driver.find_element_by_css_selector('paste the CSS selector here')
# button.click()

# Retrieve url
auth_access_token = driver.current_url
# print (auth_access_token)

# store retrieved key and close browser
driver.close()

