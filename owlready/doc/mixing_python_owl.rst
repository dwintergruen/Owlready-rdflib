Mixing Python and OWL
=====================

Adding Python methods to an OWL Class
-------------------------------------

Python methods can be defined in ontology Classes as usual in Python. In the example below, the Drug Class
has a Python method for computing the per-tablet cost of a Drug, using two OWL Properties (which have been
renamed in Python, see :ref:`associating-python-alias-name-to-properties`):

::

   >>> from owlready import *
   
   >>> onto = Ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto
   ...     def get_per_tablet_cost(self):
   ...         return self.cost / self.number_of_tablets
   
   >>> class has_for_cost(FunctionalProperty):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [float]
   >>> ANNOTATIONS[has_for_cost]["python_name"] = "cost"
   
   >>> class has_for_number_of_tablets(FunctionalProperty):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [int]
   >>> ANNOTATIONS[has_for_number_of_tablets]["python_name"] = "number_of_tablets"
   
   >>> my_drug = Drug("my_drug", cost = 10.0, number_of_tablets = 5)
   >>> print(my_drug.get_per_tablet_cost())
   2.0


Generating Instance names
-------------------------

The Instances OWL name (or identifier) can also be generated in Python, from the relations of the Instance.
The Class must inherit from the special Class GeneratedName, and it must have a .generate_name() method.

::

   >>> class Drug(GeneratedName, Thing):
   ...     ontology = onto
   ...     def generate_name(self):
   ...         return "drug_with_%s" % "_and_".join(sorted(ai.name for ai in self.active_principles))

   >>> class ActivePrinciple(Thing):
   ...     ontology = onto

   >>> class has_for_active_principle(Property):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [ActivePrinciple]
   >>> ANNOTATIONS[has_for_active_principle]["python_name"] = "active_principles"

   >>> amoxicillin     = ActivePrinciple("amoxicillin")
   >>> clavulanic_acid = ActivePrinciple("clavulanic_acid")
   >>> my_drug       = Drug()
   >>> my_drug.active_principles = [amoxicillin, clavulanic_acid]

   >>> print(my_drug.name)
   drug_with_amoxicillin_and_clavulanic_acid

Notice the use of sorted() when generating the name: it is often a good idea to have constant
and order-independent names.

Owlready garenteers the uniqueness of the generated names, and will add "_2", "_3", and so on if needed.

Forward declarations
--------------------

Sometimes, you may need to forward-declare a Class or a relation.
This can be done with the @forward_declaration decorator:

::

   >>> @forward_declaration
   >>> class has_for_active_principle(Property): pass
   
   # This definition of drug exclude Placebo, and requires the has_for_active_principle Property
   >>> class Drug(Thing):
   ...     ontology = onto
   ...     is_a = [has_for_active_principle(SOME, ActivePrinciple)]
   
   # This is the final declaration of the Property
   >>> class has_for_active_principle(Property):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [ActivePrinciple]


Associating a Python module to an OWL ontology
----------------------------------------------

It is possible to associate a Python module with an OWL ontology. When Owlready loads the ontology,
it will automatically import the Python module.
This is done with the 'python_module' annotation, which should be set on the ontology itself.
The value should be the name of your Python module, *e.g.* 'my_package.my_module'.
This annotation can be set with editor like Protégé, after importing the 'owlready_ontology.owl' ontology:

.. figure:: _images/protege_python_module_annotation.png

The Python module can countain Class and Properties definitions, and methods.
However, it does not need to include all the is-a relations, domain, range,...: any such relation
defined in OWL does not need to be specified in Python. Therefore, if your Class hierarchy is
defined in OWL, you can create all Classes as child of Thing.

For example, in file 'my_python_module.py':

::

   >>> from owlready import *
   
   >>> onto = Ontology("http://test.org/onto.owl")
   
   >>> class Drug(GeneratedName, Thing):
   ...     ontology = onto
   ...     def generate_name(self):
   ...         return "drug_with_%s" % "_and_".join(sorted(ai.name for ai in self.active_principles))
   
   >>> class has_for_active_principle(Property):
   ...     ontology = onto

And then, in OWL file 'onto.owl', you can define:

 * The 'python_module' annotation (value: 'my_python_module')
 * The 'has_for_active_principle' Property with its domain and range
 * The 'ActivePrinciple' Class (ommitted above -- not needed)

In this way, Onotopy allows you to take the best of Python and OWL!
