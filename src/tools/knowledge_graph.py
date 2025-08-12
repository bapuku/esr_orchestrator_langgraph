import networkx as nx
import pandas as pd
from pathlib import Path

class KnowledgeGraph:
    def __init__(self):
        self.G = nx.MultiDiGraph()

    def init_from_files(self, waste_csv: str, iso_txt: str):
        if Path(waste_csv).exists():
            df = pd.read_csv(waste_csv)
            for _, r in df.iterrows():
                wb = str(r["batch_id"])
                container = str(r["container_id"])
                material = str(r["material"])
                self.G.add_node(wb, type="WasteBatch", **r.to_dict())
                self.G.add_node(container, type="Container")
                self.G.add_node(material, type="Material")
                self.G.add_edge(container, wb, relation="contains_batch")
                self.G.add_edge(wb, material, relation="contains_material")
        if Path(iso_txt).exists():
            with open(iso_txt, "r", encoding="utf-8") as f:
                for line in f:
                    clause = line.strip()
                    if clause:
                        self.G.add_node(clause, type="Regulation")
                        # simplistic hook: relate clause to all materials initially
                        for n, data in self.G.nodes(data=True):
                            if data.get("type") == "Material":
                                self.G.add_edge(clause, n, relation="applies_to")

    def query(self, q: str) -> dict:
        # very simple micro-language: "NODE -> relation -> ?"
        try:
            subj, rel, obj = [p.strip() for p in q.split("->")]
        except Exception:
            return {"error": "query format: SUBJECT -> relation -> ?"}
        subj = subj.strip()
        rel = rel.strip()
        results = []
        if not self.G.has_node(subj):
            return {"results": results}
        for _, tgt, d in self.G.out_edges(subj, data=True):
            if d.get("relation") == rel:
                results.append({"from": subj, "relation": rel, "to": tgt})
        return {"results": results}

KG = KnowledgeGraph()
