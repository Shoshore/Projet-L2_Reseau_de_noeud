from random import sample, randint, random
from collections import deque
from networkx import Graph, spring_layout, draw_networkx_nodes, draw_networkx_labels, draw_networkx_edges
from matplotlib.pyplot import title, gcf, show
from numpy import linalg, array


class Noeud:
    """
    Cette classe représente un nœud dans un graphe.

    Attributes:
        * id (int): 
            L'identifiant unique du nœud.
        * tier (str):
            Le niveau/tier auquel le nœud appartient.
        * voisins (list):
            Une liste des identifiants des nœuds voisins de celui-ci dans le graphe.
    """
    def __init__(self, id, tier):
        self.id = id
        self.tier = tier
        self.voisins = []


def calcule_du_tier(id_noeud):
    """
    Calcule le tier d'un nœud en fonction de son identifiant.

    Ce calcul attribue un niveau/tier à un nœud en fonction de son identifiant.
    Les nœuds ayant un identifiant inférieur à 10 sont attribués au Tier 1,
    ceux dont l'identifiant est compris entre 10 et 29 sont attribués au Tier 2,
    et les autres sont attribués au Tier 3.

    Args:
        * id_noeud (int):
            L'identifiant du nœud dont on veut calculer le tier.

    Returns:
        * str:
            Le tier calculé pour le nœud.

    """
    if id_noeud < 10:
        return "Tier1"
    elif id_noeud < 30:
        return "Tier2"
    else:
        return "Tier3"


def creation_reseau_aleatoire():
    """
    Crée un réseau de manière aléatoire avec des nœuds et des liens.

    Ce réseau est créé en générant des nœuds avec des identifiants de 0 à 99
    et en leur attribuant des niveaux/tiers en fonction de leur identifiant.
    Ensuite, des liens sont établis entre les nœuds en fonction de probabilités
    spécifiques à chaque zone/tier, avec des coûts de liens aléatoires.

    Returns:
        * list:
            Une liste de nœuds représentant le réseau créé.
    """
    graph = []
    for i in range(100):
        noeud = Noeud(i, calcule_du_tier(i))
        graph.append(noeud)

    for i in range(10):
        for j in range(10):
            if i != j and random() < 0.75:
                cout_du_lien = randint(5, 10)
                graph[i].voisins.append((graph[j], cout_du_lien))
                graph[j].voisins.append((graph[i], cout_du_lien))

    for i in range(10, 30):
        tier1_voisins = sample(graph[:10], randint(1, 2))
        tier2_voisins = sample(graph[10:30], randint(2, 3))
        for voisin in tier1_voisins + tier2_voisins:
            if voisin != graph[i]:
                cout_du_lien = randint(10, 20)
                graph[i].voisins.append((voisin, cout_du_lien))
                voisin.voisins.append((graph[i], cout_du_lien))

    for i in range(30, 100):
        tier2_voisins = sample(graph[10:30], 2)
        for voisin in tier2_voisins:
            cout_du_lien = randint(20, 50)
            graph[i].voisins.append((voisin, cout_du_lien))
            voisin.voisins.append((graph[i], cout_du_lien))

    return graph


def est_connexe(graph):
    """
    Vérifie si le graphe est connexe.

    Cette fonction vérifie si le graphe représenté par une liste de nœuds est connexe,
    c'est-à-dire que tous les nœuds du graphe peuvent être atteints à partir de n'importe quel
    autre nœud en suivant les liens du graphe.

    Args:
        * graph (list):
            Une liste de nœuds représentant le graphe.

    Returns:
        * bool:
            True si le graphe est connexe, False sinon.
    """
    noeud_debut = graph[0]
    
    visiter = set()
    file = deque([noeud_debut])

    while file:
        noeud_actuel = file.popleft()
        visiter.add(noeud_actuel)

        for voisin, _ in noeud_actuel.voisins:
            if voisin not in visiter:
                file.append(voisin)

    return len(visiter) == len(graph)


def calcule_table_routage(graph):
    """
    Calcule les tables de routage pour chaque nœud dans le graphe.

    Cette fonction calcule les tables de routage pour chaque nœud dans le graphe,
    en utilisant l'algorithme de Dijkstra pour trouver les chemins les plus courts
    vers tous les autres nœuds du graphe.

    Args:
        * graph (list):
            Une liste de nœuds représentant le graphe.

    """
    for noeud in graph:
        table_de_routage = {voisin.id: (float('inf'), None) for voisin in graph if voisin != noeud}
        table_de_routage[noeud.id] = (0, noeud.id)

        pas_visite = set(graph)

        while pas_visite:
            noeud_actuel = min(pas_visite, key=lambda x: table_de_routage[x.id][0])
            pas_visite.remove(noeud_actuel)

            for voisin, cout in noeud_actuel.voisins:
                nouveau_cout = table_de_routage[noeud_actuel.id][0] + cout
                if nouveau_cout < table_de_routage[voisin.id][0]:
                    table_de_routage[voisin.id] = (nouveau_cout, noeud_actuel.id)

        noeud.table_de_routage = table_de_routage


def generer_reseau():
    """
    Génère un réseau connexe de manière aléatoire.

    Cette fonction génère un réseau en utilisant la fonction `creation_reseau_aleatoire()`.
    Si le réseau généré n'est pas connexe, elle réessaie jusqu'à obtenir un réseau connexe.

    Returns:
        * list:
            Une liste de nœuds représentant le réseau généré.
    """
    reseau = creation_reseau_aleatoire()
    
    while not est_connexe(reseau):
        reseau = creation_reseau_aleatoire()
    
    return reseau


reseau = generer_reseau()

calcule_table_routage(reseau)


def reconstruct_chemin(id_source, id_destinataire, reseau):
    """
    Reconstruit le chemin entre deux nœuds dans le réseau.

    Cette fonction reconstruit le chemin entre un nœud source et un nœud destinataire
    en utilisant les tables de routage des nœuds dans le réseau.

    Args:
        * id_source (int):
            L'identifiant du nœud source.
        * id_destinataire (int):
            L'identifiant du nœud destinataire.
        * reseau (list):
            Une liste de nœuds représentant le réseau.

    Returns:
        * list:
            Une liste d'identifiants de nœuds représentant le chemin de id_source à id_destinataire.
    """
    noeud_source = reseau[id_source]

    table_de_routage = noeud_source.table_de_routage

    chemin = []
    id_noeud_actuel = id_destinataire

    while id_noeud_actuel != id_source:
        next_id_noeud = table_de_routage[id_noeud_actuel][1]
        chemin.append(id_noeud_actuel)
        id_noeud_actuel = next_id_noeud

    chemin.append(id_source)
    chemin.reverse()

    return chemin


def montrer_chemin():
    """
    Affiche le chemin entre deux nœuds sélectionnés.

    Cette fonction affiche le chemin entre un nœud source et un nœud destinataire
    dans le réseau, en utilisant la fonction reconstruct_chemin().
    """
    if noeud_source is None or noeud_destinataire is None:
        print("Sélectionne le noeud source et le noeud destinataire")
        return

    chemin = reconstruct_chemin(noeud_source, noeud_destinataire, reseau)
    print("Chemin du noeud {} vers le noeud {}: {}".format(noeud_source, noeud_destinataire, chemin))


graphique = Graph()

for noeud in reseau:
    graphique.add_node(noeud.id)
    for voisin, _ in noeud.voisins:
        graphique.add_edge(noeud.id, voisin.id)

position = spring_layout(graphique)

draw_networkx_nodes(graphique, position, node_size=200)

draw_networkx_edges(graphique, position)

draw_networkx_labels(graphique, position)

noeud_source = None
noeud_destinataire = None


def clique_sur_noeud(event):
    """
    Gère l'événement de clic sur un nœud dans le graphique.

    Cette fonction met à jour les nœuds source et destinataire en fonction du nœud
    cliqué dans le graphique. Si les deux nœuds sont sélectionnés, elle affiche le chemin
    entre eux en utilisant la fonction montrer_chemin().

    Args:
        * event:
            L'événement de clic sur le graphique.
    """
    global noeud_source, noeud_destinataire
    x, y = event.xdata, event.ydata
    if x is not None and y is not None:
        id_noeuds = list(graphique.nodes)
        distances = [(linalg.norm(array((x, y)) - array(position[noeud])), noeud) for noeud in id_noeuds]
        distances.sort()
        noeud_plus_proche = distances[0][1]
        if noeud_source is None:
            noeud_source = noeud_plus_proche
            print("Noeud source : ", noeud_source)
        elif noeud_destinataire is None:
            noeud_destinataire = noeud_plus_proche
            print("Noeud destinataire : ", noeud_destinataire)
            montrer_chemin()


title("Graphique du réseau")
gcf().canvas.mpl_connect('button_press_event', clique_sur_noeud)

show()