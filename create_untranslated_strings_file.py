from Oyasis import oyasis

#configure your login
config = oyasis.Ini()
#acquire new session using the config deta
session = oyasis.Session(ini=config)
#start translation
tafsiri_work = oyasis.Tafsiri(session=session)
tafsiri_work.get_all_untranslated_strings()
