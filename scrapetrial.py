from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys, ActionChains

import pandas as pd
from urllib.parse import urlparse, urljoin
import time
import os
from cleaner import save_to_file, send_to_trash


class Scraper(): 
    browser = Chrome()
    """Ecommerce website scraper object"""

    def __init__(self, 
                brand_selector, 
                info_selector, 
                price_selector, 
                link_selector, 
                site_name, 
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

        self.links = set()
        
        self.browser_wait = WebDriverWait(self.browser, 10)

    def load_url(self, url=""):
        url = url or self.url
        self.browser.get(url)

    def get_page(self):     
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

    def next_page(self, xpath=False):
        """press site next page"""
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
        item = self.items['product list']
        
        pd.DataFrame(item).to_csv(f"{site_name}_{self.file_name}.csv", index=False)
        
        print(f"scrapped {self.browser.current_url}")
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
    
    def follow_links(self, path=[], press_end=False):

        """follow and scrape the extracted links from extract links function"""

        if path:
            for url in path:
                self.load_url(url)
                if press_end:
                    for _ in range(10):
                        time.sleep(1)
                        self.press_end()
                
                try:
                    self.get_page()
                    self.save_file()
                except:
                    print('****No Content****')
        else:            
            for url in self.links:
                self.load_url(url)
                if press_end:
                    for _ in range(10):
                        time.sleep(1)
                        self.press_end()
                
                try:
                    self.get_page()
                    self.save_file()
                except:
                    print('****No Content****')


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
        with open(f"{self.site_name}.txt", "w") as write:
            write.write(str(self.links))
            print(f"{self.site_name}.txt written..")
            write.close()              

    def extract_more_links(self, iteration=5):
        for _ in range(iteration):
            self.check_each_link()
        
        with open(f"{self.site_name}.txt", "w") as write:
            write.write(str(self.links))
            write.close()              
