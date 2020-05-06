import csv
import json
import pandas as pd
import requests
import time

from db_writer import *


GENDER_API_KEY = 'kWPETZVPqpbTDVjGXm'


def query_for_gender(name):
    response_raw = requests.get("https://gender-api.com/get?name={0}&key={1}".format(name, GENDER_API_KEY))
    response_json = json.loads(response_raw.text)
    time.sleep(0.5)
    return response_json['gender'], response_json['accuracy']


cnx, cur = init_connection_with_json("./login.json")

researchers = execute_select_operation(("SELECT rid, first_name FROM Researchers2", None), cur)
researchers_df = pd.DataFrame(researchers, columns=['rid', 'first_name'])

name_to_gender_tup = dict(map(lambda name: (name, query_for_gender(name)), set(researchers_df['first_name'])))
with open('./data/name_to_gender.csv', 'w') as name_to_gender_file:
    name_to_gender_writer = csv.writer(name_to_gender_file)
    for name_row in name_to_gender_tup.items():
        name_to_gender_writer.writerow((name_row[0], name_row[1][0], name_row[1][1]))

# read from file
# name_to_gender_tup = dict()
# with open('./data/name_to_gender.csv', 'r') as name_to_gender_file:
#     reader = csv.reader(name_to_gender_file)
#     for row in reader:
#         name_to_gender_tup[row[0]] = (row[1], row[2])

i = 0
n = len(researchers_df)

for _, row in researchers_df.iterrows():
    gender_tup = name_to_gender_tup[row['first_name']]
    update_gender(row['rid'], gender_tup[0], gender_tup[1], cur, cnx)
    i = i + 1
    print(i/n)

close_connection(cnx, cur)
