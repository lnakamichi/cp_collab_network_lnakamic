import json
import numpy as np
import requests
import pandas as pd

from bs4 import BeautifulSoup
from db_writer import *


def get_ms_query(name):
    return (name.lower().replace(' ', '+')
            + '+california+polytechnic+state+university')


def author_entity_to_dict(author_entity):
    names = author_entity['AuN'].split()
    first_name = names[0]
    last_name = names[-1]
    middle_name = '' if len(names) == 2 else ' '.join(names[1:-1])
    return {
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'institution': author_entity.get('AfN'),
        'ms_id': author_entity.get('AuId')
    }


def ms_entity_to_dict(entity):
    return {
        'title': entity['Ti'],
        'year': entity['Y'],
        'data_source': 'MICROSOFT_ACADEMIC',
        'authors': list(
            map(
                author_entity_to_dict,
                entity['AA']))
    }


def get_first_nonempty_string(series):
    for index, value in series.items():
        if isinstance(value, int):
            return value
        if len(value) > 0:
            return value
    return ''


class MsAcademicScraper:
    # Some methods borrowed from initial study
    MS_REQUEST_HEADERS = {
        'Host': 'api.labs.cognitive.microsoft.com',
        'Ocp-Apim-Subscription-Key': '4875ccd816c14d38a2ba6f703bbef29a'}
    MS_URL_PREFIX = 'https://api.labs.cognitive.microsoft.com/academic/v1.0'

    def __init__(self):
        self.rid_temp = 0
        self.cid_temp = 0
        self.collaborations_df = pd.DataFrame(
            columns=['cid_temp', 'title', 'year', 'data_source'])
        self.researchers_df = pd.DataFrame(
            columns=['rid_temp', 'first_name', 'middle_name', 'last_name', 'department', 'institution', 'ms_id'])
        self.authors_df = pd.DataFrame(
            columns=['cid_temp', 'rid_temp'])

    def get_ms_query_expr(self, name):
        url = ('%s/interpret?query=%s&count=1000' % (self.MS_URL_PREFIX,
                                                     get_ms_query(name)))
        r = requests.get(url, headers=self.MS_REQUEST_HEADERS)
        response_dict = json.loads(r.content)
        if response_dict.get('interpretations'):
            first_interpretation = response_dict.get('interpretations')[0]
            soup = BeautifulSoup(first_interpretation['parse'], 'html.parser')
            element = soup.find('attr', {'name': 'academic#AA.AuN'})
            try:
                canonical_name = element['canonical']
            except KeyError:
                canonical_name = element.get_text()
            canonical_name = canonical_name.replace(' ', '+')
            return "Composite(AA.AuN=='%s')" % (canonical_name)

    def fill_with_ms(self, name):
        url = ('%s/evaluate?expr=%s&attributes=Ti,Y,CC,ECC,AA.AuN,AA.AuId,'
               'AA.AfN,AA.AfId,AA.S,J.JN,J.JId,C.CN,C.CId,E.VFN&count=1000'
               % (self.MS_URL_PREFIX, self.get_ms_query_expr(name)))
        r = requests.get(url, headers=self.MS_REQUEST_HEADERS)
        response_dict = json.loads(r.content)
        try:
            return list(
                map(ms_entity_to_dict,
                    response_dict.get('entities', [])))
        except KeyError:
            pass

    def insert_researcher_df(self, first_name, middle_name, last_name, department, institution, ms_id):
        cur_rid = self.rid_temp
        row = pd.DataFrame.from_dict({
            'rid_temp': [cur_rid],
            'first_name': [first_name],
            'middle_name': [middle_name or ''],
            'last_name': [last_name],
            'department': [department or ''],
            'institution': [institution or ''],
            'ms_id': [ms_id or '']
        })
        self.researchers_df = self.researchers_df.append(row, ignore_index=True)
        self.rid_temp = cur_rid + 1
        return cur_rid

    def insert_collaboration_df(self, title, year, data_source):
        cur_cid = self.cid_temp
        row = pd.DataFrame.from_dict({
            'cid_temp': [cur_cid],
            'title': [title],
            'year': [year],
            'data_source': [data_source]
        })
        self.collaborations_df = self.collaborations_df.append(row, ignore_index=True)
        self.cid_temp = cur_cid + 1
        return cur_cid

    def insert_authors_df(self, cid, rid):
        row = pd.DataFrame.from_dict({
            'cid_temp': [cid],
            'rid_temp': [rid]
        })
        self.authors_df = self.authors_df.append(row, ignore_index=True)

    def fold_researchers_df(self):
        ms_id_counts = self.researchers_df['ms_id'].value_counts()
        repeated_ms_ids = set(ms_id_counts[ms_id_counts > 1].index)
        for ms_id in repeated_ms_ids:
            researcher_entries = self.researchers_df[self.researchers_df['ms_id'] == ms_id]
            first_name = get_first_nonempty_string(researcher_entries['first_name'])
            middle_name = get_first_nonempty_string(researcher_entries['middle_name'])
            last_name = get_first_nonempty_string(researcher_entries['last_name'])
            department = get_first_nonempty_string(researcher_entries['department'])
            institution = get_first_nonempty_string(researcher_entries['institution'])
            ms_id = get_first_nonempty_string(researcher_entries['ms_id'])
            self.researchers_df.drop(researcher_entries.index, inplace=True)
            new_rid = self.insert_researcher_df(
                first_name,
                middle_name,
                last_name,
                department,
                institution,
                ms_id)
            self.authors_df['rid_temp'] = np.where(
                np.isin(self.authors_df['rid_temp'], researcher_entries['rid_temp'].tolist()),
                new_rid,
                self.authors_df['rid_temp'])

    def scrape_for_researcher(self, first_name, middle_name, last_name, department, institution):
        name = ' '.join(filter(lambda n: n is not None, [first_name, middle_name, last_name]))
        base_researcher_id = None
        collaborations = self.fill_with_ms(name)
        if len(collaborations) == 0:
            print('No collaborations for {}'.format(name))
        for collaboration in collaborations:
            # if base_researcher_id is None:
            #     base_author_entry = next(
            #         entry for entry in
            #         collaboration['authors']
            #         if entry['first_name'] == first_name and entry['last_name'] == last_name)
            #     base_researcher_id = self.insert_researcher_df(
            #         first_name,
            #         middle_name,
            #         last_name,
            #         department,
            #         institution,
            #         base_author_entry['ms_id'])
            # collaborator_ids = [base_researcher_id]
            collaborator_ids = []
            for author in collaboration['authors']:
                # if author['first_name'] != first_name and author['last_name'] != last_name:
                collaborator_ids.append(self.insert_researcher_df(
                    author['first_name'],
                    author['middle_name'],
                    author['last_name'],
                    '',
                    author['institution'],
                    author['ms_id']
                ))
            collaboration_id = self.insert_collaboration_df(
                    collaboration['title'],
                    collaboration['year'],
                    collaboration['data_source'])
            for collaborator in collaborator_ids:
                self.insert_authors_df(collaboration_id, collaborator)


CAL_POLY = 'california polytechnic state university'

MATH_PROFESSORS = [
    'Bonini, Vincent',
    'Borzellino, Joe',
    'Brussel, Eric',
    'Camp, Charles',
    'Champney, Danielle',
    'Charalampidis, Stathis',
    'Choboter, Paul',
    'Dimitrova, Elena',
    'Easton, Rob',
    'Grundmeier, Todd',
    'Gu, Caixing',
    'Hamilton, Emily',
    'Kato, Goro',
    'Kaul, Anton',
    'Kirk, Colleen',
    'Liese, Jeff',
    'Lin, Joyce',
    'Medina, Elsa',
    'Mendes, Anthony',
    'Paquin, Dana',
    'Patton, Linda',
    'Pearse, Erin',
    'Retsek, Dylan',
    'Richert, Ben',
    'Riley, Kate',
    'Robbins, Marian',
    'Schinck-Mikel, Amelie',
    'Shapiro, Jonathan',
    'Sherman, Morgan',
    'Stankus, Mark',
    'Sze, Lawrence',
    'White, Matthew',
    'Yoshinobu, Stan'
]

scraper = MsAcademicScraper()
for prof in MATH_PROFESSORS:
    print(prof)
    name_list = prof.split(', ')
    scraper.scrape_for_researcher(name_list[1].lower(), None, name_list[0].lower(), 'math', CAL_POLY)
# after all for one department are done
scraper.fold_researchers_df()

cnx, cur = init_connection_with_json("./login.json")
upload_dfs(scraper.collaborations_df, scraper.researchers_df, scraper.authors_df, cur, cnx)
close_connection(cnx, cur)
