import logging, beautifullogger
import sys, re
from pathlib import Path
import networkx as nx, pygraphviz as pgv

logger = logging.getLogger(__name__)

def setup_nice_logging():
    beautifullogger.setup(logmode="w")
    logging.getLogger("toolbox.ressource_manager").setLevel(logging.WARNING)
    logging.getLogger("toolbox.signal_analysis_toolbox").setLevel(logging.WARNING)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        logger.info("Keyboard interupt")
        sys.exit()
        return
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception

def singleglob(p: Path, *patterns, error_string='Found {n} candidates for pattern {patterns} in folder {p}', only_ok=False):
    all = [path for pat in patterns for path in p.glob(pat)]
    if only_ok:
        return len(all)==1
    if len(all) >1:
        raise FileNotFoundError(error_string.format(p=p, n=len(all), patterns=patterns))
    if len(all) ==0:
        raise FileNotFoundError(error_string.format(p=p, n=len(all), patterns=patterns))
    return all[0]

# def nxrender(graph: nx.Graph, autolabel=[..., r'NEXT.*', "shape", "color"], **drawkwargs):
#     graph = graph.copy()
#     node_labels = {node: "\n".join([f'{k}={v}' for k,v in graph.nodes[node].items() if not "NEXT" in k]) for node in graph.nodes}
#     edge_labels = {edge: "\n".join([f'{k}={v}' for k,v in graph.edges[edge].items()]) for edge in graph.edges}
#     nx.set_node_attributes(graph, node_labels, "label")
#     nx.set_edge_attributes(graph, edge_labels, "label")
#     for node in graph.nodes:
#         attrs = []
#         for attr in graph.nodes(data=True)[node]:
#                 if attr != "label":
#                     attrs.append(attr)
#         for attr in attrs:
#             graph.nodes[node].pop(attr, None)
#     return nx.nx_agraph.to_agraph(graph).draw(prog="dot", **drawkwargs)
    
def nxrender(graph: nx.Graph, nodeautolabel=[..., "+dot"], edgeautolabel=[..., "+dot"], legend=True, **drawkwargs):
    dotnodelabels = ["shape", "color", "fillcolor", "style"]
    dotedgelabels = []
    if "+dot" in nodeautolabel:
        nodeautolabel=[k for k in nodeautolabel if not k=="+dot"] + dotnodelabels
    if "+dot" in edgeautolabel:
        edgeautolabel=[k for k in edgeautolabel if not k=="+dot"] + dotedgelabels
    nodeautolabel+=["legend"]
    graph = graph.copy()
    legend_data = {}
    for node in graph.nodes:
        if nodeautolabel is not None:
            labels=[]
            for attr in graph.nodes(data=True)[node]:
                match = False
                reverse=False
                for a in nodeautolabel:
                    if hasattr(a, "fullmatch"):
                        if a.fullmatch(str(attr)) is not None:
                            match=True
                            break
                    elif isinstance(a, str):
                        if str(attr)==a:
                            match=True
                            break
                    elif a==...:
                        reverse=True
                    else:
                        raise Exception("Unknown type for matching")
                if ... in nodeautolabel:
                    reverse=True
                if match != reverse:
                    labels.append(f'{attr}={graph.nodes(data=True)[node][attr]}')
            graph.nodes(data=True)[node]["label"] = "\n".join(labels)
        if "legend" in graph.nodes(data=True)[node]:
            legend_val = graph.nodes(data=True)[node]["legend"]
            data = {k:v for k,v in graph.nodes(data=True)[node].items() if k in dotnodelabels}
            if not legend_val in legend_data:
                legend_data[legend_val] = data
            elif legend_data[legend_val]!=data:
                raise Exception("Non matching legend...")

    for edge in graph.edges:
        if edgeautolabel is not None:
            labels=[]
            for attr in graph.edges()[edge]:
                match = False
                reverse=False
                for a in edgeautolabel:
                    if hasattr(a, "fullmatch"):
                        if a.fullmatch(str(attr)) is not None:
                            match=True
                            break
                    elif isinstance(a, str):
                        if str(attr)==a:
                            match=True
                            break
                    elif a==...:
                        reverse=True
                    else:
                        raise Exception("Unknown type for matching")
                if ... in edgeautolabel:
                    reverse=True
                if match != reverse:
                    labels.append(f'{attr}={graph.edges[edge][attr]}')
            graph.edges[edge]["label"] = "\n".join(labels)
    if legend and len(legend_data) > 0:
        legend_graph = nx.DiGraph(size = "9, 16" )
        for k,v in legend_data.items():
            legend_graph.add_node(k, **v)
        g = nx.nx_agraph.to_agraph(nx.union(legend_graph, graph))
        nodes = list(legend_graph.nodes)
        legend = g.add_subgraph(nodes, name="legend", label="legend", rankdir="LR", style="filled", cluster=True)
        # g.add_edge(list(legend_data.keys())[0], 1, style="invis", minlen=5)
    else:
        g = nx.nx_agraph.to_agraph(graph)
    return g.draw(prog="dot", **drawkwargs)
    
    
def run():
    setup_nice_logging()
    logger.info("Running start")
    logger.info("Running end")