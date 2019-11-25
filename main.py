from Oyasis import oyasis
#configure your login
config = oyasis.Ini(username="JohnDoe",password="StrongPassword")
#acquire new session using the config deta
session = oyasis.Session(ini=config)
#start translation
tafsiriWork = oyasis.Tafsiri(session=session)
#selecting a project to work on
#tafsiriWork.selectProject("Mate User Guide")
tafsiriWork.select_random_project()
#select random string
while(True):
    randomString=tafsiriWork.get_random_string()
    print(randomString["RandString"])
    translated = input("Translation: ")
    tafsiriWork.translate(translation=translated,todo=randomString)
