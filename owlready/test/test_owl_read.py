import owlready


owlready.onto_path.append("/Users/dwinter/Desktop/")
scholars_ontology = owlready.get_ontology("http://ontology.mpiwg-berlin.mpg.de/scholarlyRelations/scholars_ontology.owl").load()

print(scholars_ontology.classes)
print(scholars_ontology.base_iri)
print(owlready.to_n3(scholars_ontology.Institution))
si = scholars_ontology.Person("siegg")
mu = scholars_ontology.Person("muller") 
owlready.ANNOTATIONS[mu].add_annotation(owlready.rdfs.label,"LABEL")

si.co_author.append(mu)

print(owlready.to_n3(scholars_ontology))

import rdflib



from rdflib.plugins.stores.sparqlstore import NSSPARQLWrapper,SPARQLUpdateStore,\
    SPARQLUpdateStore

#store = SPARQLUpdateStore(queryEndpoint="http://localhost:8890/sparql",
#                        update_endpoint="http://localhost:8890/sparql-auth",
#                       )

store = SPARQLUpdateStore(queryEndpoint="http://localhost:10214/blazegraph/sparql",
                        update_endpoint="http://localhost:10214/blazegraph/sparql",
                       )


store.setNamespaceBindings({"ont":"http://ontology.mpiwg-berlin.mpg.de/scholarlyRelations",
                          "end":"http://entity.mpiwg-berlin.mpg.de/modernPhysics"})



#g = rdflib.Graph(store=store,identifier="http://entities.mpiwg-berlin.mpg.de/graphs/gr/V14TEST")
#g.store.setCredentials('admin','admin')
#g.store.setHTTPAuth('DIGEST')
#owlready.to_rdflib(scholars_ontology,g)
