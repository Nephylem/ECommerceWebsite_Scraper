from scraperv1 import Scraper, save_to_file, send_to_trash
import os 


"""WRITE YOUR CODE HERE"""

brand_selector = 'div[class="content-description"] div[class="content-title"]'
info_selector = 'div[class="content-description"] div[class="content-title"]'
link_selector = 'div[class="quick-view-btn"]>a'
price_selector = 'div[class="content-description"] div[class="content-price"]'

url="https://www.furniture-republic.com.ph/product-category/bar-chair-stool"

site_name="furniturerepublicph"

scraper = Scraper(
    brand_selector=brand_selector,
    info_selector=info_selector,
    link_selector=link_selector,
    price_selector=price_selector,
    url=url,
    site_name=site_name
)

scraper.load_url()
scraper.get_page()
scraper.save_file()
scraper.close()