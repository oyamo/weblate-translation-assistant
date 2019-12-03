import sqlite3
import configparser
from Oyasis import oyasis

config = oyasis.Ini()
session = oyasis.Session(ini=config)
tafsiri_work = oyasis.Tafsiri(session=session)

config = configparser.ConfigParser()
config.read('config.ini')

conn = sqlite3.connect(config['PERSISTENCE']['database'])
cursor = conn.cursor()
unpersisted_translations = []

passed_to_weblate_query = 'select checksum, phrase_url, swahili_translation, phrase_id from localisation_main where passed_to_weblate is not "true" and swahili_translation is not null'
passed_to_weblate_cursor = conn.execute(passed_to_weblate_query)
for entry in passed_to_weblate_cursor:
    unpersisted_translations.append(entry)

for unpersisted in unpersisted_translations:
    weblate_request = session.getSession().get(config['WEBLATE']['url'])
    cookie = session.getCookies()
    print(cookie.items())
    tafsiri_work.translate(translation=unpersisted[2],todo={'endpoint':unpersisted[1],'cookies':cookie,'checksum':unpersisted[0]})
    print("just translated\n"+str(unpersisted))
    sql_query = 'UPDATE localisation_main set passed_to_weblate = "true" where phrase_id = '+ str(unpersisted[3])
    cursor.execute(sql_query)
    conn.commit()
    
conn.close()

