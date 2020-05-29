import statistics
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from collaboration_graph import *
from db_writer import *

# Men tend to have more co-authors

warnings.simplefilter(action='ignore', category=FutureWarning)

cnx, cur = init_connection_with_json('./login.json')

raw_authors = select_all_from_table('Authors2', cur)
authors_df = pd.DataFrame(raw_authors, columns=['cid', 'rid', 'created_at', 'updated_at'])

raw_researchers = select_all_from_table('Researchers2', cur)
researchers_df = pd.DataFrame(raw_researchers, columns=['rid', 'department', 'institution', 'created_at', 'updated_at',
                                                        'first_name', 'middle_name', 'last_name', 'ms_id', 'hired_year',
                                                        'cal_poly_position', 'education', 'gender', 'gender_accuracy'])

raw_collaborations = select_all_from_table('Collaborations2', cur)
collaborations_df = pd.DataFrame(raw_collaborations, columns=['cid', 'title', 'year', 'created_at', 'update_at',
                                                              'data_source', 'type'])

close_connection(cnx, cur)

bio_rids = researchers_df[researchers_df['department'] == 'biology']['rid']
math_rids = researchers_df[researchers_df['department'] == 'math']['rid']
cs_rids = researchers_df[researchers_df['department'].isin(['computer science', 'computer science, electrical '
                                                                                'engineering'])]['rid']
ee_rids = researchers_df[researchers_df['department'].isin(['electrical engineering', 'computer science, electrical '
                                                                                      'engineering'])]['rid']


def get_rid_to_collaborators(rids):
    rid_cids_df = pd.DataFrame(authors_df[authors_df['rid'].isin(rids)]
                               .groupby('rid')['cid'].agg(lambda cids: set(cids)))
    rid_to_collaborators = dict()
    for rid, row in rid_cids_df.iterrows():
        collaborators = list(filter(lambda crid: crid != rid,
                                    [x for y in map(lambda c: (authors_df[authors_df['cid'] == c]['rid'].tolist()),
                                                    row['cid']) for x in y]))
        rid_to_collaborators[rid] = collaborators
    return rid_to_collaborators


def get_gender(rid):
    return researchers_df[researchers_df['rid'] == rid].iloc[0]['gender']


def claim_1():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(bio_m).values())))
    bio_f_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(bio_f).values())))
    cs_m_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(cs_m).values())))
    cs_f_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(cs_f).values())))
    ee_m_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(ee_m).values())))
    ee_f_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(ee_f).values())))
    math_m_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(math_m).values())))
    math_f_count = statistics.mean(list(map(lambda cids: len(set(cids)), get_rid_to_collaborators(math_f).values())))

    print('Means:')
    print('Bio: {0}, {1}'.format(bio_m_count, bio_f_count))
    print('CS: {0}, {1}'.format(cs_m_count, cs_f_count))
    print('EE: {0}, {1}'.format(ee_m_count, ee_f_count))
    print('Math: {0}, {1}'.format(math_m_count, math_f_count))

    print('Percent Differences:')
    print('Bio: {0}'.format((bio_m_count - bio_f_count) / bio_m_count))
    print('CS: {0}'.format((cs_m_count - cs_f_count) / cs_m_count))
    print('EE: {0}'.format((ee_m_count - ee_f_count) / ee_m_count))
    print('Math: {0}'.format((math_m_count - math_f_count) / math_m_count))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [bio_m_count, cs_m_count, ee_m_count, math_m_count]
    f_avgs = [bio_f_count, cs_f_count, ee_f_count, math_f_count]

    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Average number of collaborators')
    plt.title('Average Number of Collaborators by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim1.jpg')


def get_num_repeats(rid_list):
    return sum(map(lambda rid: rid_list.count(rid) - 1, set(rid_list)))


def claim_2():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_count = statistics.mean(
        list(map(lambda cids: get_num_repeats(cids), get_rid_to_collaborators(bio_m).values())))
    bio_f_count = statistics.mean(
        list(map(lambda cids: get_num_repeats(cids), get_rid_to_collaborators(bio_f).values())))
    cs_m_count = statistics.mean(list(map(lambda cids: get_num_repeats(cids), get_rid_to_collaborators(cs_m).values())))
    cs_f_count = statistics.mean(list(map(lambda cids: get_num_repeats(cids), get_rid_to_collaborators(cs_f).values())))
    ee_m_count = statistics.mean(list(map(lambda cids: get_num_repeats(cids), get_rid_to_collaborators(ee_m).values())))
    ee_f_count = statistics.mean(list(map(lambda cids: get_num_repeats(cids), get_rid_to_collaborators(ee_f).values())))
    math_m_count = statistics.mean(list(map(lambda cids: get_num_repeats(cids),
                                            get_rid_to_collaborators(math_m).values())))
    math_f_count = statistics.mean(list(map(lambda cids: get_num_repeats(cids),
                                            get_rid_to_collaborators(math_f).values())))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [bio_m_count, cs_m_count, ee_m_count, math_m_count]
    f_avgs = [bio_f_count, cs_f_count, ee_f_count, math_f_count]

    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Average number of repeat collaborations')
    plt.title('Average Number of Repeat Collaborations by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim2.jpg')


def claim_3():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    G = CollaborationGraph()

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [
        G.avg_clustering_coefficient_by_rid(bio_m),
        G.avg_clustering_coefficient_by_rid(cs_m),
        G.avg_clustering_coefficient_by_rid(ee_m),
        G.avg_clustering_coefficient_by_rid(math_m)
    ]
    f_avgs = [
        G.avg_clustering_coefficient_by_rid(bio_f),
        G.avg_clustering_coefficient_by_rid(cs_f),
        G.avg_clustering_coefficient_by_rid(ee_f),
        G.avg_clustering_coefficient_by_rid(math_f)
    ]

    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Average local clustering coefficient')
    plt.title('Average Local Clustering Coefficient by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim3.jpg')


def get_gender_to_gender_ratio(rids, female_to_male):
    female_count = 0
    male_count = 0
    for rid in rids:
        gender = get_gender(rid)
        if gender == 'male':
            male_count = male_count + 1
        elif gender == 'female':
            female_count = female_count + 1
    print('{0} : {1}'.format(female_count, male_count))
    if female_to_male:
        if male_count == 0:
            return 1.0
        else:
            return female_count / male_count
    else:
        if female_count == 0:
            return 1.0
        else:
            return male_count / female_count


def wgr(rids):
    female_count = 0
    for rid in rids:
        gender = get_gender(rid)
        if gender == 'female':
            female_count = female_count + 1
    if len(rids) == 0:
        return 1.0
    else:
        return female_count / len(rids)


def claim_4_1():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(bio_m).values())))
    bio_f_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(bio_f).values())))
    cs_m_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(cs_m).values())))
    cs_f_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(cs_f).values())))
    ee_m_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(ee_m).values())))
    ee_f_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(ee_f).values())))
    math_m_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(math_m).values())))
    math_f_count = statistics.mean(list(map(wgr, get_rid_to_collaborators(math_f).values())))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [bio_m_count, cs_m_count, ee_m_count, math_m_count]
    f_avgs = [bio_f_count, cs_f_count, ee_f_count, math_f_count]
    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Average WGR')
    plt.title('Weightless g-ratio by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/wgr.jpg')


def claim_4():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, False),
                                           get_rid_to_collaborators(bio_m).values())))
    bio_f_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, True),
                                           get_rid_to_collaborators(bio_f).values())))
    cs_m_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, False),
                                          get_rid_to_collaborators(cs_m).values())))
    cs_f_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, True),
                                          get_rid_to_collaborators(cs_f).values())))
    ee_m_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, False),
                                          get_rid_to_collaborators(ee_m).values())))
    ee_f_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, True),
                                          get_rid_to_collaborators(ee_f).values())))
    math_m_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, False),
                                            get_rid_to_collaborators(math_m).values())))
    math_f_count = statistics.mean(list(map(lambda rids: get_gender_to_gender_ratio(rids, True),
                                            get_rid_to_collaborators(math_f).values())))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [bio_m_count, cs_m_count, ee_m_count, math_m_count]
    f_avgs = [bio_f_count, cs_f_count, ee_f_count, math_f_count]
    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Same gender collaborator ratio')
    plt.title('Same Gender Collaborator Ratio by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim4.jpg')


def get_publications_list(rid):
    return set(authors_df[authors_df['rid'] == rid]['cid'].unique())


def get_publication_year(cid):
    year = collaborations_df[collaborations_df['cid'] == cid].iloc[0]['year']
    return year


def claim_5():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 bio_m)))
    bio_f_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 bio_f)))
    cs_m_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 cs_m)))
    cs_f_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 cs_f)))
    ee_m_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 ee_m)))
    ee_f_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 ee_f)))
    math_m_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 math_m)))
    math_f_first = statistics.mean(
        list(map(lambda rid: 2020 - min(set(map(get_publication_year, get_publications_list(rid)))),
                 math_f)))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [bio_m_first, cs_m_first, ee_m_first, math_m_first]
    f_avgs = [bio_f_first, cs_f_first, ee_f_first, math_f_first]
    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Average publication history length (years)')
    plt.title('Average Publication History Length by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim5.jpg')


def claim_6():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), bio_m)))
    bio_f_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), bio_f)))
    cs_m_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), cs_m)))
    cs_f_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), cs_f)))
    ee_m_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), ee_m)))
    ee_f_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), ee_f)))
    math_m_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), math_m)))
    math_f_first = statistics.mean(list(map(lambda rid: len(get_publications_list(rid)), math_f)))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [bio_m_first, cs_m_first, ee_m_first, math_m_first]
    f_avgs = [bio_f_first, cs_f_first, ee_f_first, math_f_first]
    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Average number of publications')
    plt.title('Average Number of Publications by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim6.jpg')


def is_intramural(rid):
    return researchers_df[researchers_df['rid'] == rid].iloc[0]['institution'] == 'california polytechnic state ' \
                                                                                  'university'


def get_percent_true(bool_list):
    if len(bool_list) == 0:
        return 0.0
    else:
        return sum(bool_list) / len(bool_list)


def claim_7():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                           get_rid_to_collaborators(bio_m).values())))
    bio_f_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                           get_rid_to_collaborators(bio_f).values())))
    cs_m_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                          get_rid_to_collaborators(cs_m).values())))
    cs_f_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                          get_rid_to_collaborators(cs_f).values())))
    ee_m_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                          get_rid_to_collaborators(ee_m).values())))
    ee_f_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                          get_rid_to_collaborators(ee_f).values())))
    math_m_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                            get_rid_to_collaborators(math_m).values())))
    math_f_count = statistics.mean(list(map(lambda rids: get_percent_true(list(map(is_intramural, rids))),
                                            get_rid_to_collaborators(math_f).values())))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    m_avgs = [bio_m_count, cs_m_count, ee_m_count, math_m_count]
    f_avgs = [bio_f_count, cs_f_count, ee_f_count, math_f_count]
    plt.bar(ind, m_avgs, width, label="Men")
    plt.bar(ind + width, f_avgs, width, label='Women')

    plt.ylabel('Percentage of intramural collaborations')
    plt.title('Percentage of Intramural Collaborations by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim7.jpg')


def get_all_publications(rids):
    return set(authors_df[authors_df['rid'].isin(rids)]['cid'].unique())


def map_year_to_publications(cids):
    year_to_cids = dict()
    for cid in cids:
        year = collaborations_df[collaborations_df['cid'] == cid].iloc[0]['year']
        if year in year_to_cids.keys():
            year_to_cids[year].append(cid)
        else:
            year_to_cids[year] = [cid]
    return year_to_cids


def cid_contains_woman_author(cid, woman_seed=False):
    rids = set(authors_df[authors_df['cid'] == cid]['rid'].unique())
    collaborator_genders = researchers_df[researchers_df['rid'].isin(rids)]['gender'].tolist()
    if woman_seed:
        return collaborator_genders.count('female') > 1
    else:
        return 'female' in collaborator_genders


def get_line(x, y):
    x_np = np.array(list(x))
    y_np = np.array(list(y))
    slope, intercept = np.polyfit(x_np, y_np, 1)
    return x_np, (slope * x_np) + intercept


def claim_8():
    bio_m = list(filter(lambda rid: get_gender(rid) == 'male', bio_rids))
    bio_f = list(filter(lambda rid: get_gender(rid) == 'female', bio_rids))
    cs_m = list(filter(lambda rid: get_gender(rid) == 'male', cs_rids))
    cs_f = list(filter(lambda rid: get_gender(rid) == 'female', cs_rids))
    ee_m = list(filter(lambda rid: get_gender(rid) == 'male', ee_rids))
    ee_f = list(filter(lambda rid: get_gender(rid) == 'female', ee_rids))
    math_m = list(filter(lambda rid: get_gender(rid) == 'male', math_rids))
    math_f = list(filter(lambda rid: get_gender(rid) == 'female', math_rids))

    bio_m_map = {year: sum(map(cid_contains_woman_author, cids)) / len(cids) for year, cids in
                 map_year_to_publications(get_all_publications(bio_m)).items()}
    bio_f_map = {year: sum(map(lambda cid: cid_contains_woman_author(cid, True), cids)) / len(cids) for year, cids in
                 map_year_to_publications(get_all_publications(bio_f)).items()}
    cs_m_map = {year: sum(map(cid_contains_woman_author, cids)) / len(cids) for year, cids in
                map_year_to_publications(get_all_publications(cs_m)).items()}
    cs_f_map = {year: sum(map(lambda cid: cid_contains_woman_author(cid, True), cids)) / len(cids) for year, cids in
                map_year_to_publications(get_all_publications(cs_f)).items()}
    ee_m_map = {year: sum(map(cid_contains_woman_author, cids)) / len(cids) for year, cids in
                map_year_to_publications(get_all_publications(ee_m)).items()}
    ee_f_map = {year: sum(map(lambda cid: cid_contains_woman_author(cid, True), cids)) / len(cids) for year, cids in
                map_year_to_publications(get_all_publications(ee_f)).items()}
    math_m_map = {year: sum(map(cid_contains_woman_author, cids)) / len(cids) for year, cids in
                  map_year_to_publications(get_all_publications(math_m)).items()}
    math_f_map = {year: sum(map(lambda cid: cid_contains_woman_author(cid, True), cids)) / len(cids) for year, cids in
                  map_year_to_publications(get_all_publications(math_f)).items()}

    bio_m_lin = get_line(bio_m_map.keys(), bio_m_map.values())
    bio_f_lin = get_line(bio_f_map.keys(), bio_f_map.values())
    cs_m_lin = get_line(cs_m_map.keys(), cs_m_map.values())
    cs_f_lin = get_line(cs_f_map.keys(), cs_f_map.values())
    ee_m_lin = get_line(ee_m_map.keys(), ee_m_map.values())
    ee_f_lin = get_line(ee_f_map.keys(), ee_f_map.values())
    math_m_lin = get_line(math_m_map.keys(), math_m_map.values())
    math_f_lin = get_line(math_f_map.keys(), math_f_map.values())

    fig, ax = plt.subplots(4, 1, sharex=True, sharey=True)

    plt.subplots_adjust(hspace=0.5)

    ax[0].scatter(bio_m_map.keys(), bio_m_map.values(), c='#0000FF', s=3)
    ax[0].scatter(bio_f_map.keys(), bio_f_map.values(), c='#FF0000', s=3)
    ax[0].plot(bio_m_lin[0], bio_m_lin[1], c='#0000FF', linewidth=0.75)
    ax[0].plot(bio_f_lin[0], bio_f_lin[1], c='#FF0000', linewidth=0.75)
    ax[0].set_title('Biology')

    ax[1].scatter(cs_m_map.keys(), cs_m_map.values(), c='#0000FF', s=3)
    ax[1].scatter(cs_f_map.keys(), cs_f_map.values(), c='#FF0000', s=3)
    ax[1].plot(cs_m_lin[0], cs_m_lin[1], c='#0000FF', linewidth=0.75)
    ax[1].plot(cs_f_lin[0], cs_f_lin[1], c='#FF0000', linewidth=0.75)
    ax[1].set_title('Computer Science')

    ax[2].scatter(ee_m_map.keys(), ee_m_map.values(), c='#0000FF', s=3)
    ax[2].scatter(ee_f_map.keys(), ee_f_map.values(), c='#FF0000', s=3)
    ax[2].plot(ee_m_lin[0], ee_m_lin[1], c='#0000FF', linewidth=0.75)
    ax[2].plot(ee_f_lin[0], ee_f_lin[1], c='#FF0000', linewidth=0.75)
    ax[2].set_title('Electrical Engineering')

    ax[3].scatter(math_m_map.keys(), math_m_map.values(), c='#0000FF', s=3)
    ax[3].scatter(math_f_map.keys(), math_f_map.values(), c='#FF0000', s=3)
    ax[3].plot(math_m_lin[0], math_m_lin[1], c='#0000FF', linewidth=0.75)
    ax[3].plot(math_f_lin[0], math_f_lin[1], c='#FF0000', linewidth=0.75)
    ax[3].set_title('Math')

    fig.suptitle('Percentage of Publications with a Woman Collaborator', fontsize=11)

    fig.legend(['Men', 'Women'])

    plt.savefig('./data/claim8.jpg')


def get_collaborations_by_number_of_authors(rids):
    few_authors = list()
    many_authors = list()
    for rid in rids:
        publications = get_publications_list(rid)
        gender = get_gender(rid)
        for cid in publications:
            if len(authors_df[authors_df['cid'] == cid].index) > 3:
                many_authors.append((gender, cid))
            else:
                few_authors.append((gender, cid))
    return few_authors, many_authors


def homophily_score(gender, cid):
    authors = set(authors_df[authors_df['cid'] == cid]['rid'].unique())
    genders = list(map(get_gender, authors))
    f_count = genders.count('female')
    m_count = genders.count('male')
    if gender == 'female':
        if m_count == 0:
            return 1.0
        else:
            return (f_count - 1) / m_count
    else:
        if f_count == 0:
            return 1.0
        else:
            return (m_count - 1) / f_count


def claim_9():
    bio_few, bio_many = get_collaborations_by_number_of_authors(bio_rids)
    cs_few, cs_many = get_collaborations_by_number_of_authors(cs_rids)
    ee_few, ee_many = get_collaborations_by_number_of_authors(ee_rids)
    math_few, math_many = get_collaborations_by_number_of_authors(math_rids)

    bio_few_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), bio_few)))
    bio_many_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), bio_many)))
    cs_few_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), cs_few)))
    cs_many_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), cs_many)))
    ee_few_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), ee_few)))
    ee_many_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), ee_many)))
    math_few_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), math_few)))
    math_many_count = statistics.mean(list(map(lambda t: homophily_score(t[0], t[1]), math_many)))

    ind = np.arange(4)
    width = 0.35
    department = ('Biology', 'Computer Science', 'Electrical Engineering', 'Math')

    few_avgs = [bio_few_count, cs_few_count, ee_few_count, math_few_count]
    many_avgs = [bio_many_count, cs_many_count, ee_many_count, math_many_count]
    plt.bar(ind, few_avgs, width, label="Few Collaborators")
    plt.bar(ind + width, many_avgs, width, label='Many Collaborators')

    plt.ylabel('Same gender collaborator ratio')
    plt.title('Same Gender Collaborator Ratio by Department')
    plt.xticks(ind + width / 2, department, rotation=40)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('./data/claim9.jpg')


claim_4_1()
