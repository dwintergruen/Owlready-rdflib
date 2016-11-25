from owlready import *
   
onto = Ontology("http://test.org/onto.owl")
   
class Drug(Thing):
  ontology = onto
  def take(self): print("I took a drug")
   
class ActivePrinciple(Thing):
  ontology = onto
   
class has_for_active_principle(Property):
  ontology = onto
  domain   = [Drug]
  range    = [ActivePrinciple]
ANNOTATIONS[has_for_active_principle]["python_name"] = "active_principles"

class Placebo(Drug):
  equivalent_to = [Drug & NOT(restriction(has_for_active_principle, SOME, ActivePrinciple))]
  def take(self): print("I took a placebo")

class SingleActivePrincipleDrug(Drug):
  equivalent_to = [Drug & restriction(has_for_active_principle, EXACTLY, 1, ActivePrinciple)]
  def take(self): print("I took a drug with a single active principle")

class DrugAssociation(Drug):
  equivalent_to = [Drug & restriction(has_for_active_principle, MIN, 2, ActivePrinciple)]
  def take(self): print("I took a drug with %s active principles" % len(self.active_principles))

acetaminophen   = ActivePrinciple("acetaminophen")
amoxicillin     = ActivePrinciple("amoxicillin")
clavulanic_acid = ActivePrinciple("clavulanic_acid")

AllDistinct(acetaminophen, amoxicillin, clavulanic_acid)

drug1 = Drug(active_principles = [acetaminophen])
drug2 = Drug(active_principles = [amoxicillin, clavulanic_acid])
drug3 = Drug(active_principles = [])

drug1.closed_world()
drug2.closed_world()
drug3.closed_world()

onto.sync_reasoner()

print()
print("I'm taking drug1...")
drug1.take()

print()
print("I'm taking drug2...")
drug2.take()

print()
print("I'm taking drug3...")
drug3.take()


