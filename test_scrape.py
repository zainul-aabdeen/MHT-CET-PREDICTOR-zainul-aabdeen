import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def test():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    college_name = "Government College of Engineering, Amravati"
    query = f'"{college_name}" placement statistics highest average package site:edu.in OR site:ac.in OR google summary'
    url = "https://www.google.com/search?q=" + query.replace(" ", "+")
    
    driver.get(url)
    time.sleep(3)
    
    context = ""
    try:
        body = driver.find_element(By.TAG_NAME, "body").text
        context = body[:5000]
    except Exception as e:
        print("Error finding body:", e)
        
    print("CONTEXT EXTRACTED:")
    print("------------------")
    print(context if context else "CONTEXT IS EMPTY!")
    
    driver.quit()

if __name__ == "__main__":
    test()
