from owlready import *
   
onto = Ontology("http://test.org/onto.owl")
   
class Drug(GeneratedName, Thing):
  ontology = onto
  def generate_name(self):
    return "drug_cip:%s_with_%s" % (self.cip, "_and_".join(sorted(ai.inn for ai in self.active_principles)))
   
class ActivePrinciple(GeneratedName, Thing):
  ontology = onto
  def generate_name(self):
    return "active_principle_%s" % self.inn

class DrugForm(Thing):
  ontology = onto
   
tablet     = DrugForm("tablet")
capsule    = DrugForm("capsule")
injectable = DrugForm("injectable")
pomade     = DrugForm("pomade")


class has_for_cip(FunctionalProperty):
  ontology = onto
  domain   = [Drug]
  range    = [int]
ANNOTATIONS[has_for_cip]["python_name"] = "cip"
  
class has_for_active_principle(Property):
  ontology = onto
  domain   = [Drug]
  range    = [ActivePrinciple]
ANNOTATIONS[has_for_active_principle]["python_name"] = "active_principles"

class has_for_form(FunctionalProperty):
  ontology = onto
  domain   = [Drug]
  range    = [DrugForm]
ANNOTATIONS[has_for_form]["python_name"] = "form"

# INN means 'international nonproprietary name'
class has_for_inn(FunctionalProperty):
  ontology = onto
  domain   = [ActivePrinciple]
  range    = [normstr]
ANNOTATIONS[has_for_inn]["python_name"] = "inn"


# Reorder the priority:

ANNOTATIONS[has_for_cip             ]["editobj_priority"] = 1
ANNOTATIONS[has_for_active_principle]["editobj_priority"] = 2
ANNOTATIONS[has_for_form            ]["editobj_priority"] = 3


acetaminophen   = ActivePrinciple(inn = "acetaminophen")
amoxicillin     = ActivePrinciple(inn = "amoxicillin")
clavulanic_acid = ActivePrinciple(inn = "clavulanic_acid")
   
drug1 = Drug(cip = 1234, active_principles = [acetaminophen])
drug2 = Drug(cip = 1235, active_principles = [amoxicillin, clavulanic_acid])
drug3 = Drug()



from owlready.editor import *
from owlready.instance_editor import *
import editobj3#, editobj3.introsp as introsp


for ontology in onto.indirectly_imported_ontologies(): configure_editobj_from_ontology(ontology)

# Choose between Qt or HTML (a web browser should open)

editobj3.GUI = "Qt"
#editobj3.GUI = "HTML"

if editobj3.GUI == "Qt":
  import sys, PyQt5.QtWidgets as qtwidgets
  if qtwidgets.QApplication.startingUp(): qtwidgets.app = qtwidgets.QApplication(sys.argv)
  
editor = OntologyInstanceEditor()
editor.set_ontology(onto, edited_classes = [ActivePrinciple, Drug])
editor.main()
