import requests
from bs4 import BeautifulSoup
import random
import json
from SeleniumScript.selenium_script import SeleniumScript as sel_script
import configparser


class Ini:
    def __init__(self):
        self.config = configparser.ConfigParser().read('../config.ini')
        self.username = self.config['WEBLATE']['username']
        self.password = self.config['WEBLATE']['password']
        self.url = self.config['WEBLATE']['url']

    def set_password(self, password):
        self.password = password

    def set_username(self, username):
        self.username = username

    @staticmethod
    def get_url(self):
        return self.url


class Session:
    def __init__(self, **kwargs):
        self.__ini = kwargs["ini"]
        head = {'Content-Type': 'application/x-www-form-urlencoded', \
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        login_details = {"username": self.__ini.username, "password": self.__ini.password}
        url = self.__ini.url + "/accounts/login/"
        with requests.Session() as s:
            # open the login page
            r = s.get(url)
            # Get the csrf-token from input tag
            soup = BeautifulSoup(r.text, "lxml")
            # Get the page cookie
            cookie = r.cookies
            self.cookies = cookie
            csrf_token = soup.select_one('input[name="csrfmiddlewaretoken"]')['value']
            # Set CSRF-Token
            head['X-CSRF-Token'] = csrf_token
            head['X-Requested-With'] = 'XMLHttpRequest'
            head['Referer'] = self.__ini.url
            self.head = head
            login_details["csrfmiddlewaretoken"] = csrf_token
            # request login
            r = s.post(url, cookies=cookie, data=login_details, headers=head)
            self.session = s

    def getSession(self):
        return self.session



class Tafsiri:
    def __init__(self, **kwargs):
        self.__session = kwargs["session"]
        self.config = configparser.ConfigParser().read('config.ini')
        self.__url = self.config['WEBLATE']['url']

    def get_components(self):
        weblate_session = self.__session.getSession()
        weblate_api_response = weblate_session.get(self.__url+"/api/components/?format=json")
        components_dict = json.loads(weblate_api_response.text)
        components_list = components_dict["results"]
        while components_dict["next"] is not None:
            weblate_api_response = weblate_session.get(components_dict["next"])
            components_dict = json.loads(weblate_api_response.text)
            components_list_next_page = components_dict["results"]
            components_list += components_list_next_page
        return components_list

    def select_component(self):
        components = self.get_components()
        for component in components:
            if self.get_translation_progress(component["statistics_url"]) < 100.0:
                return component
        return None

    def get_translation_progress(self, component_url):
        weblate_session = self.__session.getSession()
        weblate_api_response = weblate_session.get(component_url)
        statistics_dict = json.loads(weblate_api_response.text)
        progress_results_per_languages = statistics_dict["results"]
        for progress in progress_results_per_languages:
            if progress["code"] == 'sw':
                return progress["translated_percent"]
        print("sw not detected in "+component_url)

    def get_random_string(self):
        component = self.select_component()
        if component is None:
            return "No untranslated strings"
        url = component["web_url"]
        url_for_untranslated_strings = url.replace("/projects/","/translate/")+"sw/?type=nottranslated"
        weblate_session = self.__session.getSession()
        weblate_request = weblate_session.get(url_for_untranslated_strings)
        beautifulsoup_object = BeautifulSoup(weblate_request.text, "lxml")
        form = beautifulsoup_object.select_one('form[class="translation-form translator"]')
        cookie = weblate_request.cookies
        csrf_token = beautifulsoup_object.select_one('input[name="csrfmiddlewaretoken"]')['value']
        # Set CSRF-Token
        head = {}
        head['X-CSRF-Token'] = csrf_token
        head['X-Requested-With'] = 'XMLHttpRequest'
        head['Referer'] = url_for_untranslated_strings
        # get a random offset
        offset = int(beautifulsoup_object.select_one('input[id="id-goto-number"]')["max"])
        random_offset = random.randrange(1, offset)
        rqst = weblate_session.get(f"{url_for_untranslated_strings}&offset={random_offset}")
        soup = BeautifulSoup(rqst.text, "lxml")
        form = soup.select_one('form[class="translation-form translator"]')
        formelbs = BeautifulSoup(str(form), "lxml")
        endpoint = form['action']
        content_sum = formelbs.select_one('input[name="contentsum"]')['value']
        translation_sum = formelbs.select_one('input[name="translationsum"]')['value']
        csrf_token = formelbs.select_one('input[name="csrfmiddlewaretoken"]')['value']
        ranstring = formelbs.select_one('button[class="btn btn-link btn-xs pull-right flip"]')['data-clipboard-text']
        checksum = formelbs.select_one('input[name="checksum"]')['value']
        result = {"endpoint": endpoint, \
                  "cookies": cookie, \
                  "header": head, \
                  "checksum": checksum, \
                  "contentsum": content_sum, \
                  "csrfmiddlewaretoken": csrf_token, \
                  "RandString": ranstring, \
                  "component": component["web_url"],\
                  "translationsum": translation_sum, \
                  "offset": random_offset \
                  }
        return result

    def translate(self, **kwargs):
        todo = kwargs["todo"]
        translation = kwargs["translation"]
        url = self.url + todo["endpoint"]
        print("making submission to "+ url)
        cookie = todo["cookies"].items()[0]
        checksum = todo["checksum"]
        translation_box_xpath = self.set_translation_box_xpath(checksum)
        selenium_script = sel_script()
        selenium_script.navigate_page(url, cookie)        
        selenium_script.set_translation(translation_box_xpath, translation)
        selenium_script.send_translation("div.panel:nth-child(1) > div:nth-child(3) > button:nth-child(1)")

    @staticmethod
    def set_translation_box_xpath(checksum):
        return '//*[@id="id_'+checksum+'_0"]'


class StringsFile:

    def __init__(self):
        self.config = configparser.ConfigParser().read('../config.ini')
        self.filename = self.config['PERSISTENCE']['untranslated_strings_file_path']
        self.existing_phrase_endpoints = self.get_existing_phrase_endpoints()

    def get_file_contents(self):
        english_string_obj_file = open(self.filename, 'r')
        english_string_obj_file_contents = english_string_obj_file.readlines()
        return english_string_obj_file_contents

    def get_existing_phrase_endpoints(self):
        endpoints_list = []
        all_file_contents = self.get_file_contents()
        for entry in all_file_contents:
            try:
                json_obj = json.loads(entry.strip().replace("'",'"'))
                endpoints_list.append(json_obj['endpoint'])
            except Exception as e:
                continue
        return endpoints_list

    def write_untranslated_strings_file(self, string_object):
        untranslated_strings_file = open(self.filename,'w')
        if string_object['endpoint'] not in self.existing_phrase_endpoints:
            untranslated_strings_file.write(str(string_object))
            untranslated_strings_file.write('\n')
        else:
            print(str(string_object)+' is already in file')

