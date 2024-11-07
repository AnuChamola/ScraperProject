from operator import truediv
from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import os
import wget
import time
import pandas as pd

#name the user agent
my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
#create chrome options
chrome_options = Options()

# Set the custom User-Agent
chrome_options.add_argument(f"--user-agent={my_user_agent}")
#Set the chromdriver service
s = Service(executable_path='D:/PythonProjects/Scraper/chromedriver2_win32/chromedriver.exe')
#create the webdriver with our chrome driver and our options
driver = webdriver.Chrome(service = s, options=chrome_options)
#Open the amazon site to scrape
driver.get('https://www.amazon.in/s?rh=n%3A6612025031&fs=true&ref=lp_6612025031_sar')
#create a list of links to store our fetched links
listOfLinks = []
condition = True

#we loop until the condition is set to false
while condition:
    #we put this in try and catch to keep the loop going even if we encounter an error rrlated to xpath
    try:
        #fetch the a tag element with xpath
        productInfoList = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@data-cy='title-recipe']//h2/a")))
        #append the fetched links of the page in the link array
        for links in productInfoList:
            listOfLinks.append(links.get_property('href'))
        #we put this in try and except, so that we can break out of the loop when we no longer get the next button element
        try:
            #get the next button element
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@aria-label, 'Go to next')]")))
            #click the button
            driver.execute_script("arguments[0].click();", next_button)
            #sleep/suspend the execution for random intervals, to delay the request
            time.sleep(randint(1, 3))
        except:
            condition = False
    except:
        print("Link fetch error")
#list for all the product details
allDetails = []
#loop through the list of links. tqdm gives us a progress bar to know how many elements are left
for i in tqdm(listOfLinks):
    #we put this in try and except, to ignore any link issues or xpath issues
    try:
        #open the links
        driver.get(i)
        #we put product name and product links in its own try and except so that we skip the current loop iteration, as there 
        #is no point in adding a product without these two inpformation
        try:
            product_name = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='productTitle']")))
            product_price = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='apex_offerDisplay_desktop']//span[@class='a-price-whole']")))
        except:
            print("No Product name or price")
            continue
           
        product_rating = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='averageCustomerReviews_feature_div']//span[@id='acrCustomerReviewText']")))
        product_seller = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH, " //div[@id='buybox']//div[@class='tabular-buybox-text']//a[@id='sellerProfileTriggerId']")))
        #create a dictionary with product details
        tempj = {'product name':product_name.text,
        "price":  product_price.text,
        "product rating": product_rating.text,
        "product seller": product_seller.text
        }
        #add the dictionary to the allDetails array
        allDetails.append(tempj)
        #sleep the execution for a random time to delay the request
        time.sleep(randint(1, 3))
    except:
        print("Site or xpath error")
#create a dataframe with the allDetails array       
df = pd.DataFrame(allDetails)
#save the product details in the allDetails array in details.csv
df.to_csv("details.csv")
#delay the execution to prevent closing, incase if the program stops midway, we can check which product page cause the issue, and 
#investigate for xpath or link errors
time.sleep(10)
#close the chromdriver
driver.quit()
