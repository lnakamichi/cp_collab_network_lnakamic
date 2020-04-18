import pandas as pd

from db_writer import *

cnx, cur = init_connection_with_json("./login.json")

researchers = select_all_from_table('Researchers2', cur)
researcher_rid_set = set(map(lambda researcher_tup: researcher_tup[0], researchers))
print(len(researcher_rid_set))

authors = select_all_from_table('Authors2', cur)
author_rid_set = set(map(lambda author_tup: author_tup[1], authors))
print(len(author_rid_set))

for rid in researcher_rid_set:
    if rid not in author_rid_set:
        delete_researcher(rid, cur, cnx)

close_connection(cnx, cur)
