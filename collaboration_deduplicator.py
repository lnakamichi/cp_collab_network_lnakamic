import pandas as pd

from db_writer import *


cnx, cur = init_connection_with_json("./login.json")

collaborations = select_all_from_table("Collaborations2", cur)
collaborations_df = pd.DataFrame(collaborations,
                                 columns=['cid', 'title', 'year', 'created_at', 'updated_at', 'data_source', 'type'])

found_titles = set()
cids_to_delete = set()

for _, row in collaborations_df.iterrows():
    if row['title'] in found_titles:
        cids_to_delete.add(row['cid'])
    else:
        found_titles.add(row['title'])

print("Found {0} titles to delete, updated table size will be: {1}".format(len(cids_to_delete), len(found_titles)))
print(cids_to_delete)

print('Delete? (y/n)')
response = input()

if 'y' in response:
    for cid in cids_to_delete:
        delete_collaboration(cid, cur, cnx)

close_connection(cnx, cur)
