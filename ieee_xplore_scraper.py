import json
import Levenshtein
import pandas as pd
import requests

from db_writer import *


rid_cache = dict()


# copied from mathscinet_data_reader.py
def get_rid_with_cache(first_name, last_name):
    if (first_name, last_name) in rid_cache.keys():
        return rid_cache[(first_name, last_name)]
    else:
        rid = extract_rid_from_db(first_name, last_name)
        # add rid to cache
        rid_cache[(first_name, last_name)] = rid
        return rid


# copied from mathscinet_data_reader.py
def extract_rid_from_db(first, last):
    response_list = find_rid_by_name(first, last, cur)
    if len(response_list) == 0:
        op = insert_researchers_operation_minimum(first, last)
        rid = execute_insert_operation(op, cur, cnx)
        return rid
    else:
        return response_list[0][0]


def name_to_tuple(name_string):
    name_list = name_string.lower().split()
    if len(name_list) == 1:
        return name_string, name_string
    elif len(name_list) == 2:
        return name_list[0], name_list[1]
    # elif len(name_list) == 3:
    #     return name_list[0], name_list[2]
    else:
        return name_list[0], ' '.join(name_list[1:])


def get_rids(author_list):
    rid_list = []
    for author_dict in author_list:
        tup = name_to_tuple(author_dict['full_name'])
        rid_list.append(get_rid_with_cache(tup[0], tup[1]))
    return rid_list


# copied from mathscinet_data_reader.py
def title_missing(title, publications):
    for publication in publications:
        if title == publication:
            return False
        elif Levenshtein.distance(title, publication) < 10:
            print('Are these the same? (Y/n)')
            print('1. {0}'.format(title))
            print('2. {0}'.format(publication))
            response = input()
            if len(response) == 0 or 'y' in response:
                return False
    return True


# copied from mathscinet_data_reader.py
def process_publication_row_list(rows):
    name_to_publications = dict()
    for row in rows:
        first_last = (row[0], row[1])
        if first_last in name_to_publications.keys():
            name_to_publications[first_last].append(row[2].lower())
        else:
            name_to_publications[first_last] = [row[2].lower()]
    return name_to_publications


class IEEEXploreScraper:
    URL_PREFIX = ('http://ieeexploreapi.ieee.org/api/v1/search/articles?apikey=8smb77nr6a97kqmqex7mmn84' +
                  '&format=json&max_records=200&sort_order=asc&sort_field=article_number')

    def get_query_response_df(self, name_string, page):
        response = requests.get(
            self.URL_PREFIX + '&start_record={0}'.format(1 + (200 * page)) + '&author=' + name_string.replace(' ', '+'))
        response_dict = json.loads(response.text)
        num_records = response_dict['total_records']
        if num_records == 0:
            return pd.DataFrame()
        data_articles = response_dict['articles']
        article_df = pd.json_normalize(data_articles)
        if num_records > (page + 1) * 200:
            article_df = article_df.append(self.get_query_response_df(name_string, page + 1), ignore_index=True)
        return article_df

    def scrape_for_researcher(self, name_string, found_publications):
        article_df = self.get_query_response_df(name_string, 0)
        for _, row in article_df.iterrows():
            title = row['title'].lower()
            if title_missing(title, found_publications):
                content_type = row['content_type'].lower()
                year = row['publication_year']
                rids = get_rids(row['authors.authors'])
                collaboration_op = insert_collaborations_operation_with_type(
                    title, year, 'IEEE_XPLORE', content_type)
                cid = execute_insert_operation(collaboration_op, cur, cnx)
                print('Added collaboration: {0}'.format(title))
                for rid in rids:
                    next_author_op = insert_authors_operation(cid, rid)
                    execute_insert_operation(next_author_op, cur, cnx)
                print('Added {0} authors for collaboration'.format(len(rids)))


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

CS_FACULTY = [
    'Chris Lupo',
    'Paul Anderson',
    'Hisham Assal',
    'John Bellardo',
    'John Clements',
    'Bruno da Silva',
    'Bruce DeBruhl',
    'Alex Dekhtyar',
    'Christian Eckhardt',
    'Sussan Einakian',
    'Davide Falessi',
    'Dongfeng Fang',
    'Sara Ford',
    'Kris Fox',
    'Hasmik Gharibyan',
    'Paul Hatalsky',
    'Michael Haungs',
    'Irene Humer',
    'David Janzen',
    'Daniel Kauffman',
    'Aaron Keen',
    'Foaad Khosmood',
    'Toshihiro Kuboi',
    'Franz Kurfess',
    'Kurt Mammen',
    'Andrew Migler',
    'Theresa Migler',
    'Kirsten Mork',
    'Phillip Nico',
    'Maria Pantoja',
    'David Parkinson',
    'Zachary Peterson',
    'John Planck',
    'Michael Reynosa',
    'Nicholas Sakellariou',
    'John Seng',
    'Erin Sheets',
    'Christopher Siu',
    'Hugh Smith',
    'Clint Staley',
    'Lubomir Stanchev',
    'Clark Turner',
    'Ignatios Vakalis',
    'Michael Van De Vanter',
    'Jonathan Ventura',
    'Kurt Voelker',
    'Zoë Wood',
    'Julie Workman'
]

cnx, cur = init_connection_with_json("./login.json")

scraper = IEEEXploreScraper()

name_to_publications = process_publication_row_list(
    select_collaborations_from_department('computer science', cur))

for name in CS_FACULTY:
    name_tuple = name_to_tuple(name)
    if name_tuple in name_to_publications.keys():
        scraper.scrape_for_researcher(name, name_to_publications[name_tuple])
    else:
        scraper.scrape_for_researcher(name, [])

close_connection(cnx, cur)
