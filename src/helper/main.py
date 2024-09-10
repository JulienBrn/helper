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
    

class Step:
    def __init__(self, script: Path, file: str):
        self.script = script
        self.file = file
    def exec_if_necessary(self):
        if not (self.script.parent/ self.file).exists():
            if not self.script.exists():
                raise Exception("Problem")
            else:
                if self.script.suffix ==".ipynb":
                    import papermill, shutil
                    tmp_script = self.script.with_name(self.script.name+"_tmp")
                    papermill.execute_notebook(self.script, tmp_script, cwd=self.script.parent)
                    shutil.move(tmp_script, self.script)
        if not (self.script.parent/ self.file).exists():
            raise Exception(f"Script {self.script} did not create file {self.file}")
        return (self.script.parent/ self.file)

def dict_merge(*d, incompatible="raise"):
    def dict_merge_impl(d1, d2):
        if not isinstance(d1, dict) or not isinstance(d2, dict):
            if not d1==d2:
                import pandas as pd
                if pd.isna(d1):
                    return d2
                if pd.isna(d2):
                    return d1
                if incompatible == "raise":
                    raise Exception(f"problem merging dictionaries... {d1} {d2} {pd.isna(d2)} {pd.isna(d1)}")
                elif incompatible == "remove":
                    return {}
            return d1
        else:
            merge = {k:dict_merge(v, d2[k], incompatible=incompatible) for k,v in d1.items() if k in d2}
            return {k:v for k,v in d1.items() if not k in d2} | {k:v for k,v in d2.items() if not k in d1} |  {k:v for k,v in merge.items() if not v=={}}
    if len(d) ==0:
        return {}
    curr = d[0]
    for di in d[1:]:
        curr= dict_merge_impl(curr, di)
    return curr
def run():
    setup_nice_logging()
    logger.info("Running start")
    logger.info("Running end")