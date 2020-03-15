import json
import numpy as np
import requests
import time
import datetime
import pandas as pd

from bs4 import BeautifulSoup
from db_writer import *
from calpoly_faculty_directory_scraper import *


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
        if value is not None and len(value) > 0:
            return value
    return None


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
            columns=['rid_temp', 'first_name', 'middle_name', 'last_name', 'department', 'institution', 'ms_id',
                     'hired_year', 'cal_poly_position', 'education'])
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
            'ms_id': [ms_id or ''],
            'hired_year': [None],
            'cal_poly_position': [None],
            'education': [None]
        })
        self.researchers_df = self.researchers_df.append(row, ignore_index=True)
        self.rid_temp = cur_rid + 1
        return cur_rid

    def insert_calpoly_researcher_df(self, first_name, middle_name, last_name, department, institution, ms_id,
                                     hired_year, cal_poly_position, education):
        cur_rid = self.rid_temp
        row = pd.DataFrame.from_dict({
            'rid_temp': [cur_rid],
            'first_name': [first_name],
            'middle_name': [middle_name or ''],
            'last_name': [last_name],
            'department': [department or ''],
            'institution': [institution or ''],
            'ms_id': [ms_id or ''],
            'hired_year': [hired_year or None],
            'cal_poly_position': [cal_poly_position or None],
            'education': [education or None]
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
            hired_year = get_first_nonempty_string(researcher_entries['hired_year'])
            cal_poly_position = get_first_nonempty_string(researcher_entries['cal_poly_position'])
            education = get_first_nonempty_string(researcher_entries['education'])
            self.researchers_df.drop(researcher_entries.index, inplace=True)
            new_rid = self.insert_calpoly_researcher_df(
                first_name,
                middle_name,
                last_name,
                department,
                institution,
                ms_id,
                hired_year,
                cal_poly_position,
                education
            )
            self.authors_df['rid_temp'] = np.where(
                np.isin(self.authors_df['rid_temp'], researcher_entries['rid_temp'].tolist()),
                new_rid,
                self.authors_df['rid_temp'])

    def scrape_for_researcher(self, first_name, middle_name, last_name, department, institution):
        name = ' '.join(filter(lambda n: n is not None, [first_name, middle_name, last_name]))
        faculty_dict = get_calpoly_faculty_dict()
        # base_researcher_id = None
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
                if (author['first_name'], author['last_name']) in faculty_dict.keys():
                    faculty_dict_info = faculty_dict[(author['first_name'], author['last_name'])]
                    collaborator_ids.append(self.insert_calpoly_researcher_df(
                        author['first_name'],
                        author['middle_name'],
                        author['last_name'],
                        department if author['first_name'] == first_name.lower() and author[
                            'last_name'] == last_name.lower() else '',
                        author['institution'],
                        author['ms_id'],
                        faculty_dict_info[0],
                        faculty_dict_info[1],
                        faculty_dict_info[2]
                    ))
                else:
                    collaborator_ids.append(self.insert_researcher_df(
                        author['first_name'],
                        author['middle_name'],
                        author['last_name'],
                        department if author['first_name'] == first_name.lower() and author['last_name'] == last_name.lower() else '',
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

MATH_FACULTY = [
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
    'Yoshinobu, Stan',
    # MATH LECTURERS
    'Bishop, Rebecca',
    'Chi, Haoyan',
    'Elwood, Jason',
    'Gervasi, Jeff',
    'Grishchenko, Lana',
    'Hahlbeck, Clint',
    'Hesselgrave, Bill',
    'Jenkin, Bryce',
    'Kreider, Brandy',
    'McCaughey, Tim',
    'Quackenbush, Blaine',
    'Robertson, Mike',
    'Schuster, Sonja',
    'Terry, Raymond',
    'Watson, Sean',
    'Yang, Fan'
]

BIO_FACULTY = [
    'Adams, Nikki',
    'Bean, Tim',
    'Black, Michael',
    'Blank, Jason',
    'Clement, Sandra',
    'Davidson, Jean',
    'Fidopiastis, Pat',
    'Francis, Clinton',
    'Grossenbacher, Dena',
    'Hardy, Kristin',
    'Himelblau, Ed',
    'Keeling, Elena',
    'Knight, Charles',
    'Kolluru, Gita',
    'Lema, Sean',
    'Liwanag, Heather',
    'Martinez, Nathaniel',
    'Pasulka, Alexis',
    'Perrine, John',
    'Rajakaruna, Nishi',
    'Ritter, Matthew',
    'Ruttenberg, Ben',
    'Strand, Christy',
    'Taylor, Emily',
    'Tomanek, Lars',
    'Villablanca, Francis',
    'Vredevoe, Larisa',
    'White, Crow',
    'Winstead, Candace',
    'Yep, Alejandra',
    'Yeung, Marie',
    'Yost, Jenn',
    # BIO LECTURERS
    'Bunting, Jamie',
    'Jones, Michael',
    'Babu, Praveen',
    'Bergen, Anne Marie',
    'Debruhl, Heather',
    'Goschke, Grace',
    'Hendricks, Steve',
    'Howes, Amy',
    'Jew, Kara',
    'Maj, Magdalena',
    'May, Mellisa',
    'McConnico, Laurie',
    'Neal, Emily',
    'Needles, Lisa',
    'O\'Neill, Megan',
    'Pisula, Anneka',
    'Polacek, Kelly',
    'Resner, Emily',
    'Roest, Michele',
    'Ryan, Sean',
    'Trunzo, Juliana',
    'VanderKelen, Jennifer'
]

EE_FACULTY = [
    'Dennis Derickson',
    'Samuel Agbo',
    'William Ahlgren',
    'Dean Arakaki',
    'Bridget Benson',
    'David Braun',
    'Joseph Callenes-Sloan',
    'Andrew Danowitz',
    'Fred DePiero',
    'Dale Dolan',
    'Ben Hawkins',
    'Xiaomin Jin',
    'Albert Liddicoat',
    'Art MacCarley',
    'James Mealy',
    'Ahmad Nafisi',
    'John Oliver',
    'Wayne Pilkington',
    'Majid Poshtan',
    'Vladimir Prodanov',
    'John Saghri',
    'Ali Shaban',
    'Lynne Slivovsky',
    'Tina Smilkstein',
    'Taufik Taufik',
    'Xiao-Hua Yu',
    'Jane Zhang',
    # EE LECTURERS
    'Kurt Behpour',
    'Chuck Bland',
    'Nazeih Botros',
    'Mostafa Chinichian',
    'Ali Dehghan Banadaki',
    'Steve Dunton',
    'Ron Eisworth',
    'Mona El Helbawy',
    'John Gerrity',
    'Doug Hall',
    'Paul Hummel',
    'Marty Kaliski',
    'Amin Malekmohammadi',
    'Dan Malone',
    'David McDonald',
    'Clay McKell',
    'Rich Murray',
    'Maxwell Muscarella',
    'Gary Perks',
    'John Planck',
    'Asit Rairkar',
    'Joe Sparks',
    'Hiren Trada',
    'Siddharth Vyas',
    'Michael Wilson'
]

scraper = MsAcademicScraper()

for prof in MATH_FACULTY:
    print(prof)
    name_list = prof.split(', ')
    first_name_split = name_list[1].split()
    if len(first_name_split) == 1:
        scraper.scrape_for_researcher(name_list[1].lower(), None, name_list[0].lower(), 'math', CAL_POLY)
    else:
        scraper.scrape_for_researcher(first_name_split[0].lower(), ' '.join(first_name_split[1:]).lower(), name_list[0].lower(), 'math', CAL_POLY)
    time.sleep(0.5)

for prof in BIO_FACULTY:
    print(prof)
    name_list = prof.split(', ')
    first_name_split = name_list[1].split()
    if len(first_name_split) == 1:
        scraper.scrape_for_researcher(name_list[1].lower(), None, name_list[0].lower(), 'biology', CAL_POLY)
    else:
        scraper.scrape_for_researcher(first_name_split[0].lower(), ' '.join(first_name_split[1:]).lower(), name_list[0].lower(), 'biology', CAL_POLY)
    time.sleep(0.5)

for prof in EE_FACULTY:
    print(prof)
    name_list = prof.split()
    if len(name_list) == 2:
        scraper.scrape_for_researcher(name_list[0].lower(), None, name_list[1].lower(), 'electrical engineering', CAL_POLY)
    elif len(name_list) == 3:
        scraper.scrape_for_researcher(name_list[0].lower(), name_list[1].lower(), name_list[2].lower(), 'electrical engineering', CAL_POLY)
    time.sleep(0.5)

scraper.fold_researchers_df()
print(scraper.researchers_df['department'].value_counts())
#
# # SAVE DF's
# timestamp = datetime.datetime.fromtimestamp(time.time()).isoformat()
# scraper.researchers_df.to_csv('./data/{0}_researchers.csv'.format(timestamp), index=False)
# scraper.authors_df.to_csv('./data/{0}_authors.csv'.format(timestamp), index=False)
# scraper.collaborations_df.to_csv('./data/{0}_collaborations.csv'.format(timestamp), index=False)

cnx, cur = init_connection_with_json("./login.json")
upload_dfs(scraper.collaborations_df, scraper.researchers_df, scraper.authors_df, cur, cnx)
close_connection(cnx, cur)
