Restrictions
============

Restrictions are special type of Classes in ontology.

Restrictions on a Property
--------------------------

::

   >>> from owlready import *
   
   >>> onto = Ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto
   
   >>> class ActivePrinciple(Thing):
   ...     ontology = onto
   
   >>> class has_for_active_principle(Property):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [ActivePrinciple]

For example, a Placebo is a Drug with no Active Principle:

::

   >>> class Placebo(Drug):
   ...     equivalent_to = [Drug & NOT(has_for_active_principle(SOME, ActivePrinciple))]

In the example above, 'has_for_active_principle(SOME, ActivePrinciple)' is the Class of all
objects that have at least one Active Principle. The NOT() function returns the negation of a Class.
The & operator returns the intersection of two Classes.

Another example: an Association Drug is a Drug that associates two or more Active Principle:

::

   >>> class DrugAssociation(Drug):
   ...     equivalent_to = [Drug & has_for_active_principle(MIN, 2, ActivePrinciple)]

Owlready provides the following types of restrictions (they have the same names than in Protégé):

 * some : property(SOME, Range Class)
 * only : property(ONLY, Range Class)
 * min : property(MIN, cardinality, Range Class)
 * max : property(MAX, cardinality, Range Class)
 * exactly : property(EXACTLY, cardinality, Range Class)
 * value : property(VALUE, Range Instance)


Class operators
---------------

Owlready provides the following operators between Classes (normal Classes but also restrictions):

 * & : and operator (intersection). For example: Class1 & Class2
 * | : or operator (union). For example: Class1 | Class2
 * NOT() : not operator (negation). For example: NOT(Class1)


One-Of constructs
-----------------

In ontologies, a 'One Of' statement is used for defining a Class by extension, *i.e.* by listing its Instances
rather than by defining its properties.

::
   
   >>> class DrugForm(Thing):
   ...     ontology = onto
   
   >>> tablet     = DrugForm()
   >>> capsule    = DrugForm()
   >>> injectable = DrugForm()
   >>> pomade     = DrugForm()

   # Assert that there is only four drug forms possible
   >>> DrugForm.is_a.append(one_of(tablet, capsule, injectable, pomade))
   

