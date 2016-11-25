Properties
==========



Creating a new class of property
--------------------------------

A new property can be created by sublcassing the Property class.
The 'domain' and 'range' properties can be used to specify the domain and the range of the property.
Domain and range must be given in list, since OWL allows to specify several domains or ranges for a given
property (if multiple domains or ranges are specified, the domain or range is the intersection of them,
*i.e.* the items in the list are combined with an 'and' operator).

::

   >>> from owlready import *
   
   >>> onto = Ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto

   >>> class Ingredient(Thing):
   ...     ontology = onto
   
   >>> class has_for_ingredient(Property):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [Ingredient]

The following subclasses of Property are available: FunctionalProperty, InverseFunctionalProperty,
TransitiveProperty, SymmetricProperty, AsymmetricProperty, ReflexiveProperty, IrreflexiveProperty.


Creating a relation
-------------------

A relation is a triple (subject, property, object) where property is a Property class, and subject and object
are instances which are subclasses of the domain and range defined for the property class.
A relation can be get or set using Python attribute of the subject, the attribute name being the same as
the Property class name: 

::

   >>> my_drug = Drug("my_drug")
   
   >>> acetaminophen = Ingredient("acetaminophen")
   
   >>> my_drug.has_for_ingredient.append(acetaminophen)

The attribute contains a list of the subjects:

::

   >>> print(my_drug.has_for_ingredient)
   [onto.acetaminophen]


Data Property
-------------

Contrary to OWL, Owlready does not distinguish between ObjectProperty and DataProperty,
because everything is object in Python,
and Owlready aims at providing a transparent access to ontology in Python.
Data Properties are simply a Property with a data type in their range. The following data types
are currently supported by Owlready:

 * int
 * float
 * bool
 * str (string)
 * owlready.normstr (a single-line string)
 * datetime.date
 * datetime.time
 * datetime.datetime

Here is an example of a string Data Property:

::

   >>> class has_for_synonym(Property):
   ...     ontology = onto
   ...     range    = [str]

   >>> acetaminophen.has_for_synonym = ["acetaminophen", "paracétamol"]

.. note::
   
   If you really need to create a range-less DataProperty in Owlready, you can use a very broad range, *e.g.*:

   ::

      >>> class my_rangeless_data_property(Property):
      ...     range = [OrRestriction(int, float, str, bool)] # int or float or str or bool


Inverse properties
------------------

Two properties are inverse if they express the same meaning, but in a reversed way. 
For example the 'is_ingredient_of' Property is the inverse of the 'has_for_ingredient' Property created above:
saying "a drug A has for ingredient B" is equivalent to "B is ingredient of drug A".

In Owlready, Inverse Properties are defined using the 'inverse_property' attribute.

::

   >>> class is_ingredient_of(Property):
   ...     ontology         = onto
   ...     domain           = [Ingredient]
   ...     range            = [Drug]
   ...     inverse_property = has_for_ingredient

Owlready automatically handles Inverse Properties. It will automatically set has_for_ingredient.inverse_property,
and automatically update relations when the inverse relation is modified.

::

   >>> my_drug2 = Drug("my_drug2")
   
   >>> aspirin = Ingredient("aspirin")
   
   >>> my_drug2.has_for_ingredient.append(aspirin)
   
   >>> print(my_drug2.has_for_ingredient)
   [onto.aspirin]
   
   >>> print(aspirin.is_ingredient_of)
   [onto.my_drug2]


   >>> aspirin.is_ingredient_of = []

   >>> print(my_drug2.has_for_ingredient)
   []

.. note::

   This won't work for the acetaminophen drug created previously, because we created the inverse property
   **after** we created the relation between my_drug and acetaminophen.


Functional and Inverse Functional properties
--------------------------------------------

A functional property is a property that has a single value for a given instance. Functional properties
are created by inheriting the FunctionalProperty class. The default value is None for Object Properties,
0 for numbers, False for boolean and "" for strings.

::

   >>> class has_for_cost(FunctionalProperty): # Each drug has a single cost
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [float]
   
   >>> acetaminophen.has_for_cost = 4.2
   
   >>> print(acetaminophen.has_for_cost)
   4.2

An Inverse Functional Property is a property whose inverse property is functional.
They are created by inheriting the InverseFunctionalProperty class.


Creating a subproperty
----------------------

A subproperty can be created by subclassing a Property class.

::

   >>> class ActivePrinciple(Ingredient):
   ...     ontology = onto
   
   >>> class has_for_active_principle(has_for_ingredient):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [ActivePrinciple]

.. note::
   
   Owlready currently does not automatically update parent properties when a child property is defined.
   This might be added in a future version, though.

   If you need this feature, use the get_relations() global function:

   ::
      
      >>> print(get_relations(my_drug, has_for_ingredient)) # List also has_for_active_principle!


.. _associating-python-alias-name-to-properties:

Associating Python alias name to Properties
-------------------------------------------

In ontologies, properties are usually given long names, *e.g.* "has_for_ingredient", while in programming
languages like Python, shorter attribute names are more common, *e.g.* "ingredients" (notice also the use
of a plural form, since it is actually a list of ingredients).

Owlready allows to rename Properties with more Pythonic name through the 'python_name' annotation (defined
in the Owlready ontology):

::

   >>> ANNOTATIONS[has_for_ingredient]["python_name"] = "ingredients"
   
   >>> my_drug3 = Drug("my_drug3")
   
   >>> cetirizin = Ingredient("cetirizin")
   
   >>> my_drug3.ingredients.append(cetirizin)
   
.. note::
   
   The Property class is still considered to be called 'has_for_ingredient', for example it is still
   available as 'onto.has_for_ingredient', but not as 'onto.ingredients'.

For more information about how to use annotations, see :doc:`annotations`.

The 'python_name' annotations can also be set in ontology editors like Protégé, by importing the Owlready
ontology (file 'owlready/owlready_ontology.owl' in Owlready sources).
