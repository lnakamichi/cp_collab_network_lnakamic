import networkx as nx
import time

from db_writer import *
from pyvis.network import Network


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


class CollaborationGraph:
    def __init__(self):
        self.graph = generate_graph()

    def generate_visualization(self):
        print('Generating Visual in ./data/collaboration_graph_colored.html')
        visual = Network()
        nodes = self.graph.nodes.data()
        edges = self.graph.edges.data('year')
        for node, data_dict in nodes:
            visual.add_node(node, title=data_dict['name'], color=get_color_for_dept(data_dict['department']))
        for edge in edges:
            visual.add_edge(edge[0], edge[1], title=edge[2])
        visual.show('./data/collaboration_graph_colored.html')


print(time.strftime("%H:%M:%S", time.localtime()))
g = CollaborationGraph()
print(time.strftime("%H:%M:%S", time.localtime()))
g.generate_visualization()
