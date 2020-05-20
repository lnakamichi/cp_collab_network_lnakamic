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


claim_6()
