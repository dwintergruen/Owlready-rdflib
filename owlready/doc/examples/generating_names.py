from owlready import *
   
onto = Ontology("http://test.org/onto.owl")

class Drug(GeneratedName, Thing):
  ontology = onto
  def generate_name(self):
    return "drug_with_%s" % "_and_".join(sorted(ai.name for ai in self.active_principles))

class ActivePrinciple(Thing):
  ontology = onto

class has_for_active_principle(Property):
  ontology = onto
  domain   = [Drug]
  range    = [ActivePrinciple]
ANNOTATIONS[has_for_active_principle]["python_name"] = "active_principles"

amoxicillin     = ActivePrinciple("amoxicillin")
clavulanic_acid = ActivePrinciple("clavulanic_acid")
my_drug       = Drug()
my_drug.active_principles = [amoxicillin, clavulanic_acid]
print(my_drug.name)
