from owlready import *
   
onto = Ontology("http://test.org/onto.owl")
   
class Drug(Thing):
  ontology = onto
  def take(self): print("I took a drug")
   
class has_for_cip(FunctionalProperty):
  ontology = onto
  domain   = [Drug]
  range    = [int]
ANNOTATIONS[has_for_cip]["python_name"] = "cip"

has_for_cip.create_index(Drug)

drug1 = Drug("drug1", cip = 2166868)
drug2 = Drug("drug2", cip = 4166507)
drug3 = Drug("drug3", cip = 3698604)

# Get a drug by its CIP code
print(has_for_cip.indexes[Drug][4166507])
