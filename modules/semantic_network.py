
import json
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
NETWORK_FILE = BASE_DIR / "knowledge" / "semantic_network.json"


class SemanticNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.load()

    def load(self):
        with open(NETWORK_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.graph.clear()
        self.graph.add_nodes_from(data["nodes"])

        for item in data["relations"]:
            self.graph.add_edge(
                item["source"],
                item["target"],
                relation=item["relation"]
            )

    def find_related(self, node):
        if node not in self.graph:
            return []

        result = []

        for target in self.graph.successors(node):
            result.append({
                "object": target,
                "relation": self.graph[node][target]["relation"]
            })

        return result

    def search_path(self, source, target):
        try:
            return nx.shortest_path(
                self.graph,
                source=source,
                target=target
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def show(self):
        plt.figure(figsize=(13, 8))

        pos = nx.spring_layout(self.graph, seed=42)

        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_color="#A78BFA",
            node_size=2400,
            font_size=9,
            arrows=True,
            arrowsize=18
        )

        labels = nx.get_edge_attributes(
            self.graph, "relation"
        )

        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels=labels,
            font_size=7
        )

        plt.title("Семантическая сеть FixAI")
        plt.axis("off")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    network = SemanticNetwork()

    print("СВЯЗАННЫЕ ОБЪЕКТЫ КОМПЬЮТЕРА:")

    for item in network.find_related("Компьютер"):
        print(
            f"Компьютер → {item['relation']} → {item['object']}"
        )

    print("\nПОИСК ПУТИ:")
    print(
        network.search_path(
            "Компьютер",
            "Нет изображения"
        )
    )

    network.show()
