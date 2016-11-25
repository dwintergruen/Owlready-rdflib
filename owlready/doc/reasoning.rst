Reasoning
=========

OWL reasoners can be used to check the *consistency* of an ontology, and to deduce new fact in the ontology,
typically be *reclassing* Instances to new Classes depending on their relations.

Several OWL reasoners exist; Owlready includes a modified version of the `HermiT reasoner <http://hermit-reasoner.com/>`_,
developed by the department of Computer Science of the University of Oxford, and released under the LGPL licence.
HermiT is written in Java, and thus you need a Java Vitual Machine to perform reasoning in Owlready.

Setting up everything
---------------------

Before performing reasoning, you need to create all Classes, Properties and Instances, and
to ensure that restrictions and disjointnesses / distinctnesses have been defined too.

Here is an example creating a 'reasoning-ready' ontology:

::

   >>> from owlready import *
   
   >>> onto = Ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto
   ...     def take(self): print("I took a drug")
   
   >>> class ActivePrinciple(Thing):
   ...     ontology = onto
   
   >>> class has_for_active_principle(Property):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [ActivePrinciple]
   >>> ANNOTATIONS[has_for_active_principle]["python_name"] = "active_principles"

   >>> class Placebo(Drug):
   ...     equivalent_to = [Drug & NOT(has_for_active_principle(SOME, ActivePrinciple))]
   ...     def take(self): print("I took a placebo")

   >>> class SingleActivePrincipleDrug(Drug):
   ...     equivalent_to = [Drug & has_for_active_principle(EXACTLY, 1, ActivePrinciple)]
   ...     def take(self): print("I took a drug with a single active principle")

   >>> class DrugAssociation(Drug):
   ...     equivalent_to = [Drug & has_for_active_principle(MIN, 2, ActivePrinciple)]
   ...     def take(self): print("I took a drug with %s active principles" % len(self.active_principles))

   >>> acetaminophen   = ActivePrinciple("acetaminophen")
   >>> amoxicillin     = ActivePrinciple("amoxicillin")
   >>> clavulanic_acid = ActivePrinciple("clavulanic_acid")
   
   >>> AllDistinct(acetaminophen, amoxicillin, clavulanic_acid)

   >>> drug1 = Drug(active_principles = [acetaminophen])
   >>> drug2 = Drug(active_principles = [amoxicillin, clavulanic_acid])
   >>> drug3 = Drug(active_principles = [])

   >>> close_world(drug1)
   >>> close_world(drug2)
   >>> close_world(drug3)


Running the reasoner
--------------------

The reasoner is simply run by calling the .sync_reasoner() method of the ontology:

::

   >>> onto.sync_reasoner()


Results of the automatic classification
---------------------------------------

Owlready automatically gets the results of the reasoning from HermiT and reclassifies the Classes and Instances,
*i.e* Owlready changes the superclasses of Classes and the Classes of Instances.

::

   >>> print("drug2 new Classes:", drug2.__class__)
   drug2 new Classes: onto.DrugAssociation
   
   >>> drug1.take()
   I took a drug with a single active principle

   >>> drug2.take()
   I took a drug with 2 active principles

   >>> drug3.take()
   I took a placebo

In this example, drug1, drug2 and drug3 Classes have changed! The reasoner *deduced* that drug2 is an Association
Drug, and that drug3 is a Placebo.

Also notice how the example combines automatic classification of OWL Classes with polymorphism on Python Classes.
