from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time 

# Login details for Redmart
email = "czy199162@gmail.com"
password = "Wrestlin2021"

PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"

# pls retrieve the respective webdriver file path and enter below
driver = webdriver.Chrome(PATH)

# Enter Redmart login page URL 
driver.get('https://partners.redmart.com/login/index')

# To key in username and password
# 1. pls selct input box right click inspect
# 2. enter the respective element id naming
# email_element = driver.find_element(By.CSS_SELECTOR, "input[id='account']")
# email_element.send_keys(email)

# password_element = driver.find_element(By.CSS_SELECTOR,"input[id='password']")
# password_element.send_keys(password)
    
try: 
    time.sleep(5)
    # Locate web element
    email_element = driver.find_element(By.CSS_SELECTOR, "input[id='account']")
    email_element.send_keys(email)
    
    
    password_element = driver.find_element(By.CSS_SELECTOR,"input[id='password']")
    password_element.send_keys(password)
    #element = driver.find_element(By.XPATH, "//input[contains(@id, 'account')]")
    time.sleep(5)
    
    password_element.send_keys(Keys.RETURN) #press Enter
    
except NoSuchElementException:
    print ("Unable to locate element")

# If enter button does not work then need to click the button
# button = driver.find_element_by_css_selector('paste the CSS selector here')
# button.click()
# for locating elements pls refer the the guide: https://selenium-python.readthedocs.io/locating-elements.html


# click confirm authorisation
# button = driver.find_element_by_css_selector('paste the CSS selector here')
# button.click()

# to: month year element
# <div class="mighty-picker__month-name ng-binding" ng-bind="month.name">July 2022</div>
# to: date element
# <div class="mighty-picker-calendar__day-wrapper" bo-text="day.date.date()">14</div>    
    
    
    
# close driver
# driver.close()




