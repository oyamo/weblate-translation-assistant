from Oyasis import oyasis

# configure your login
config = oyasis.Ini()
# acquire new session using the config deta
session = oyasis.Session(ini=config)
#start translation
tafsiri_work = oyasis.Tafsiri(session=session)
#select random string
while(True):
    random_string_dict=tafsiri_work.get_random_string()
    print(random_string_dict["component"]+" -> "+random_string_dict["RandString"])
    translated = input("Translation: ")
    tafsiri_work.translate(translation=translated,todo=random_string_dict)
