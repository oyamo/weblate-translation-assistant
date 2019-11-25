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

    def get_projects(self):
        weblate_session = self.__session.getSession()
        weblate_api_response = weblate_session.get("https://tafsiri.swahilinux.org/api/projects/?format=json")
        projects_dict = json.loads(weblate_api_response)
        projects_list = projects_dict["results"]
        return projects_list
    def selectProject(self,title):
        projects = self.getProjects()
        Dict = [{"title":x["title"],"endpoint":x["endpoint"]} for x in projects if x["title"] == title][0]
        selected_project = Project(Dict["title"],Dict["endpoint"])
        self.project = selected_project
    def selectRandomProject(self):
        projects = self.getProjects()
        self.project = random.choice(projects)

    def getRandomString(self):
        project = self.project
        url = self.url+"/translate"+project.get_endpoint()[9:]
        url = url+ project.get_endpoint()[10:]+"sw/?type=nottranslated"
        s = self.__session.getSession()
        rqst = s.get(url)
        soup = BeautifulSoup(rqst.text,"lxml")
        form = soup.select_one('form[class="translation-form translator"]')
        cookie = rqst.cookies
        csrf_token = soup.select_one('input[name="csrfmiddlewaretoken"]')['value']
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
