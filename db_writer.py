import mysql.connector
import json

HOST = "cpcollabnetwork8.cn244vkxrxzn.us-west-1.rds.amazonaws.com"
DB = 'cpcollabnet2019'


def init_connection_with_json(filename: str, db=DB, host=HOST):
    with open(filename, "r") as pickled_login:
        mysql_login = json.load(pickled_login)
    return init_connection(mysql_login["user"], mysql_login["password"],
                           db, host)


def init_connection(user, password, db=DB, host=HOST):
    cnx = mysql.connector.connect(user=user,
                                  password=password,
                                  host=host,
                                  database=db)
    cursor = cnx.cursor()
    return cnx, cursor


def close_connection(connection, cursor):
    cursor.close()
    connection.close()


def insert_collaborations_operation(title, year, data_source):
    return ('INSERT INTO Collaborations2 (title, year, data_source) VALUES (%s, %s, %s)',
            (title, year, data_source))


def insert_collaborations_operation_with_type(title, year, data_source, type):
    return ('INSERT INTO Collaborations2 (title, year, data_source, type) VALUES (%s, %s, %s, %s)',
            (title, year, data_source, type))


def insert_researchers_operation_short(first_name, middle_name, last_name, institution, ms_id,
                                       hired_year, cal_poly_position, education):
    if middle_name is None:
        return ('INSERT INTO Researchers2' +
                '(first_name, last_name, institution, ms_id, hired_year, cal_poly_position, education)' +
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (first_name, last_name, institution, ms_id, hired_year, cal_poly_position, education))
    else:
        return ('INSERT INTO Researchers2' +
                '(first_name, middle_name, last_name, institution, ms_id, hired_year, cal_poly_position, education)' +
                ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (first_name, middle_name, last_name, institution, ms_id, hired_year, cal_poly_position, education))


def insert_researchers_operation(first_name, middle_name, last_name, department, institution, ms_id, hired_year,
                                 cal_poly_position, education):
    return ('INSERT INTO Researchers2' +
            '(first_name, middle_name, last_name, department, institution, ms_id, hired_year,' +
            'cal_poly_position, education)' +
            ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (first_name, middle_name, last_name, department, institution, ms_id,
             hired_year, cal_poly_position, education))


def insert_researchers_operation_minimum(first_name, last_name):
    return ('INSERT INTO Researchers2' +
            '(first_name, last_name)' +
            ' VALUES (%s, %s)',
            (first_name, last_name))


def insert_authors_operation(cid, rid):
    return ('INSERT INTO Authors2 (cid, rid) VALUES (%s, %s)',
            (cid, rid))


def select_all_from_table(table_name, cursor):
    try:
        cursor.execute('SELECT * FROM ' + table_name)
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print('Unable to execute select operation for table ({0}): {1}'.format(table_name, error))
        raise Exception('MySQL operations could not be executed')


def select_collaborations_from_department(department_name, cursor):
    try:
        cursor.execute('SELECT cpcollabnet2019.Researchers2.first_name, ' +
                       'cpcollabnet2019.Researchers2.last_name, title FROM (cpcollabnet2019.Researchers2 RIGHT JOIN ' +
                       'cpcollabnet2019.Authors2 ON cpcollabnet2019.Researchers2.rid = cpcollabnet2019.Authors2.rid) ' +
                       'LEFT JOIN cpcollabnet2019.Collaborations2 ON cpcollabnet2019.Authors2.cid = ' +
                       'cpcollabnet2019.Collaborations2.cid WHERE cpcollabnet2019.Researchers2.department = "{0}"'
                       .format(department_name))
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print('Unable to execute select operation for department ({0}): {1}'.format(department_name, error))
        raise Exception('MySQL operations could not be executed')


def find_rid_by_name(first_name, last_name, cursor):
    try:
        cursor.execute('SELECT rid FROM cpcollabnet2019.Researchers2 WHERE ' +
                       'first_name = "' + first_name + '" AND last_name = "' + last_name + '"')
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print('Unable to execute select operation for researcher ({0} {1}): {2}'.format(first_name, last_name, error))
        raise Exception('MySQL operations could not be executed')


def delete_collaboration(cid, cursor, connection):
    try:
        cursor.execute('DELETE FROM cpcollabnet2019.Authors2 WHERE cid={}'.format(cid))
        cursor.execute('DELETE FROM cpcollabnet2019.Collaborations2 WHERE cid={}'.format(cid))
        connection.commit()
    except mysql.connector.Error as error:
        print('Unable to delete collaboration with cid {0}: {1}'.format(cid, error))
        raise Exception('MySQL operations could not be executed')


def execute_insert_operation(operation_param_tuple, cursor, connection, commit=True):
    try:
        cursor.execute(operation_param_tuple[0], operation_param_tuple[1])
        if commit:
            connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error as error:
        print('Unable to execute operations: {}'.format(error))
        print('Rolling back executed operations')
        connection.rollback()
        raise Exception('MySQL operations could not be executed')


def execute_select_operation(operation_param_tuple, cursor):
    try:
        cursor.execute(operation_param_tuple[0], operation_param_tuple[1])
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print('Unable to execute select operation: {}'.format(error))
        raise Exception('MySQL operations could not be executed')


def upload_dfs(collaborations_df, researchers_df, authors_df, cursor, connection):
    temp_to_rid = {}
    temp_to_cid = {}
    for index, researcher in researchers_df.iterrows():
        insert_researcher_op = insert_researchers_operation(
            researcher['first_name'],
            researcher['middle_name'],
            researcher['last_name'],
            researcher['department'],
            researcher['institution'],
            researcher['ms_id'],
            researcher['hired_year'],
            researcher['cal_poly_position'],
            researcher['education'])
        actual_rid = execute_insert_operation(insert_researcher_op, cursor, connection)
        temp_to_rid[researcher['rid_temp']] = actual_rid
    for index, collaboration in collaborations_df.iterrows():
        insert_collaboration_op = insert_collaborations_operation(
            collaboration['title'],
            collaboration['year'],
            collaboration['data_source'])
        actual_cid = execute_insert_operation(insert_collaboration_op, cursor, connection)
        temp_to_cid[collaboration['cid_temp']] = actual_cid
    author_tuples = set()
    for index, author in authors_df.iterrows():
        author_tuples.add((temp_to_cid[author['cid_temp']],
                           temp_to_rid[author['rid_temp']]))
    for t in author_tuples:
        insert_author_op = insert_authors_operation(t[0], t[1])
        execute_insert_operation(insert_author_op, cursor, connection)
