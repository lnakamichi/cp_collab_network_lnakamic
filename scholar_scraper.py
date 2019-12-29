import scholarly

from researcher import Researcher

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

print(generate_researcher(get_scholarly_result("Theresa Migler")))
