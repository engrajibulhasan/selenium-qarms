import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get("file://" + os.path.abspath("index.html"))

time.sleep(1)

driver.find_element(By.ID, "nameInput").send_keys("Rajibul Hasan")
driver.find_element(By.ID, "submitBtn").click()

time.sleep(1)

message = driver.find_element(By.ID, "message").text
assert "Rajibul Hasan" in message

print("✅ Test Passed")

driver.quit()
