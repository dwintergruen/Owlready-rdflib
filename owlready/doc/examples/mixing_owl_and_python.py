from owlready import *
   
onto = Ontology("http://test.org/onto.owl")
   
class Drug(Thing):
  ontology = onto
  def get_per_tablet_cost(self):
    return self.cost / self.number_of_tablets
   
class has_for_cost(FunctionalProperty):
  ontology = onto
  domain   = [Drug]
  range    = [float]
ANNOTATIONS[has_for_cost]["python_name"] = "cost"
   
class has_for_number_of_tablets(FunctionalProperty):
  ontology = onto
  domain   = [Drug]
  range    = [int]
ANNOTATIONS[has_for_number_of_tablets]["python_name"] = "number_of_tablets"
   
my_drug = Drug("my_drug", cost = 10.0, number_of_tablets = 5)

print(my_drug.get_per_tablet_cost())

