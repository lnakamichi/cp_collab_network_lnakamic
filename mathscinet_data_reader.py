import Levenshtein
import pandas as pd

from db_writer import *


def process_publication_row_list(rows):
    name_to_publications = dict()
    for row in rows:
        first_last = (row[0], row[1])
        if first_last in name_to_publications.keys():
            name_to_publications[first_last].append(row[2].lower())
        else:
            name_to_publications[first_last] = [row[2].lower()]
    return name_to_publications


def extract_first_name(name):
    first_middle = name.split(', ')[1]
    if ' ' in first_middle:
        return first_middle.split()[0].lower()
    else:
        return first_middle.lower()


def extract_last_name(name):
    return name.split(', ')[0].lower()


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


def parse_collaborators(collaborators):
    if pd.isna(collaborators):
        return []
    collaborator_list = collaborators.split(';')
    return list(
        map(
            lambda name: (extract_first_name(name), extract_last_name(name)),
            collaborator_list
        )
    )


cnx, cur = init_connection_with_json("./login.json")


def extract_rid_from_db(first, last, cur):
    response_list = find_rid_by_name(first, last, cur)
    if len(response_list) == 0:
        op = insert_researchers_operation_minimum(first, last)
        rid = execute_insert_operation(op, cur, cnx)
        return rid
    else:
        return response_list[0][0]


msn_df = pd.read_csv('./data/mathscinet_collaborations.csv')
msn_df['title'] = msn_df['title'].apply(lambda t: t.lower())
msn_df['first_name'] = msn_df['searched researcher'].apply(extract_first_name)
msn_df['last_name'] = msn_df['searched researcher'].apply(extract_last_name)

name_to_publications = process_publication_row_list(select_collaborations_from_department("math", cur))

df_to_add = pd.DataFrame()

for name, publications in name_to_publications.items():
    msn_rows = msn_df[(msn_df['first_name'] == name[0]) & (msn_df['last_name'] == name[1])]
    missing_msn_rows = msn_rows.loc[map(lambda tup: title_missing(tup[1]['title'], publications), msn_rows.iterrows())]
    df_to_add = df_to_add.append(missing_msn_rows)

for row in df_to_add.iterrows():
    print(row)

if 'y' in input('Upload DF? y/n\n'):
    print('Uploading')
    rid_cache = dict()


    def get_rid_with_cache(first_name, last_name):
        if (first_name, last_name) in rid_cache.keys():
            return rid_cache[(first_name, last_name)]
        else:
            rid = extract_rid_from_db(first_name, last_name, cur)
            # add rid to cache
            rid_cache[(first_name, last_name)] = rid
            return rid


    for _, row_to_add in df_to_add.iterrows():
        main_rid = get_rid_with_cache(row_to_add['first_name'], row_to_add['last_name'])
        collaborator_tuples = parse_collaborators(row_to_add['collaborators'])
        collaborator_rids = list(
            map(
                lambda name: get_rid_with_cache(name[0], name[1]),
                collaborator_tuples
            )
        )
        op = insert_collaborations_operation(row_to_add['title'], row_to_add['year'], 'MATH_SCI_NET')
        cid = execute_insert_operation(op, cur, cnx)
        author_op = insert_authors_operation(cid, main_rid)
        execute_insert_operation(author_op, cur, cnx)
        for collaborator_rid in collaborator_rids:
            next_author_op = insert_authors_operation(cid, collaborator_rid)
            execute_insert_operation(next_author_op, cur, cnx)
        print('Uploaded: {0}'.format(row_to_add['title']))
else:
    print('DF will not be uploaded')

close_connection(cnx, cur)
