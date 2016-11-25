Disjointness and open world assumption
======================================

By default, OWL considers the world as 'open', *i.e.* everything that is not stated in the ontology is
not 'false' but 'possible' (this is known as *open world assumption*).
Therfore, things and facts that are 'false' or 'impossible' must be clearly stated as so in the ontology.

Disjoint Classes
----------------

Two (or more) Classes are disjoint if there is no Instance belonging to all these Classes (remember that,
contrary to Python instances, an OWL Instance can have several Classes, see :doc:`class`).

A Classes disjointness is created with the AllDisjoint global function, which takes two or more Classes
as parameters. In the example below, we have two Classes, Drug and ActivePrinciple, and we assert that they
are disjoint (yes, we need to specify that explicitely -- sometimes ontologies seem a little dumb!).

::

   >>> from owlready import *
   
   >>> onto = get_ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto
   
   >>> class ActivePrinciple(Thing):
   ...     ontology = onto

   >>> AllDisjoint(Drug, ActivePrinciple)


Disjoint Properties
-------------------

OWL also introduces Disjoint Properties.
Disjoint Properties can also be created using the AllDisjoint() function.


Distinct Instances
------------------

Two Instances are distinct if they are different. In OWL, two Instances might be considered as being actually
the same single Individual, unless they are distinct.
Distinctness is to Instances what Disjointness is to Classes.

The following example creates two active principles and asserts that they are distinct (yes, we also need
to state explicitely that acetaminophen and aspirin are not the same!)

::

   >>> acetaminophen = ActivePrinciple("acetaminophen")
   >>> aspirin       = ActivePrinciple("aspirin")
   
   >>> AllDistinct(acetaminophen, aspirin)

.. note::

   In Owlready, AllDistinct is actually the same function as AllDisjoint -- the exact meaning depends on the
   parameters (AllDisjoint if you provide Classes, AllDistinct if you provide Instances,
   and disjoint Properties if you provide Properties).


Closing Instances
-----------------

The open world assumption also implies that the properties of a given Instance are not limited to the
ones that are explicitely stated. For example, if you create a Drug Instance with a single Active
Principle, it does not mean that it has *only* a single Active Principle.

::

   >>> class has_for_active_principle(Property):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [ActivePrinciple]
   
   >>> my_acetaminophen_drug = Drug(has_for_active_principle = [acetaminophen])

In the example above, 'my_acetaminophen_drug' has an acetaminophen Active Principle (this fact is true) and it
may have other Active Principle(s) (this fact is possible).

If you want 'my_acetaminophen_drug' to be a Drug with acetaminophen and no other Active Principle, you have to
state it explicitely using a restriction (see :doc:`restriction`):

::

   >>> my_acetaminophen_drug.is_a.append(has_for_active_principle(ONLY, one_of(acetaminophen)))

Notice that we used one_of() to 'turn' the acetaminophen Instance into a Class that we can use in the restriction.

You'll quickly find that the open world assumption often leads to tedious and long lists
of AllDistincts and Restrictions. Hopefully, Owlready provides the close_world() function for automatically
'closing' an instance. close_world() will automatically add ONLY restriction as needed; it accepts an
optional parameter: a list of the Properties to 'close' (defaults to all Properties whose domain is
compatible with the Instance).

::

   >>> close_world(my_acetaminophen_drug)

If you want to close the whole world, this can be done as following:

::

   >>> onto.add(AllDistinct(*onto.instances))
   >>> for instance in onto.instances:
   ...     close_world(instance)

  
   
