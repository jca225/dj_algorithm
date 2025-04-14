from dataclasses import dataclass, field
from graphviz import Digraph

"""Defines all of our data structures"""
@dataclass
class AtomicTrack:
    index: str = ""
    name: str = ""
    artist: str = ""
    publisher: str = ""
    url: str = ""
    time: str = ""
    links: list[str] = field(default_factory=list)

    def __hash__(self):
        return hash(self.index)  # Uses the unique index as hash


@dataclass
class CompoundTrack:
    index: str = ""
    name: str = ""
    artist: str = ""
    publisher: str = ""
    url: str = ""
    time: str = ""
    links: list[str] = field(default_factory=list)
    binded_atoms: list[AtomicTrack] = field(default_factory=list)
    invisible_atoms: list[AtomicTrack] = field(default_factory=list)

    def __hash__(self):
        return hash(self.index)  # Uses the unique index as hash


@dataclass
class Set:
    name: str = ""
    date_published: str = ""
    num_tracks: str = ""
    url_link: str = ""
    tracks: dict[str, CompoundTrack]=field(default_factory=dict)

def trace(compound_song):
    # builds a set of all nodes and edges in a graph
    nodes, binded_edges, mashed_edges = set(), set(), set()
    def build(v):
        if v not in nodes:
            nodes.add(v)
            for child in v.binded_atoms:
                nodes.add(child)
                binded_edges.add((child, v))
            for child in v.invisible_atoms:
                nodes.add(child)
                mashed_edges.add((child, v))
    build(compound_song)
    return nodes, binded_edges, mashed_edges

def draw_dot(compound_song):
    dot = Digraph(format='svg', graph_attr={'rankdir':'LR'}) # LR = left to right

    nodes, binded_edges, mashed_edges = trace(compound_song)
    for n in nodes:
        # Get the id of the node
        uid = str(id(n))
        # for any value in the graph, create a rectangular ('record') node for it
        dot.node(name=uid, label= "{name %s | index %s | time %s}" % (n.name, n.index, n.time), shape='record')
        if len(n.binded_atoms) != 0:
            identifier = n.name + " binded with"
            # if this compound track has some binded atoms, create a node indicating it
            dot.node(name=identifier, label = "binded with")
            # and connect this node to it
            dot.edge(identifier, uid)
        if len(n.invisible_atoms) != 0:
            identifier = n.name + " mashup with"
            # if this compound track has some binded atoms, create a node indicating it
            dot.node(name=identifier, label = "mashup with")
            # and connect this node to it
            dot.edge(identifier, uid)
    for node in nodes:
        print(type(node))
    for n1, n2 in binded_edges:
        # connect n1 to the op node of n2
        dot.edge(str(id(n1)), n2.name + " binded with")
    for n1, n2 in mashed_edges:
        # connect n1 to the op node of n2
        dot.edge(str(id(n1)), n2.name + " mashup with")
    return dot


