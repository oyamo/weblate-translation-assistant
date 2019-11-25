import requests
import lxml
from bs4 import BeautifulSoup
import re
import random
import json


class Site:
    url = "https://tafsiri.swahilinux.org"


class Ini(Site):
    def __init__(self, **kwargs):
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.url = super().url

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

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


class Tafsiri(Site):
    def __init__(self, **kwargs):
        self.__session = kwargs["session"]
        self.__url = super().url

    def get_components(self):
        weblate_session = self.__session.getSession()
        weblate_api_response = weblate_session.get("https://tafsiri.swahilinux.org/api/components/?format=json")
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
                  "translationsum": translation_sum, \
                  "offset": random_offset \
                  }
        return result
        # print(content_sum,translation_sum,csrf_token,endpoint,offset,ranstring

    def translate(self, **kwargs):
        todo = kwargs["todo"]
        translation = kwargs["translation"]
        session = self.__session.getSession()
        url = self.url + todo["endpoint"]
        head = todo["header"]
        cookies = todo["cookies"]
        payload = {"csrfmiddlewaretoken": todo["csrfmiddlewaretoken"], \
                   "content": translation, \
                   "checksum": todo["checksum"], \
                   "fuzzy": "", \
                   "contentsum": todo["contentsum"], \
                   "translationsum": todo["translationsum"], \
                   "review": "0", \
                   "save": ""}
        head["Referer"] = url
        post = session.post(url, data=payload, cookies=cookies, headers=head)
        # with open("o.htm","w") as m:
        #     print(post.text)
