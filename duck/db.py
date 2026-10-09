from rdflib import Graph, URIRef
from rdflib.plugins.sparql import prepareQuery

from pywps import configuration

# Provide the path to the SQLite database in the local folder
# DB_URL = "sqlite:////var/lib/pywps/db/provenance.sqlite"
# DB_URL = "sqlite:////tmp/provenance.sqlite"
DB_URL = configuration.get_config_value("logging", "database")


class GraphDB(object):
    def __init__(self):
        # Create a graph with a specific backend store
        self.graph = Graph(
            store="SQLAlchemy", identifier=URIRef("http://example.org/graph")
        )
        self.graph.open(DB_URL, create=True)

    def add(self, data):
        new_graph = Graph()
        new_graph.parse(data=data, format="turtle")

        # add rdf to existing graph
        for triple in new_graph:
            self.graph.add(triple)
        # Commit changes to the store
        self.graph.commit()

    def query(self, query_str):
        namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "prov": "http://www.w3.org/ns/prov#",
            "provone": "http://purl.dataone.org/provone/2015/01/15/ontology#",
            "dcterms": "http://purl.org/dc/terms/",
            "clint": "urn:clint:",
        }
        query = prepareQuery(query_str, initNs=namespaces)
        results = self.graph.query(query)
        return results
