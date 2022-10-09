from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys, ActionChains

import pandas as pd
from urllib.parse import urlparse, urljoin
import time
import os, shutil
import re


BASE_PATH = os.path.dirname(os.path.abspath(__name__))

class Scraper(): 
    browser = Chrome()
    """Ecommerce website scraper object"""

    def __init__(self, 
                brand_selector=None, 
                info_selector=None, 
                price_selector=None, 
                link_selector=None, 
                site_name="", 
                next_page_selector=None, 
                url=""): 

        self.url = url
        self.site_name = site_name
        self.next_page_selector = next_page_selector
        self.brand_selector = brand_selector
        self.info_selector = info_selector
        self.price_selector = price_selector
        self.link_selector = link_selector

        self.selector = ""
        self.file_name = ""
        self.items = None

        self.links = set()
        self.browser_wait = WebDriverWait(self.browser, 10)
        

    def load_url(self, url=""):
        url = url or self.url
        self.browser.get(url)

    def get_page(self):     
        try:
            brands_element = self.browser_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.brand_selector)))
            brand_info_element = self.browser_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.info_selector)))
            brand_price_element = self.browser_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.price_selector)))
            link_element = self.browser_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.link_selector)))
            
            
            brand = [brand.text.title() for brand in brands_element]
            info = [info.text.title() for info in brand_info_element]
            price = [price.text for price in brand_price_element]
            link = [link.get_attribute('href') for link in link_element]

            self.items = {
                "product list" : {
                    "brand" : brand, 
                    "brand_info" : info, 
                    "brand_price" : price,
                    "link" : link
                }
            }

            current_url = urlparse(self.browser.current_url)
            self.file_name = "_".join((current_url.path + current_url.query).split("/"))

            data = self.items['product list']

            print("length brand: " + str(len(data['brand'])))
            print("length price: " + str(len(data['brand_price'])))
            print("length link: " + str(len(data['link'])))
            print(f"current url: {self.browser.current_url}")
        except:
            print('***elements not found on this page***')

    def next_page(self, xpath=False):
        """press site next page"""

        """this code is in development phase, need to finalize yet"""
        flag = True
        if xpath:
            while flag: 
                time.sleep(2)
                self.get_page()
                self.save_file()
                try:                    
                    click_element = self.browser_wait.until(EC.presence_of_element_located(((By.XPATH, self.next_page_selector))))
                    click_element.click()                    
                    print("***next page clicked***")                    
                    continue
                except:
                    print("***unlickable***")
                    flag = False                                
        else:            
            while flag: 
                time.sleep(3)
                self.get_page()
                self.save_file()
                try:
                    click_element = self.browser_wait.until(EC.presence_of_element_located(((By.CSS_SELECTOR, self.next_page_selector)))).click()
                    click_element.click()
                    print("***next page clicked***")
                    continue
                except:
                    print("***unlickable***")
                    flag = False                                

    def save_file(self):
        """saves the scraped data from get_page function to .csv"""
        site_name = self.site_name
        save_path = os.path.join(BASE_PATH, f"output/{site_name}/trash")
        
        os.makedirs(save_path, exist_ok=True)

        try:
            item = self.items['product list']
            pd.DataFrame(item).to_csv(os.path.join(save_path, f"{self.file_name}.csv"), index=False)
            
            print("*" * 100)
            print(f"scrapped {self.browser.current_url}")
            print(f"file saved to {os.path.join(save_path, self.file_name)}.csv")
            print("*" * 100)
        except: 
            print("*" * 100)
            print("****dataframe must have the same length****")
            print("****review your css selectors****")
            print("*" * 100)

    
    def close(self):
        """closes the browser driver"""
        last_url = str(self.browser.current_url)
        print(f"*****last scraped url {last_url}*****")
        self.browser.close()


    def press_end(self):

        """press end button"""
        ActionChains(self.browser)\
            .key_down(Keys.END)\
            .perform()
    
    def follow_links(self, path=None, press_end=False):

        """follow and scrape the extracted links from extract links function"""

        if path:
            for url in path:
                self.load_url(url)
                if press_end:
                    for _ in range(10):
                        time.sleep(1)
                        self.press_end()
                
                
                self.get_page()
                self.save_file()
            
        else:            
            for url in self.links:
                self.load_url(url)
                if press_end:
                    for _ in range(10):
                        time.sleep(1)
                        self.press_end()
                
                
                self.get_page()
                self.save_file()

    def extract_link(self, selector=str()):

        """Checks the URL by and extract link elements using selector variable"""

        self.selector = selector
        self.load_url()
        elements = self.browser_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        for link in elements: 
            self.links.add(link.get_attribute('href'))
        
        print(f"Links length: {self.links}")


    def check_each_link(self):

        """Checks the extracted link from 
            extract_link function and then use the self.selector 
            attribute to check all the elements from the exctracted links"""

        in_links = set()
        selector = self.selector
        links = self.links
        for link in links:
            self.load_url(link)
            print(f"checking link --> {self.browser.current_url}")        
            try:
                element_select = self.browser_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                for element in element_select:
                    in_links.add(element.get_attribute('href'))
                    
            except:
                print("****No links****")
        
        for i in in_links:
            self.links.add(i)

        print("Links length: " + str(len(self.links)))

        os.makedirs(os.path.join(BASE_PATH, f"output/{self.site_name}/trash"), exist_ok=True)

        path_to_text = os.path.join(BASE_PATH, f"output/{self.site_name}/trash/{self.site_name}.txt")
        with open(path_to_text, "w") as write:
            write.write(str(self.links))
            print(f"{self.site_name}.txt written..")
            write.close()              

    def extract_more_links(self, iteration=5):
        for _ in range(iteration):
            self.check_each_link()
          



"""A function to clean scraped csv file from Scraper object"""


def concat_all_csv(foldername, filename, brand=False, price_replace=None):
    def cleanpricevalue(x):
        x = x.replace(".", ",").replace(",", "")
        pattern = "\d{1,}\,\d{3,}\.\d{2}|\d{3}\.\d{2}|\d{1,}\,\d{3,}|\d{2,}|\d{2,}\.\d{2}|\d"
        match = re.findall(string=x, pattern=pattern)[-1]
        fprice = match[:-2] + '.' + match[-2:] 
        return float(fprice)

    
    trash_path = os.path.join(BASE_PATH, f"output/{foldername}/trash")
    csv_abspath = [os.path.join(trash_path, file) for file in os.listdir(trash_path)]
    save_to_path = os.path.join(BASE_PATH, f"output/{foldername}/{filename}.csv")

    dataframe = pd.concat([pd.read_csv(file) for file in csv_abspath if file.endswith('.csv')])
    dataframe.dropna(inplace=True)
    dataframe.drop_duplicates(inplace=True)
    if brand:
        dataframe['brand'] = dataframe['brand'].apply(lambda x: x.replace(x, foldername.title()))

    if price_replace:
        dataframe['brand_price'] = dataframe['brand_price'].apply(lambda x: '0' if(x ==price_replace) else x)

    try:   
    #     pattern = "\d{1,}\,\d{3,}\.\d{2}|\d{3}\.\d{2}|\d{1,}\,\d{3,}|\d{2,}|\d{2,}\.\d{2}|\d|\d{3,}.\d{3,}.\d{1,}|\d{2,}.\d{3,}.\d{1,}|\d{1,}.\d{3,}.\d{1,}"
    #     dataframe['brand_price'] = dataframe['brand_price'].apply(lambda x: float("".join((re.findall(string=x, pattern=pattern)[-1]).split(','))))
 
        dataframe['brand_price'] = dataframe['brand_price'].apply(cleanpricevalue)

    except IndexError:
        print("***Index Error***")
        print("***use price_replace param***")

        
    dataframe.sort_values(by="brand_price").to_csv(save_to_path, index=False)



