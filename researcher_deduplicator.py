import pandas as pd

from db_writer import *


def get_value_from_row_list(column, row_list):
    value_set = set(filter(lambda v: not pd.isnull(v) and not v == '', map(lambda row: row[column], row_list)))
    if len(value_set) == 0:
        return None
    elif len(value_set) == 1:
        return next(iter(value_set))
    else:
        value_list = list(value_set)
        print('Which of these values should be accepted?')
        for i in range(len(value_list)):
            print('{0}. {1}'.format(i, value_list[i]))
        response = input()
        if response.isdigit():
            return value_list[int(response)]
        elif len(response) == 0:
            return None
        else:
            return response


def get_new_row_info(row_list):
    final_values = dict()
    print("Processing: {0} {1}".format(row_list[0]['first_name'], row_list[0]['last_name']))
    for column in ['department', 'institution', 'first_name', 'middle_name', 'last_name', 'hired_year',
                   'cal_poly_position', 'education']:
        new_value = get_value_from_row_list(column, row_list)
        print('{0}: {1}'.format(column, new_value))
        final_values[column] = new_value
    return final_values


cnx, cur = init_connection_with_json("./login.json")

researchers = select_all_from_table('Researchers2', cur)
researchers = pd.DataFrame(researchers, columns=['rid', 'department', 'institution', 'created_at', 'updated_at',
                                                 'first_name', 'middle_name', 'last_name', 'ms_id', 'hired_year',
                                                 'cal_poly_position', 'education'])

found_names = dict()

for _, researcher in researchers.iterrows():
    name_tuple = (researcher['first_name'], researcher['last_name'])
    if name_tuple in found_names.keys():
        found_names[name_tuple].append(researcher)
    else:
        found_names[name_tuple] = [researcher]

with open('./data/duplicate_rids', 'a') as rid_file:
    i = 0
    print(len(found_names))
    for name, rows in found_names.items():
        print(i)
        i += 1
        if len(rows) > 1:
            new_values = get_new_row_info(rows)
            op = insert_researchers_operation(new_values['first_name'], new_values['middle_name'], new_values['last_name'],
                                              new_values['department'], new_values['institution'], None,
                                              new_values['hired_year'], new_values['cal_poly_position'],
                                              new_values['education'])
            new_rid = execute_insert_operation(op, cur, cnx)
            rids_to_replace = list(map(lambda row: row['rid'], rows))
            rid_file.write('{0}->{1}\n'.format(new_rid, ','.join(map(str, rids_to_replace))))
            for rid in rids_to_replace:
                update_author_rid(rid, new_rid, cur, cnx)
                delete_researcher(rid, cur, cnx)

close_connection(cnx, cur)
