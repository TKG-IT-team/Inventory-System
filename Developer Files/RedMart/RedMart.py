from selenium import webdriver

PATH = "C:\Program Files (x86)\chromedriver_win32\chromedriver.exe"

driver = webdriver.Chrome(PATH)

driver.get("https://google.com")