
# Cet example correspond à celui décrit dans le papier publié à IC 2015 :
#       Lamy JB, Berthelot H
#       Owlready : programmation orientée ontologie en Python
#       Actes du congrès d’Ingénierie des Connaissances (IC2015) 2015

# Fichier d'exemple chargeant onto_ci.owl et testant 3 médicaments et 3 conditions cliniques.

import sys, os
from owlready import *

onto_path.append(os.path.dirname(__file__))

onto_ci = get_ontology("http://test.org/onto_ci.owl").load()

ticagrélor = onto_ci.Médicament("ticagrélor")
aspirine   = onto_ci.Médicament("aspirine")
héparine   = onto_ci.Médicament("héparine")
AllDistinct(ticagrélor, aspirine, héparine)

class Maladie_hémorragique(onto_ci.Condition_clinique):
  equivalent_to = [
    onto_ci.Condition_clinique
  & onto_ci.a_pour_terme_niveau1(SOME, onto_ci.Terme_maladie_hémorragique)
  & onto_ci.a_pour_qualifieur   (SOME, onto_ci.Qualifieur_dorigine)
  ]
  
class Maladie_hémorragique_acquise(onto_ci.Condition_clinique):
  equivalent_to = [
    onto_ci.Condition_clinique
  & onto_ci.a_pour_terme_niveau1(SOME, onto_ci.Terme_maladie_hémorragique)
  & onto_ci.a_pour_qualifieur   (SOME, onto_ci.Acquis)
  ]

class Maladie_hémorragique_constitutionnelle(onto_ci.Condition_clinique):
  equivalent_to = [
    onto_ci.Condition_clinique
  & onto_ci.a_pour_terme_niveau1(SOME, onto_ci.Terme_maladie_hémorragique)
  & onto_ci.a_pour_qualifieur   (SOME, onto_ci.Constitutionnel)
  ]


ci1 = onto_ci.Contre_indication()
aspirine.a_pour_contre_indication.append(ci1)
ci1.is_a.append(onto_ci.a_pour_condition_clinique(ONLY, Maladie_hémorragique_acquise))
Maladie_hémorragique_acquise.is_a.append(onto_ci.est_condition_clinique_de(VALUE, ci1))

ci2 = onto_ci.Contre_indication()
aspirine.a_pour_contre_indication.append(ci2)
ci2.is_a.append(onto_ci.a_pour_condition_clinique(ONLY, Maladie_hémorragique_constitutionnelle))
Maladie_hémorragique_constitutionnelle.is_a.append(onto_ci.est_condition_clinique_de(VALUE, ci2))

aspirine.is_a.append(onto_ci.a_pour_contre_indication(ONLY, one_of(ci1, ci2)))

ci3 = onto_ci.Contre_indication()
ticagrélor.a_pour_contre_indication.append(ci3)
ci3.is_a.append(onto_ci.a_pour_condition_clinique(ONLY, Maladie_hémorragique))
Maladie_hémorragique.is_a.append(onto_ci.est_condition_clinique_de(VALUE, ci3))
ticagrélor.is_a.append(onto_ci.a_pour_contre_indication(ONLY, one_of(ci3)))

ci4 = onto_ci.Contre_indication()
héparine.a_pour_contre_indication.append(ci4)
ci4.is_a.append(onto_ci.a_pour_condition_clinique(ONLY, Maladie_hémorragique_constitutionnelle))
Maladie_hémorragique_constitutionnelle.is_a.append(onto_ci.est_condition_clinique_de(VALUE, ci4))
héparine.is_a.append(onto_ci.a_pour_contre_indication(ONLY, one_of(ci4)))


class Condition_clinique_CI_avec_ticagrélor(onto_ci.Condition_clinique):
  equivalent_to = [
      onto_ci.Condition_clinique
    & onto_ci.est_condition_clinique_de(SOME, onto_ci.Contre_indication & onto_ci.est_contre_indication_de(VALUE, ticagrélor))]

class Condition_clinique_CI_avec_aspirine(onto_ci.Condition_clinique):
  equivalent_to = [
      onto_ci.Condition_clinique
    & onto_ci.est_condition_clinique_de(SOME, onto_ci.Contre_indication & onto_ci.est_contre_indication_de(VALUE, aspirine))]

class Condition_clinique_CI_avec_héparine(onto_ci.Condition_clinique):
  equivalent_to = [
      onto_ci.Condition_clinique
    & onto_ci.est_condition_clinique_de(SOME, onto_ci.Contre_indication & onto_ci.est_contre_indication_de(VALUE, héparine))]


class Condition_clinique_OK_avec_ticagrélor(onto_ci.Condition_clinique):
  equivalent_to = [
      onto_ci.Condition_clinique
    & NOT(onto_ci.est_condition_clinique_de(SOME, onto_ci.Contre_indication & onto_ci.est_contre_indication_de(VALUE, ticagrélor)))]

class Condition_clinique_OK_avec_aspirine(onto_ci.Condition_clinique):
  equivalent_to = [
      onto_ci.Condition_clinique
    & NOT(onto_ci.est_condition_clinique_de(SOME, onto_ci.Contre_indication & onto_ci.est_contre_indication_de(VALUE, aspirine)))]

class Condition_clinique_OK_avec_héparine(onto_ci.Condition_clinique):
  equivalent_to = [
      onto_ci.Condition_clinique
    & NOT(onto_ci.est_condition_clinique_de(SOME, onto_ci.Contre_indication & onto_ci.est_contre_indication_de(VALUE, héparine)))]


# La classe médicament est redéfinie dans le fichier onto_ci.py,
# chargée automatiquement avec l'ontologie.


onto_ci.sync_reasoner()


print()
print("CI                                     ticagrélor   aspirine   héparine")
print("maladie hémorragique                    ", ticagrélor.teste_ci(Maladie_hémorragique)                  , "         ", aspirine.teste_ci(Maladie_hémorragique)                  , "       ", héparine.teste_ci(Maladie_hémorragique))
print("maladie hémorragique acquise            ", ticagrélor.teste_ci(Maladie_hémorragique_acquise)          , "         ", aspirine.teste_ci(Maladie_hémorragique_acquise)          , "       ", héparine.teste_ci(Maladie_hémorragique_acquise))
print("maladie hémorragique constitutionnelle  ", ticagrélor.teste_ci(Maladie_hémorragique_constitutionnelle), "         ", aspirine.teste_ci(Maladie_hémorragique_constitutionnelle), "       ", héparine.teste_ci(Maladie_hémorragique_constitutionnelle))
