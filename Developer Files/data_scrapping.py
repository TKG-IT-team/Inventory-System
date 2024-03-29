from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Login details for Redmart
email = "czy199162@gmail.com"
password = "Wrestlin2021"

# pls retrieve the respective webdriver file path and enter below
driver = webdriver.Edge(r"C:\Users\Kaiwei\Desktop\TKG Inventory\webDriver\edgedriver_win64\msedgedriver.exe")
#driver = webdriver.Chrome(r"C:\Users\user\Downloads\chromedriver")

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
    # Locate web element
    email_element = driver.find_element(By.CSS_SELECTOR, "input[id='account']")
    email_element.send_keys(email)
    
    password_element = driver.find_element(By.CSS_SELECTOR,"input[id='password']")
    password_element.send_keys(password)
    #element = driver.find_element(By.XPATH, "//input[contains(@id, 'account')]")
    
    password_element.send_keys(Keys.RETURN) #press Enter
    
except NoSuchElementException:
    print ("Unable to locate element")


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

