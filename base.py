from scraperv1 import Scraper, concat_all_csv


"""WRITE YOUR CODE HERE"""

brand_selector = ''
info_selector = ''
link_selector = ''
price_selector = ''

url=""

site_name=""

scraper = Scraper(
    brand_selector=brand_selector,
    info_selector=info_selector,
    link_selector=link_selector,
    price_selector=price_selector,
    url=url,
    site_name=site_name
)

# Common Usage 
#
# scraper.load_url()
# scraper.get_page()
# scraper.save_file()
# scraper.close()

concat_all_csv(foldername=site_name, filename="all")
