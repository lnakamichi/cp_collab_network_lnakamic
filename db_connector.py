import mysql.connector
import pickle
import json
from nameparser import HumanName

# taken from initial study

HOST = "cpcollabnetwork8.cn244vkxrxzn.us-west-1.rds.amazonaws.com"
DB = 'cpcollabnet2019'

def init_connection_with_json(filename: str, db=DB, host=HOST):
    """
    expects a .json file with a dictionary with "user" and "password"
    """
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


def insert_institution(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    TODO: Return the iid
    """

    return insert_general(cnx, cursor, record, "Institution", postpone_commit=postpone_commit)
    # try:
    #     iid = general_query(cnx, cursor, ["iid"],
    #                     "domain='" + record["domain"] + "' or " + "name= '" + record["name"][:50] + "'", "Institution")[0][0]
    # except KeyError:
    #     iid = general_query(cnx, cursor, ["iid"], "name= '" + record["name"][:50] + "'", "Institution")[0][0]
    # return iid


def insert_researcher(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Returns rid of new researcher
    """
    if "'" in record['name']:
        record['name'] = record['name'].split("'")
        record['name'] = " ".join(record['name'])
    return insert_general(cnx, cursor, record, "Researcher", postpone_commit=postpone_commit)


def insert_email(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Inserts new email into email list
    TODO: Return something?
    """
    insert_general(cnx, cursor, record, "Email", postpone_commit=postpone_commit)


def insert_department(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Returns did of new Department
    """
    insert_general(cnx, cursor, record, "Department", postpone_commit=postpone_commit)
    print(record["dept_name"])
    did = general_query(cnx, cursor, ["did"],
                        "dept_name='" + record["dept_name"][:50] + "'", "Department")[0][0]
    return did


def insert_employment(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Returns emid of new Employment
    """
    insert_general(cnx, cursor, record, "Employment", postpone_commit=postpone_commit)
    emid = general_query(cnx, cursor, ["emid"],
                         "rid='" + str(record["rid"]) + "' and " + "did='" + str(record["did"]) + "'",
                         "Employment")[0][0]
    return emid


def insert_collaboration(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Returns cid of new Collaboration
    """
    if "'" in record['title']:
        record['title'] = record['title'].split("'")
        record['title'] = " ".join(record['title'])
    if '"' in record['title']:
        record['title'] = record['title'].split('"')
        record['title'] = " ".join(record['title'])
    return insert_general(cnx, cursor, record, "Collaboration", postpone_commit=postpone_commit)
    # cid = general_query(cnx, cursor, ["cid"],
    #                     "title='" + record["title"][:100] + "'", "Collaboration")[0][0]
    # return cid


def insert_education(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Returns emid of new Employment
    """
    insert_general(cnx, cursor, record, "Education", postpone_commit=postpone_commit)
    edid = general_query(cnx, cursor, ["edid"],
                         "rid='" + str(record["rid"]) + "' and " + "iid='" + str(record["iid"]) + "'", "Education")[0][0]
    return edid


def insert_author(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Returns cid of new Collaboration
    TODO: Return something?
    """
    insert_general(cnx, cursor, record, "Author", postpone_commit=postpone_commit)
    # aid = general_query(cnx, cursor, ["cid"],
    #                     "title='" + record["title"] + "'", "Collaboration")[0][0]
    # return cid


def insert_interest(cnx, cursor, record: dict, *, postpone_commit=False):
    """
    Returns inid of new Interest
    """
    insert_general(cnx, cursor, record, "Interest", postpone_commit=postpone_commit)
    # inid = general_query(cnx, cursor, ["inid"],
    #                      "rid='" + str(record["rid"]) + "' and " + "interest='" + record["interest"] + "'", "Interest")[0][0]
    # return inid


def insert_general(cnx, cursor, record: dict, table_name: str, *, postpone_commit=False):
    """
    Generalized version of insert.
    :param cnx
    :param cursor
    :param record dictionary with keys as columns
    :param table_name that is being inserted into
    :param postpone_commit optional
    Performs cnx.commit
    """
    insert_string = "INSERT INTO " + table_name
    column_values = "("
    val_values = "VALUES ("
    for col_val in record.keys():
        column_values = column_values + col_val + ", "
        val_values = val_values + "%(" + col_val + ")s, "

    column_values = column_values.rstrip(" ")
    column_values = column_values.rstrip(",")
    column_values += ")"

    val_values = val_values.rstrip(" ")
    val_values = val_values.rstrip(",")
    val_values += ")"

    final = " ".join([insert_string, column_values, val_values])

    cursor.execute(final, record)

    if not postpone_commit:
        # Make sure data is committed to the database
        cnx.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    return cursor.fetchone()[0]


def update_general(cnx, cursor, update_record: dict, where_cond: str, table_name: str, *, postpone_commit = False):

    update_string = "UPDATE " + table_name
    set_string = "SET "
    for key in update_record.keys():
        set_string += key + "='" + str(update_record[key]) + "', "
    where_string = "WHERE " + where_cond

    set_string = set_string.rstrip(" ")
    set_string = set_string.rstrip(",")

    final = " ".join([update_string, set_string, where_string])
    cursor.execute(final, update_record)

    if not postpone_commit:
        # Make sure data is committed to the database
        cnx.commit()


def update_researcher(cnx, cursor, record: dict, update_record):
    try:
        update_general(cnx, cursor, update_record, "rid="+str(record['rid']), "Researcher")
    except KeyError:
        try:
            update_general(cnx, cursor, update_record, "name = '" + record['name'] + "'", "Researcher")
        except KeyError:
            return False


def update_employment(cnx, cursor, record: dict, update_record):
    try:
        # update_general(cnx, cursor, update_record, "rid="+str(record['rid']), "Employment")
        final = "UPDATE Employment SET start_date = makedate(" + update_record['start_date'] + ", 1) WHERE rid = "+str(record['rid'])
        cursor.execute(final)
        cnx.commit()
    except KeyError:
        return False


def update_author(cnx, cursor, record, update_record):
    update_general(cnx, cursor, update_record, 'cid=%d and rid=%d' %
                   (record['cid'], record['rid']), 'Author')


def update_institution(cnx, cursor, record: dict, update_record):
    try:
        update_general(cnx, cursor, update_record, "iid="+str(record['iid']), "Institution")
    except KeyError:
        try:
            update_general(cnx, cursor, update_record, "name = '" + record['name'][:50] + "'", "Institution")
        except KeyError:
            try:
                update_general(cnx, cursor, update_record, "domain = '" + record['domain'][:50] + "'", "Institution")
            except KeyError:
                return False


def general_query(cnx, cursor, select_attr, where_cond, table_name):
    select_string = "SELECT " + ','.join(select_attr)
    from_string = "FROM " + table_name
    where_string = "WHERE " + where_cond
    final = " ".join([select_string, from_string, where_string])
    cursor.execute(final)
    return [entry for entry in cursor]


def institution_exists(cnx, cursor, record: dict):
    """
    :param cnx:
    :param cursor:
    :param record: Make sure record contains domain or institution name. Name is primary key
    :return: iid or False
    """
    conditions = []

    for key in ('microsoft_id', 'domain', 'name'):
        value = record.get(key, None)
        if value is not None and len(value) > 0:
            if key == 'name':
                key = key.replace("'", ' ').replace('"', ' ')
            conditions.append('%s="%s"' % (key, value))

    entries = general_query(cnx, cursor, ['iid', 'name'],
                            ' OR '.join(conditions), 'Institution')
    try:
        return entries[0][0]
    except IndexError:
        return False


def department_exists(cnx, cursor, record: dict):
    """
    :param cnx:
    :param cursor:
    :param record: Make sure record contains dept_name or college_name. dept_name is primary key
    :return: iid or False
    """
    try:
        dept_name = record['dept_name']
        if dept_name is "":
            dept_name = None
    except KeyError:
        dept_name = None

    try:
        college_name = record['college_name']
        if college_name is "":
            college_name = None
    except KeyError:
        college_name = None

    if college_name is not None or dept_name is not None:
        if dept_name is not None:
            try:
                did = general_query(cnx, cursor, ["did"],
                                    "dept_name='" + record["dept_name"] + "'", "Department")[0][0]
            except IndexError:
                did = False
        else:
            try:
                did = general_query(cnx, cursor, ["did"],
                                "college_name='" + record["college_name"] + "'", "Department")[0][0]
            except IndexError:
                did = False
        if did is "":
            return False
    else:
        did = False

    return did


def employment_exists(cnx, cursor, record):
    condition = ' AND '.join(["%s='%s'" % (key, str(value))
                              for key, value in record.items()])
    entries = general_query(cnx, cursor, ['emid'], condition,
                            'Employment')
    if len(entries) > 0:
        return entries[0][0]
    return False


def collaboration_exists(cnx, cursor, record: dict):
    """
    :param cnx:
    :param cursor:
    :param record: Make sure record contains title. title is primary key
    :return: cid or False
    """
    try:
        title = record['title']
        if title is "":
            title = None
    except KeyError:
        title = None

    if title is not None:
        try:
            if "'" in record['title']:
                record['title'] = record['title'].split("'")
                record['title'] = " ".join(record['title'])
            if '"' in record['title']:
                record['title'] = record['title'].split('"')
                record['title'] = " ".join(record['title'])
            cid = general_query(cnx, cursor, ["cid"],
                                "title='" + record["title"] + "'", "Collaboration")[0][0]
        except IndexError:
            cid = False
        if cid is "":
            return False
    else:
        cid = False

    return cid

def email_exists(cnx, cursor, record: dict):
    """
    :param cnx:
    :param cursor:
    :param record: Make sure record contains rid. rid is primary key
    :return: cid or False
    """
    try:
        rid = record['rid']
        if rid is "":
            rid = None
    except KeyError:
        rid = None
    try:
        name = record['email']
        if name is "":
            name = None
    except KeyError:
        name = None

    if rid is not None:
        try:
            email = general_query(cnx, cursor, ["email"],
                                "rid='" + record["rid"] + "'", "Email")[0][0]
        except IndexError:
            email = False
        if email is "":
            return False
    else:
        email = False

    if name is not None:
        try:
            email = general_query(cnx, cursor, ["email"],
                                "email='" + record["email"] + "'", "Email")[0][0]
        except IndexError:
            email = False
        if email is "":
            return False
    else:
        email = False

    return email


def education_exists(cnx, cursor, record: dict):
    """
    :param cnx:
    :param cursor:
    :param record: Make sure record contains rid and iid. dept_name is primary key
    :return: edid or False
    """
    try:
        rid = record['rid']
        if rid is "":
            rid = None
    except KeyError:
        rid = None

    try:
        iid = record['iid']
        if iid is "":
            iid = None
    except KeyError:
        iid = None

    if rid is not None and iid is not None:
        try:
            edid = general_query(cnx, cursor, ["edid"],
                                 "rid='" + record["rid"] + "' and " + "iid='" + record["iid"] + "'", "Education")[0][0]
        except IndexError:
            edid = False
        if edid is "":
            return False
    else:
        edid = False

    return edid


def author_exists(cnx, cursor, record: dict):
    cid = record['cid']
    rid = record['rid']
    if cid is None or rid is None:
        raise ValueError('cid and rid must not be None')
    try:
        key = general_query(cnx, cursor, ['cid', 'rid'],
                            "cid='%d' and rid='%d'" % (cid, rid), 'Author')
    except IndexError:
        return False
    return len(key) != 0


multiple_matches_memory = {}
def researcher_exists(cnx, cursor, record, cp_rids=None):
    """
    :param cnx:
    :param cursor:
    :param record: Make sure record contains name and maybe alt_name. name is primary key
    :return: rid or False
    """
    for key in ('scholar_id', 'microsoft_id'):
        id = record.get('scholar_id', None)
        if id is not None and len(id) > 0:
            rid = researcher_exists_with_id(cnx, cursor, key, id)
            if rid:
                return rid

    names = []
    for key in ('name', 'name_alt'):
        try:
            name = record[key]
            if name:
                names.append(name)
        except KeyError:
            pass

    or_conditions = []
    for name in names:
        name = name.replace("'", "")
        hn = HumanName(name)
        for key in ('name', 'name_alt'):
            or_conditions.append("%s LIKE '%s%%%s'" %
                                 (key, hn.first[0] if hn.first else "",
                                 hn.last))

    condition = '(%s)' % (' OR '.join(or_conditions))
    if cp_rids is not None:
        condition += ' AND rid IN (%s)' % (','.join(str(rid) for rid in
                                           cp_rids))
    entries = general_query(cnx, cursor, ['name', 'name_alt', 'rid'],
                            condition, 'Researcher')

    matching_entries = []
    for entry in entries:
        if entry[0] in names or entry[1] in names:
            matching_entries.append(entry)
            continue
        for name in names:
            if (entry not in matching_entries and
                (compare_names(name, entry[0], False) or
                 compare_names(name, entry[1], False))):
                matching_entries.append(entry)
        if entry not in matching_entries:
            for name in names:
                if (entry not in matching_entries and
                    (compare_names(name, entry[0]) or
                     compare_names(name, entry[1]))):
                    matching_entries.append(entry)

    if len(matching_entries) > 1:
        lowered_names = [name.lower() for name in names]
        exact_matches = [entry for entry in entries if entry[0].lower() in
                         lowered_names or (entry[1] is not None and
                                           entry[1].lower() in lowered_names)]
        if len(exact_matches) > 0:
            return exact_matches[0][2]

        rids = tuple(sorted(entry[2] for entry in matching_entries))
        try:
            return multiple_matches_memory[rids]
        except KeyError:
            pass
        print(names)
        for entry in matching_entries:
            if entry[0].lower() in names:
                return entry[1]
            print('name: %s\tname_alt: %s\trid: %d' % entry)
        choice = -2
        while choice not in rids:
            try:
                choice = int(input('Multiple matches, enter rid of the '
                                   'correct one or -1 if none are correct: '))
            except ValueError:
                continue
            if choice == -1:
                choice = False
                break
        multiple_matches_memory[rids] = choice
        return choice
    try:
        return matching_entries[0][2]
    except IndexError:
        return False


def researcher_exists_with_id(cnx, cursor, key, id):
    entries = general_query(cnx, cursor, ['rid'], "%s='%s'" % (key, id),
                            'Researcher')
    try:
        return entries[0][0]
    except IndexError:
        return False


def institution_from_employment(cnx, cursor, rid):
    """
    Returns the iid of most recent employment based on rid
    """
    select_attribute = ['iid']
    table_name = "Employment"
    where_cond = "rid =" + str(rid)
    try:
        department = general_query(cnx, cursor, ['did'], where_cond, table_name)[0][0]
        institution = general_query(cnx, cursor, ['iid'], "did = " + str(department), "Department")[0][0]
        return institution
    except IndexError:
        return False


if __name__ == "__main__":
    cnx, cursor = init_connection_with_json('data/christian_cnx', "test")
    # iid = institution_exists(cnx, cursor, {
    #                              "name": "",
    #                              "domain": "@ucla.edu"
    #                          })
    # iid = insert_institution(cnx, cursor, {
    #     "name": "California Polytechnic State University",
    #     "city": "San Luis Obispo",
    #     "state": "California",
    #     "country": "United States",
    #     "domain": "calpoly.edu",
    #     "iid": "0"})
    update_institution(cnx, cursor, {"domain": "ucsc.edu"}, {"name": "University of California Santa Cruz"})
    # print(iid)
    # rid1 = insert_researcher(cnx, cursor, {
    #     "name": "Theresa Migler",
    # })

    # rid2 = insert_researcher(cnx, cursor, {
    #     "name": "Chris Lupo",
    # })
    #
    # rid3 = insert_researcher(cnx, cursor, {
    #     "name": "Sarah Bahrami",
    # })

    rid4 = researcher_exists(cnx, cursor, {"name": "S Bahrami"})
    print(rid4)

    # print(rid)
    # did = insert_department(cnx, cursor, {
    #     "dept_name": "University of California, Los Angeles",
    #     "iid": iid
    # })
    #
    # print(did)

    close_connection(cnx, cursor)


# def compare_names(hn1, hn2):
#     if hn1 is None or hn2 is None:
#         return False
#     if isinstance(hn1, str):
#         hn1 = HumanName(hn1)
#     if isinstance(hn2, str):
#         hn2 = HumanName(hn2)
#     if _compare_single_names(hn1.last, hn2.last):
#         if _compare_single_names(hn1.first, hn2.first):
#             if hn1.middle and hn2.middle:
#                 return _compare_middle_names(hn1.middle, hn2.middle)
#             return True
#         else:
#             return False
#     else:
#         return False
#
# def _compare_middle_names(name1, name2):
#     if len(name1) == 1 or len(name2) == 1:
#         return name1[0].lower() == name2[0].lower()
#     return _compare_single_names(name1, name2)
#
#
# def _compare_single_names(name1, name2):
#     return name1.replace('-', '').lower() == name2.replace('-', '').lower()

compare_names_memory = dict()
def compare_names(hn1, hn2, query_mode=True):
    if hn1 is None or hn2 is None:
        return False
    if isinstance(hn1, str):
        hn1 = HumanName(hn1)
    if isinstance(hn2, str):
        hn2 = HumanName(hn2)
    hn1.capitalize()
    hn2.capitalize()
    try:
        return compare_names_memory[(hn1.full_name), (hn2.full_name)]
    except KeyError:
        pass
    last_comp = _compare_last_names(hn1.last, hn2.last)
    if last_comp == 1:
        if _compare_first_names(hn1.first, hn2.first):
            result = True
        elif query_mode:
            result = query_input('Are %s and %s the same name?' %
                                 (hn1.full_name, hn2.full_name))
        else:
            return False
    elif last_comp == 0 and query_mode:
        result = query_input('Are %s and %s the same name?' %
                             (hn1.full_name, hn2.full_name))
    else:
        result = False
    compare_names_memory[(hn1.full_name, hn2.full_name)] = result
    compare_names_memory[(hn2.full_name, hn1.full_name)] = result
    return result


def _compare_first_names(first1, first2):
    if len(first2) < len(first1):
        first1, first2 = first2, first1
    return (first1.isupper() and first1[0] == first2[0] or
            first1.lower() == first2[:len(first1)].lower())


def _compare_last_names(last1, last2):
    set1 = set(last1.lower().split('-'))
    set2 = set(last2.lower().split('-'))
    if set1 == set2:
        return 1
    if not set1.isdisjoint(set2):
        return 0
    return -1


def query_input(question):
    match = ''
    while match not in ('y', 'n'):
        match = input(question + ' (y/n) ').strip().lower()
    return match == 'y'


def publication_exists_by_std_title(cnx, cursor, title):
    pattern = '^' + title.replace(' ', '[[:punct:],[:blank:]]+')
    query = 'SELECT cid FROM Collaboration WHERE title REGEXP "%s"' % (pattern)
    print(query)
    cursor.execute(query)
    entries = [entry for entry in cursor]
    if len(entries) == 0:
        return False
    if len(entries) > 1:
        cids = [x[0] for x in entries]
        print('Multiple matches: %s' % (' '.join(str(x[0]) for x in entries)))
        cid = -1
        while cid not in cids:
            try:
                cid = int(input('Select one: '))
            except ValueError:
                pass
    else:
        cid = entries[0][0]
    return cid


def merge_duplicate_researchers(cnx, cursor):
    query = ('SELECT name, rid, COUNT(*), GROUP_CONCAT(rid) FROM Researcher '
             'WHERE (name NOT LIKE "%?%" AND name <> "") GROUP BY name '
             'HAVING COUNT(*) > 1')
    cursor.execute(query)
    entries = [entry for entry in cursor]
    for entry in entries:
        print(entry)
        query = ('UPDATE Employment SET rid=%d WHERE rid IN (%s)' % (entry[1],
                                                                     entry[3]))
        cursor.execute(query)
        query = ('DELETE FROM Researcher WHERE rid IN (%s)' % (entry[3]))
        cursor.execute(query)
    cnx.commit()


    # entries = [['ha', 11986, 2, '11986,11987,11531,11544,13183,13184']]
    # for entry in entries:
    #     print(entry)
    #     for from_rid in entry[3].split(','):
    #         if int(from_rid) != entry[1]:
    #             query = ('SELECT cid, author_index, iid_1 FROM Author WHERE '
    #                      'rid=%s' % (from_rid))
    #             cursor.execute(query)
    #             cid_entries = [cid_entry for cid_entry in cursor]
    #             for cid_entry in cid_entries:
    #                 query = ('SELECT author_index, iid_1 FROM Author WHERE '
    #                          'rid=%d AND cid=%d' % (entry[1], cid_entry[0]))
    #                 cursor.execute(query)
    #                 duplicate = False
    #                 for a_entry in cursor:
    #                     duplicate = True
    #                     if cid_entry[1:] != a_entry:
    #                         better_author_index = (cid_entry[1] if cid_entry[1]
    #                                                is not None else a_entry[0])
    #                         better_iid = (cid_entry[2] if cid_entry[2] is not
    #                                       None else a_entry[1])
    #                         update_author(
    #                             cnx, cursor,
    #                             {'cid': cid_entry[1], 'rid':entry[1]},
    #                             {'author_index': better_author_index,
    #                              'iid_1': better_iid})
    #                     cursor.execute('DELETE FROM Author WHERE cid=%d AND '
    #                                    'rid=%s' % (cid_entry[0], from_rid))
    #                     cnx.commit()
    #                 if duplicate == False:
    #                    update_author(cnx, cursor, {'cid': cid_entry[0],
    #                                                'rid': int(from_rid)},
    #                                  {'rid': entry[1]})

def get_all_rids(cursor):
	'''The Researcher table does not have all rids. This should be a top priority when we have a chance to resubmit our research'''
	query_1 = ('SELECT rid FROM Researcher')
	cursor.execute(query_1)
	return set([entry[0] for entry in cursor])



def get_all_cp_rids(cursor):
    '''Logan added emails to the database of reserachers who were beyond 1687 and who had a cal poly email address'''
    query =('SELECT rid FROM cpcollabnet2019.Researcher Where rid < 1687 or rid in'
            '(Select rid From Email where email like "%calpoly%")')
    cursor.execute(query)
    return set([entry[0] for entry in cursor])

def get_all_ce_rids(cursor):
	query = ('SELECT rid FROM Employment WHERE did BETWEEN 1 and 10')
	cursor.execute(query)
	return set([entry[0] for entry in cursor])

def delete_general(cnx, cursor, table, condition):
    query = 'DELETE FROM %s WHERE %s' % (table, condition)
    print(query)
    cursor.execute(query)
    cnx.commit()
