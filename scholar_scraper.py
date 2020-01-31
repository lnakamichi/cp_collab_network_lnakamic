import scholarly

from researcher import Researcher
from db_connector import *

def generate_researcher(scholarly_result):
    researcher = Researcher(scholarly_result.name)
    researcher.fill_with_scholarly(scholarly_result)
    return researcher

def get_scholarly_result(name):
    query = scholarly.search_author((','.join((name, '@calpoly.edu'))))
    for entry in query:
        if entry.name == name:
            return entry.fill()
    return None

cnx, cur = init_connection_with_json("./login.json")
print(generate_researcher(get_scholarly_result("Theresa Migler")))
close_connection(cnx, cur)
