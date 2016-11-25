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


# This is a tutorial on the use of annotations in Owlready.


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


# Annotations can be get and set through the ANNOTATIONS pseudo-dictionary.
# The following example shows how to add an annotations. 'Drug' is the annotated object,
# and rdfs.comment the class of annotation (you may also use a string like "comment").

ANNOTATIONS[Drug].add_annotation(rdfs.comment, "My first comment on Drug in general.")

# Add a second one:

ANNOTATIONS[Drug].add_annotation(rdfs.comment, "My second comment on Drug in general.")

# Add a third one in French language:

ANNOTATIONS[Drug].add_annotation((rdfs.comment, "fr"), "Un commentaire en français.")


# Shows all annotations related to Drug:

print(ANNOTATIONS[Drug])

# Extract all comment annotations related to Drug:

print(ANNOTATIONS[Drug][rdfs.comment])

# Extract all comment annotations related to Drug in French language:

print(ANNOTATIONS[Drug][rdfs.comment, "fr"])


# Remove specific comments:

ANNOTATIONS[Drug].del_annotation(rdfs.comment, "My first comment on Drug in general.")
ANNOTATIONS[Drug].del_annotation((rdfs.comment, "fr"), "Un commentaire en français.")

# Remove all French comment on 'Drug':

del ANNOTATIONS[Drug][rdfs.comment, "fr"]

# Remove all comment on 'Drug':

del ANNOTATIONS[Drug][rdfs.comment]


# Creates an individuals / instances, and annotates it:

acetaminophen = ActivePrinciple("acetaminophen")

ANNOTATIONS[acetaminophen].add_annotation(rdfs.comment, "A comment on acetaminophen.")


# Creates a new class of annotation:

class alternative_name(AnnotationProperty):
  ontology = onto_test
 
 
# Add a new annotation using the new 'alternative_name' annotation class.
# This syntax with '=' behaves slighly differently than the add_annotation method: it replaces
# any existing annotation of the same class before adding the new one.

ANNOTATIONS[acetaminophen][alternative_name, "fr"] = "paracétamol"

print(ANNOTATIONS[acetaminophen])


# Create a Drug individuals, and a relation:

doliprane = Drug("doliprane")
doliprane.has_for_active_principle = [acetaminophen]


# Annotates the relation:

ANNOTATIONS[doliprane, has_for_active_principle, acetaminophen].add_annotation(rdfs.comment, "A comment about the triple (doliprane, has_for_active_principle, acetaminophen).")

print(ANNOTATIONS[doliprane, has_for_active_principle, acetaminophen])


# Creates a drug subclass.

class DrugAssociation(Drug):
  pass


# Annotates the is-a relation between 'DrugAssociation' and 'Drug',
# using the owl.is_a pseudo Property class.

# Similarly, equivalent classes, ranges and domains can be annotated
# using the owl.equivalent_to, owl.range and owl.domain pseudo Property class.

ANNOTATIONS[DrugAssociation, owl.is_a, Drug].add_annotation(rdfs.comment, "A comment about an is-a relation.")

print(ANNOTATIONS[DrugAssociation, owl.is_a, Drug])


# Creates a subclass of the 'comment' annotation class:

class pharmaceutical_comment(rdfs.comment):
  pass

ANNOTATIONS[acetaminophen].add_annotation(pharmaceutical_comment, "A comment related to pharmacology of acetaminophen.")

# Print acetaminophen's comments -- notice that pharmaceutical_comment are considered as comment,
# and thus listed too.

print(ANNOTATIONS[acetaminophen][rdfs.comment])
