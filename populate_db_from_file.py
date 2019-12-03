import sqlite3
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
english_string_obj_file = open(config['PERSISTENCE']['untranslated_strings_file_path'], "r")
english_string_obj_file_contents = english_string_obj_file.readlines()
conn = sqlite3.connect(config['PERSISTENCE']['database'])
localisation_main_table_sql = '''
create table if not exists localisation_main
(
    phrase_id           integer
        constraint localisation_main_pk
            primary key,
    package             text not null,
    english_phrase      text not null,
    swahili_translation text,
    translator          text,
    verified            integer,
    checksum            text,
    phrase_url          text,
    offset              int,
    passed_to_weblate   text
);

'''

translator_ids_table_sql = '''create table if not exists translators_ids
(
    user_id    int not null
        constraint translators_ids_pk
            primary key,
    first_name text,
    points     int
);'''
conn.execute(localisation_main_table_sql)
conn.execute(translator_ids_table_sql)
cursor = conn.cursor()
links = []

exisiting_checksums_query = 'select phrase_url from localisation_main'
exisiting_checksums_cursor = conn.execute(exisiting_checksums_query)
for entry in exisiting_checksums_cursor:
    links.append(entry[0])

for line in english_string_obj_file_contents:
    stripped_line = line.strip()
    json_obj = {}
    try:
        json_obj = json.loads(stripped_line.replace("'", '"'))
    except Exception as e:
        continue
    package = json_obj['component']
    english_phrase = json_obj['RandString']
    checksum = json_obj['checksum']
    phrase_url = json_obj['endpoint']
    offset = json_obj['offset']
    if phrase_url in links: print("already registered this, skipping...")
    if phrase_url in links: continue
    insert_stmt = 'insert into localisation_main(package, english_phrase, checksum, phrase_url, offset) values ("' + package + '", "' + english_phrase + '", "' + checksum + '", "' + phrase_url + '", "' + str(
        offset) + '")'
    cursor.execute(insert_stmt)
    conn.commit()

conn.close()
