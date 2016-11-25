
# Script Python utilisé pour générer onto_ci.owl
# Il n'est pas nécessaire d'exécuter / d'utiliser ce script pour tester l'exemple.

import sys, os
from owlready import *

onto_path.append(os.path.dirname(__file__))

onto_ci = get_ontology("http://test.org/onto_ci.owl")
   
class Médicament(Thing):
  ontology = onto_ci

class Contre_indication(Thing):
  ontology = onto_ci
   
class Condition_clinique(Thing):
  ontology = onto_ci

  
class Terme_niveau1(Thing):
  ontology = onto_ci
  
class Terme_maladie_hémorragique(Terme_niveau1):
  ontology = onto_ci

  
class Qualifieur(Thing):
  ontology = onto_ci

class Qualifieur_dorigine(Qualifieur):
  ontology = onto_ci

class Acquis(Qualifieur_dorigine):
  ontology = onto_ci
  
class Constitutionnel(Qualifieur_dorigine):
  ontology = onto_ci

Qualifieur_dorigine.equivalent_to.append(Acquis | Constitutionnel)
AllDisjoint(Acquis, Constitutionnel)


class a_pour_contre_indication(InverseFunctionalProperty):
  ontology = onto_ci
  domain   = [Médicament]
  range    = [Contre_indication]
  
class est_contre_indication_de(FunctionalProperty):
  ontology = onto_ci
  domain   = [Contre_indication]
  range    = [Médicament]
  inverse_property = a_pour_contre_indication
  
class a_pour_condition_clinique(Property):
  ontology = onto_ci
  domain   = [Contre_indication]
  range    = [Condition_clinique]

class est_condition_clinique_de(Property):
  ontology = onto_ci
  domain   = [Condition_clinique]
  range    = [Contre_indication]
  inverse_property = a_pour_condition_clinique

class a_pour_terme_niveau1(FunctionalProperty):
  ontology = onto_ci
  domain   = [Condition_clinique]
  range    = [Terme_niveau1]

class a_pour_qualifieur(Property):
  ontology = onto_ci
  domain   = [Condition_clinique]
  range    = [Qualifieur]

Condition_clinique.is_a.append(restriction(a_pour_qualifieur, EXACTLY, 1, Qualifieur_dorigine))

# Import the Owlready ontology
onto_ci.imported_ontologies.append(owlready_ontology)

# Add a "python_module" annotation to the ontology,
# This annotation will make Owlready load the onto_ci.py Python module automatically
# when the ontology is loaded
ANNOTATIONS[onto_ci][owlready_ontology.python_module] = "onto_ci"

# Save the ontology in OWL/XML
onto_ci.save()
