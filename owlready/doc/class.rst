Classes and Instances (Individuals)
===================================

Creating a Class
----------------

A new Class can be created in an ontology by inheriting the owlready.Thing class.

The ontology class attribute can be used to associate your class to the given ontology. If not specified,
this attribute is inherited from the parent class (in the example below, the parent class is Thing,
which is defined in the 'owl' ontology).

::

   >>> from owlready import *
   
   >>> onto = get_ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto


Creating subclasses
-------------------

Subclasses can be created by inheriting an ontology class. Multiple inheritance is supported.

::

   >>> class DrugAssociation(Drug): # A drug associating several active principles
   ...     pass

Owlready provides the .is_a attribute for getting the list of superclasses (__bases__ can be used, but
with some limits described in :doc:`restriction`). It can also be modified for adding or removing superclasses.

::

   >>> print(DrugAssociation.is_a)
   [Drug]


Creating classes dynamically
----------------------------

The 'types' Python module can be used to create classes and subclasses dynamically:

::

   >>> import types

   >>> NewClass = types.new_class("NewClassName", (SuperClass,), kwds = { "ontology" : my_ontology })

   
Creating equivalent classes
---------------------------

The .equivalent_to Class attribute is a list of equivalent classes. It behaves similarly to .is_a.


Creating Instances
------------------

Instances are usually called Individuals in ontologies. They are created as any other Python class.
The first parameter is the name (or identifier) of the Instance; it corresponds to the 'name' attribute in Owlready.
If not given, the name if automatically generated from the Class name and a number.

::

   >>> my_drug = Drug("my_drug")
   >>> print(my_drug.name)
   my_drug

   >>> unamed_drug = Drug()
   >>> print(unamed_drug.name)
   drug_1

Additional keyword parameters can be given when creating an Instance, and they will be associated to the
corresponding Properties (for more information on Properties, see :doc:`properties`).

::

   my_drug = Drug("my_drug2", ontology = onto, has_for_active_principle = [],...)


The Instances are immediately available in the ontology:

::

   >>> print(onto.drug_1)

The .instances() class method can be used to iterate through all Instances of a Class (including its
subclasses):

::

   >>> for i in Drug.instances(): print(i)


Mutli-Class Instances
---------------------

In ontology, an Instance is allowed to have more than one Class. This is supported in Owlready; you need
to create the Instance as a single-Class Instance first, and then to add the other Class(ses) in
its .is_a attribute:

::

   >>> class BloodBasedProduct(Thing):
   ...     ontology = onto

   >>> a_blood_based_drug = Drug()
   >>> a_blood_based_drug.is_a.append(BloodBasedProduct)

Owlready will automatically create a hidden Class that inherits from both Drug and BloodBasedProduct. This
hidden class is visible in a_blood_based_drug.__class__, but not in a_blood_based_drug.is_a.
   
