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


# This is a tutorial on the use of Python-specific relation names in Owlready
# (e.g. x.active_principle instead of x.has_for_active_principle).


import sys, os

from owlready import *


# Create an ontology, a few classes and a relation.

onto_test = Ontology("http://test.org/onto_test.owl")

class Drug(Thing):
  ontology = onto_test

class ActivePrinciple(Thing):
  ontology = onto_test

class has_for_active_principle(Property):
  ontology         = onto_test
  domain           = [Drug]
  range            = [ActivePrinciple]


# Defines "active_principle" as a Python-name alias for relation "has_for_active_principle".

# This is done using the 'python_name' annotation of the Owlready ontology.

# Notice that you can also set this annotation in editing tools like Protégé,
# after importing the Owlready ontology in your ontology.

# See example annotations.py if you need help with annotations in Owlready.

ANNOTATIONS[has_for_active_principle]["python_name"] = "active_principles"


acetaminophen = ActivePrinciple("acetaminophen")

doliprane = Drug("doliprane")

doliprane.active_principles = [acetaminophen]

print(doliprane.active_principles)

# However, this would raise an error:

#doliprane.has_for_active_principle


# Note that, when setting the 'python_name' annotation,
# the existing relations are *not* renamed,
# thus you should set it at the beginning of your program
# -- or, probably better, in the ontology itself.
