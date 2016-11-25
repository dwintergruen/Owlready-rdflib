
# Méthodes Python associées à onto_ci.owl
# Ce fichier est chargé automatiquement lorsque onto_ci.owl est chargée.

from owlready import *

onto_ci = get_ontology("http://test.org/onto_ci.owl")

class Médicament(Thing):
    ontology = onto_ci
    
    def teste_ci(self, Condition):
        Condition_clinique_CI = onto_ci["Condition_clinique_CI_avec_" + self.name]
        Condition_clinique_OK = onto_ci["Condition_clinique_OK_avec_" + self.name]

        if issubclass(Condition, Condition_clinique_CI): return "CI"
        if issubclass(Condition, Condition_clinique_OK): return "ok"
        return "CI/ok"

