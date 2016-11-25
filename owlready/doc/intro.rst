Introduction
============

Owlready is a module for loading OWL 2.0 ontologies in Python. It can loads, modifies, saves ontologies, and
supports reasoning via HermiT (included). Owlready allows a transparent access to OWL ontologies (contrary
to usual Java-based API).

Owlready can:

 - Import OWL/XML ontologies (other file formats are not yet supported).

 - Manipulates ontology classes, instances and annotations as if they were Python objects.

 - Add Python methods to ontology classes.

 - Re-classify instances automatically, with the HermiT reasoner.

 - Automatically generate dialog boxes for editing ontology instances, using
   `Editobj3 <https://bitbucket.org/jibalamy/editobj3>`_.


Short example: What can I do with Owlready?
-------------------------------------------

Load an ontology from a local repository, or from Internet:

  >>> from owlready import *
  >>> onto_path.append("/path/to/your/local/ontology/repository")
  >>> onto = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl")
  >>> onto.load()  

Create new classes in the ontology, possibly mixing OWL restrictions and Python methods:

>>> class NonVegetarianPizza(onto.Pizza):
...   equivalent_to = [
...     onto.Pizza
...   & ( onto.has_topping(SOME, onto.MeatTopping)
...     | onto.has_topping(SOME, onto.FishTopping)
...     ) ]
...   def eat(self): print("Beurk! I'm vegetarian!")

Access ontology class, and create new instances / individuals:

::
   
   >>> onto.Pizza
   pizza_onto.Pizza
   
   >>> test_pizza = onto.Pizza("test_pizza_owl_identifier")
   >>> test_pizza.has_topping = [ onto.CheeseTopping(),
   ...                            onto.TomatoTopping(),
   ...                            onto.MeatTopping  () ]
   
Export to OWL/XML file:

::

  >>> onto.save()
  
Perform reasoning, and classify instances and classes:

::
  
  >>> test_pizza.__class__
  onto.Pizza
   
  >>> # Execute HermiT and reparent instances and classes
  >>> onto.sync_reasoner()
  
  >>> test_pizza.__class__
  onto.NonVegetarianPizza
  >>> test_pizza.eat()
  Beurk! I'm vegetarian !


Contact and links
-----------------

In case of trouble, please contact Jean-Baptiste Lamy <jean-baptiste.lamy *@* univ-paris13 *.* fr>

::

  LIMICS
  University Paris 13, Sorbonne Paris Cité
  Bureau 149
  74 rue Marcel Cachin
  93017 BOBIGNY
  FRANCE

Owlready on BitBucket (development repository): https://bitbucket.org/jibalamy/owlready
