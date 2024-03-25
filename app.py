from scraper.instagram_scraper import InstagramScraper 
import os
from dotenv import load_dotenv
load_dotenv()



if __name__ == "__main__":
    USERNAME = os.getenv("INSTAGRAM_ACCOUNT")
    PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
    
    scraper = InstagramScraper(USERNAME, PASSWORD)
    scraper.extraction_routine()
    scraper.driver.quit()