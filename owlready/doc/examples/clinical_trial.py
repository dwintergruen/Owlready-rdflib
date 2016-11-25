# -*- coding: utf-8 -*-
# Owlready
# Copyright (C) 2013-2014 Jean-Baptiste LAMY
# LIMICS (Laboratoire d'informatique médicale et d'ingénierie des connaissances en santé), UMR_S 1142
# University Paris 13, Sorbonne paris-Cité, Bobigny, France

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# This is a more complex example on drug clinical trials.

import sys, os

from owlready import *

onto_test = Ontology("http://test.org/onto_test.owl")

class ClinicalTrial(Thing):
  ontology = onto_test

class Arm(Thing):
  ontology = onto_test

class DrugIntervention(Thing):
  ontology = onto_test

class PlaceboDrugIntervention(DrugIntervention):
  ontology = onto_test

class NonPlaceboDrugIntervention(DrugIntervention):
  ontology = onto_test

DrugIntervention.is_a.append(PlaceboDrugIntervention | NonPlaceboDrugIntervention)
AllDisjoint(PlaceboDrugIntervention, NonPlaceboDrugIntervention)

class has_arm(InverseFunctionalProperty):
  ontology = onto_test
  domain   = [ClinicalTrial]
  range    = [Arm]

class belongs_to_clinical_trial(FunctionalProperty):
  ontology         = onto_test
  domain           = [Arm]
  range            = [ClinicalTrial]
  inverse_property = has_arm

class has_trial_code(FunctionalProperty):
  ontology = onto_test
  domain   = [ClinicalTrial]
  range    = [normstr]
  
class has_drug_intervention(Property):
  ontology = onto_test
  domain   = [Arm]
  range    = [DrugIntervention]
  
class prescribed_to_arm(Property):
  ontology         = onto_test
  domain           = [DrugIntervention]
  range            = [Arm]
  inverse_property = has_drug_intervention
  
class has_drug(FunctionalProperty):
  ontology = onto_test
  domain   = [DrugIntervention]
  range    = [normstr]

class has_daily_dose(FunctionalProperty):
  ontology = onto_test
  domain   = [DrugIntervention]
  range    = [float]


Arm.is_a.append(restriction("has_drug_intervention", SOME, DrugIntervention))

ClinicalTrial.is_a.append(restriction("has_arm", SOME, NOT(restriction("has_drug_intervention", SOME, PlaceboDrugIntervention))))

class ComparativeClinicalTrial(ClinicalTrial):
  equivalent_to = [
    ClinicalTrial & restriction("has_arm", MIN, 2, Arm),
    ]

class NonComparativeClinicalTrial(ClinicalTrial):
  equivalent_to = [
    ClinicalTrial & restriction("has_arm", EXACTLY, 1, Arm),
    ]

ClinicalTrial.equivalent_to.append(ComparativeClinicalTrial | NonComparativeClinicalTrial)

class ClinicalTrialAgainstPlacebo(ClinicalTrial):
  equivalent_to = [
    ClinicalTrial & restriction("has_arm", SOME, restriction("has_drug_intervention", SOME, PlaceboDrugIntervention)),
    ]


AllDisjoint(ClinicalTrial, Arm, DrugIntervention)
AllDisjoint(ComparativeClinicalTrial, NonComparativeClinicalTrial)


      
# Clinical trial #1 has a single arm.

clinical_trial_1 = ClinicalTrial("clinical_trial_1", has_trial_code = "1")

arm_1 = Arm("arm_1")
drug_intervention_1 = NonPlaceboDrugIntervention("drug_intervention_1", has_drug = "drug_A", has_daily_dose = 100.0)
arm_1.has_drug_intervention.append(drug_intervention_1)

clinical_trial_1.has_arm.append(arm_1)

drug_intervention_1.closed_world()
arm_1.closed_world()
clinical_trial_1.closed_world()

# Equivalent to :
#arm_1.is_a.append(restriction(has_drug_intervention, ONLY, one_of(drug_intervention_1)))
#clinical_trial_1.is_a.append(restriction(has_arm, ONLY, one_of(arm_1)))
#...


# Clinical trial #2 compares two drugs.

clinical_trial_2 = ClinicalTrial("clinical_trial_2", has_trial_code = "2")

arm_2_1 = Arm("arm_2_1")
drug_intervention_2_1 = NonPlaceboDrugIntervention("drug_intervention_2_1", has_drug = "drug_A", has_daily_dose = 100.0)
arm_2_1.has_drug_intervention.append(drug_intervention_2_1)
clinical_trial_2.has_arm.append(arm_2_1)

arm_2_2 = Arm("arm_2_2")
drug_intervention_2_2 = NonPlaceboDrugIntervention("drug_intervention_2_2", has_drug = "drug_B", has_daily_dose = 200.0)
arm_2_2.has_drug_intervention.append(drug_intervention_2_2)
clinical_trial_2.has_arm.append(arm_2_2)

drug_intervention_2_1.closed_world()
drug_intervention_2_2.closed_world()
arm_2_1.closed_world()
arm_2_2.closed_world()
clinical_trial_2.closed_world()

# Equivalent to :
#clinical_trial_2.is_a.append(restriction(has_arm, ONLY, one_of(arm_2_1, arm_2_2)))
#...


# Clinical trial #2 compares a drug to a placebo.

clinical_trial_3 = ClinicalTrial("clinical_trial_3", has_trial_code = "3")

arm_3_1 = Arm("arm_3_1")
drug_intervention_3_1 = NonPlaceboDrugIntervention("drug_intervention_3_1", has_drug = "drug_A", has_daily_dose = 100.0)
arm_3_1.has_drug_intervention.append(drug_intervention_3_1)
clinical_trial_3.has_arm.append(arm_3_1)

arm_3_2 = Arm("arm_3_2")
drug_intervention_3_2 = PlaceboDrugIntervention("drug_intervention_3_2", has_drug = "placebo", has_daily_dose = 100.0)
arm_3_2.has_drug_intervention.append(drug_intervention_3_2)
clinical_trial_3.has_arm.append(arm_3_2)

clinical_trial_3.has_arm.append(arm_3_2)

drug_intervention_3_1.closed_world()
arm_3_1.closed_world()
arm_3_2.closed_world()
clinical_trial_3.closed_world()

onto_test.add(AllDisjoint(clinical_trial_1, clinical_trial_2, clinical_trial_3))
onto_test.add(AllDisjoint(arm_1, arm_2_1, arm_2_2, arm_3_1, arm_3_2))
onto_test.add(AllDisjoint(drug_intervention_1, drug_intervention_2_1, drug_intervention_2_2, drug_intervention_3_1))

onto_path.append(os.path.dirname(__file__))
onto_test.save()

onto_test.sync_reasoner()

# The reasoner find that:

# * clinical_trial_1 is a non comparative trial
# * clinical_trial_2 is a comparative trial
# * clinical_trial_3 is a trial against placebo

# * ClinicalTrialAgainstPlacebo is a ComparativeClinicalTrial


