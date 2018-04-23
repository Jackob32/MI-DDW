import wikipedia
import nltk
from pprint import pprint

import nltk
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

import csv
import networkx


#opens csv
def load_csv_data(file):
    data = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            data.append(row)
    return data



def create_graph_from_file(file):
    data = []
    data = load_csv_data(file)

    film_actors = {}  # Mapping {film: [act1, act2]}
    G = networkx.Graph()
    for item in data:
        G.add_node(item[2])

        if item[1]not in film_actors:
            film_actors[item[1]] = []
        film_actors[item[1]].append(item[2])

    for film, actor_list in film_actors.items():
        if len(actor_list) < 9:
            continue
        for actor in actor_list:
            for other_actor in actor_list:
                if actor != other_actor:
                    G.add_edge(actor, other_actor)
                    # print("Adding edge between [{}] - [{}]".format(actor, other_actor))

    return G

Graph=create_graph_from_file("casts2.csv")

print("General statistics")
#e.g. number of nodes and edges, density, number of components


nodes = Graph.number_of_nodes()
edges = Graph.number_of_edges()
density = edges / (nodes * (nodes - 1) / 2)


print("Number of nodes: ", len(Graph.nodes()) )
print("Number of edges: ", len(Graph.edges()) )
print("density: ", density)

print("Avg edges: ", len(Graph.edges())/len(Graph.nodes())  )
print("number of components: ", nx.number_connected_components(Graph))

#print("-------------- Components and connectivity -------------")

#for component in nx.connected_components(Graph):
    #print(component)



print("-------------- communities -------------")


communities = {node: cid + 1 for cid, community in enumerate(nx.algorithms.community.k_clique_communities(Graph, 3)) for
               node in community}

group_actors = {}
for key, item in communities.items():
    if item not in group_actors:
        group_actors[item] = []
        group_actors[item].append(key)


group_actors = sorted(group_actors.items(), key=lambda element: len(element[1]), reverse=True)

print("COMMUNITIES:")
for community in group_actors[:10]:
    print("ID {}, {} actors: {}".format(community[0], len(community[1]), ", ".join(community[1])))


# Add as attribute to graph
for actor, community_id in communities.items():
    Graph.node[actor]['community_id'] = community_id


print("-------------- Centrality -------------")


print("-------------- degree_centrality -------------")
degree_centrality=nx.degree_centrality(Graph)

degree_centrality = sorted(degree_centrality.items(), key=lambda element: element[1], reverse=True)
print("{} - top 10:degree_centrality")
print("  {} \n".format(" ".join(["{} ({}) \n".format(elm[0], elm[1]) for elm in degree_centrality[:10]])))

'''
print("-------------- betweenness_centrality -------------")
betweenness_centrality=nx.betweenness_centrality(Graph)

betweenness_centrality = sorted(betweenness_centrality.items(), key=lambda element: element[1], reverse=True)
print("{} - top 10:degree_centrality")
print("  {} \n".format(" ".join(["{} ({}) \n".format(elm[0], elm[1]) for elm in betweenness_centrality[:10]])))
'''

print("-------------- eigenvector_centrality -------------")

eigenvector_centrality=nx.eigenvector_centrality(Graph)

eigenvector_centrality = sorted(eigenvector_centrality.items(), key=lambda element: element[1], reverse=True)
print("{} - top 10:degree_centrality")
print("  {} \n".format(" ".join(["{} ({}) \n".format(elm[0], elm[1]) for elm in eigenvector_centrality[:10]])))

'''
print("-------------- closeness_centrality -------------")

closeness_centrality=nx.closeness_centrality(Graph)

closeness_centrality = sorted(closeness_centrality.items(), key=lambda element: element[1], reverse=True)
print("{} - top 10:degree_centrality")
print("  {} \n".format(" ".join(["{} ({}) \n".format(elm[0], elm[1]) for elm in closeness_centrality[:10]])))
'''

start_actor='Maggie Smith'

lengths = nx.single_source_shortest_path_length(Graph, start_actor)

sum = 0
for actor, length in lengths.items():
    Graph.node[actor]['Length'] = length
    sum += length

bacon_average = sum / len(lengths)

lengths = sorted(lengths.items(), key=lambda element: element[1], reverse=True)


print("Pocatecni node")
print(start_actor)

print("Kevin Bacon number")

print("Average: ")
print(bacon_average)

print("Smallest 10: {}".format(", ".join(["{} ({})".format(actorlen[0], actorlen[1]) for actorlen in lengths[-10:]])))

networkx.write_gexf(Graph, 'exported_graph.gexf')


























