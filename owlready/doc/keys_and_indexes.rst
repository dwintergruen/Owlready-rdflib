Keys and indexes
================

A Key is Property that acts as a 'key' (like 'primary key' in database) for a given Class of Individuals.

When a Key is defined in an ontology, Owlready automatically creates an index for that Key, using a Python
dict.

.. note::
   This feature corresponds to the 'target for key' attribute in Protégé.
   Protégé displays it the the Class tab while Owlready associate indexes to Propeties for optimization purpose.

Creating an index
-----------------

An indexing key is created with the .create_index() method of a Property. It takes a single parameter,
the domain Class that are indexed.

In the example below, Drug are identified by their CIP codes (a standard drug presentation code in France):

::

   >>> from owlready import *
   
   >>> onto = Ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto
   ...     def take(self): print("I took a drug")
   
   >>> class has_for_cip(FunctionalProperty):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [int]
   >>> ANNOTATIONS[has_for_cip]["python_name"] = "cip"
   
   >>> has_for_cip.create_index(Drug)
   
   >>> drug1 = Drug("drug1", cip = 2166868)
   >>> drug2 = Drug("drug2", cip = 4166507)
   >>> drug3 = Drug("drug3", cip = 3698604)
   

Using the index
---------------

The .indexes dict attribute of the Property can be use to access to the indexes Instances.
The first dict key is the domain Class indexed, and the second one is the value.

For example to get the Drug of CIP code 4166507:

::

   >>> print(has_for_cip.indexes[Drug][4166507])

.. note::

   The index can be created before or after creating the Instances,
   and it is automatically updated if the values of the Property change.

