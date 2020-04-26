import networkx as nx
import time

from db_writer import *
from pyvis.network import Network


MATH = 0
BIOLOGY = 1
COMPUTER_SCIENCE = 2
ELECTRICAL_ENGINEERING = 3


def generate_graph():
    cnx, cur = init_connection_with_json("./login.json")
    researchers = select_all_from_table('Researchers2', cur)
    collaborations = select_all_from_table('Collaborations2', cur)
    edges = select_collaborating_authors(cur)
    close_connection(cnx, cur)

    graph = nx.Graph()
    print('Adding researchers')
    for researcher_tuple in researchers:
        graph.add_node(researcher_tuple[0], department=researcher_tuple[1],
                       institution=researcher_tuple[2],
                       name=' '.join([researcher_tuple[5], researcher_tuple[7]]),
                       hired_year=researcher_tuple[9],
                       cal_poly_position=researcher_tuple[10],
                       education=researcher_tuple[11])
    cid_to_details = dict(map(lambda c: (c[0], (c[1], c[2])), collaborations))
    print('Adding edges')
    for edge in edges:
        collaboration = cid_to_details[edge[2]]
        graph.add_edge(edge[0], edge[1], cid=edge[2], title=collaboration[0], year=collaboration[1])
    return graph


def get_color_for_dept(dept):
    if dept == 'math':
        # yellow
        return '#ffff00'
    elif dept == 'electrical engineering':
        # blue
        return '#0050db'
    elif dept == 'biology':
        # green
        return '#37941b'
    elif dept == 'computer science':
        # red
        return '#ff0000'
    elif dept == 'computer science, electrical engineering':
        # purple
        return '#b300ff'
    else:
        # gray
        return '#757573'


def get_rids_for_department(department):
    cnx, cur = init_connection_with_json("./login.json")
    rids = []
    if department is MATH:
        rids = [t[0] for t in select_math_rids(cur)]
    elif department is BIOLOGY:
        rids = [t[0] for t in select_biology_rids(cur)]
    elif department is COMPUTER_SCIENCE:
        rids = [t[0] for t in select_computer_science_rids(cur)]
    elif department is ELECTRICAL_ENGINEERING:
        rids = [t[0] for t in select_electrical_engineering_rids(cur)]
    close_connection(cnx, cur)
    return rids


def generate_visualization(graph, out_file):
    print('Generating Visual in ' + out_file)
    visual = Network()
    nodes = graph.nodes.data()
    edges = graph.edges.data('year')
    for node, data_dict in nodes:
        visual.add_node(node, title=data_dict['name'], color=get_color_for_dept(data_dict['department']))
    for edge in edges:
        visual.add_edge(edge[0], edge[1], title=edge[2])
    visual.show(out_file)


class CollaborationGraph:
    def __init__(self):
        self.graph = generate_graph()
        self.math_graph = self.graph.subgraph(get_rids_for_department(MATH)).copy()
        self.biology_graph = self.graph.subgraph(get_rids_for_department(BIOLOGY)).copy()
        self.electrical_engineering_graph = self.graph.subgraph(get_rids_for_department(ELECTRICAL_ENGINEERING)).copy()
        self.computer_science_graph = self.graph.subgraph(get_rids_for_department(COMPUTER_SCIENCE)).copy()


print(time.strftime("%H:%M:%S", time.localtime()))
g = CollaborationGraph()
print(time.strftime("%H:%M:%S", time.localtime()))
generate_visualization(g.math_graph, './data/math_network.html')
generate_visualization(g.computer_science_graph, './data/computer_science_network.html')
generate_visualization(g.biology_graph, './data/biology_network.html')
generate_visualization(g.electrical_engineering_graph, './data/electrical_engineering_network.html')
