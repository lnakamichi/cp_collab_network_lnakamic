import pandas as pd

from db_writer import *

cnx, cur = init_connection_with_json("./login.json")

data = select_all_data(cur)
data_df = pd.DataFrame(data, columns=['department', 'institution', 'first_name', 'middle_name', 'last_name', 'title',
                                      'year'])
data_df.to_csv('./data/all_collaboration_data.csv')

close_connection(cnx, cur)
