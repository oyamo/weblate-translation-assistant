from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import configparser


class SeleniumScript:
    
    def __init__(self):
        self.config = configparser.ConfigParser().read('config.ini')
        self.chromedriver_location = self.config['SELENIUM']['chrome_webdriver_location']
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("disable-gpu")
        self.chrome_options.add_argument("window-size=1440,900")
        self.driver = webdriver.Chrome(self.chromedriver_location, options=self.chrome_options)
        
    def navigate_page(self, url, cookie):
        self.driver.get(url)
        self.driver.add_cookie(self.construct_cookie(cookie, url))
        self.driver.refresh()
    
    @staticmethod
    def construct_cookie(cookie, url):
        sessionid_value = cookie[1]
        domain = url.split("//")[1].split("/")[0]
        constructed_cookie_dict = {"name":"sessionid","domain":domain,"value":sessionid_value}
        return constructed_cookie_dict
        
    def set_translation(self, xpath, translation):
        self.driver.find_element_by_xpath(xpath).send_keys(translation)
        
    def send_translation(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()

