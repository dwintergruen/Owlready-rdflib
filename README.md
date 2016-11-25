Owlready-rdflib

This is an extension of Owlready
https://pypi.python.org/pypi/Owlready

which adds the support of rdflib to the library:

It adds a .to_rdflib method.

Currently its not very well tested.

Example:

    g = rdflib.Graph(store=store,identifier="http://entities.mpiwg-berlin.mpg.de/graphs/gr/V14TEST")
    g.store.setCredentials('admin','admin')
    g.store.setHTTPAuth('DIGEST')
    owlready.to_rdflib(scholars_ontology,g)



Owlready
========

Owlready (previously named Ontopy) is a module for ontology-oriented programming in Python 3.

Owlready can:

 - Import and export OWL 2.0 ontologies in the OWL/XML format
   (other file formats are not yet supported).

 - Manipulates ontology classes, instances and properties transparently,
   as if they were normal Python objects.

 - Add Python methods to ontology classes.

 - Perform automatic classification of classes and instances, using the HermiT reasoner.

 - Automatically generate dialog boxes for editing ontology instances,
   using `Editobj3 <http://www.lesfleursdunormal.fr/static/informatique/editobj/index_en.html>`_.

Owlready has been created by Jean-Baptiste Lamy at the LIMICS reseach lab.
It is available under the GNU LGPL licence v3.
In case of trouble, please contact Jean-Baptiste Lamy
<jean-baptiste.lamy *@* univ-paris13 *.* fr>

::

  LIMICS
  University Paris 13, Sorbonne Paris Cité
  Bureau 149
  74 rue Marcel Cachin
  93017 BOBIGNY
  FRANCE


What can I do with Owlready?
----------------------------

Load an ontology from a local repository, or from Internet:

  >>> from owlready import *
  >>> onto_path.append("/path/to/your/local/ontology/repository")
  >>> onto = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl")
  >>> onto.load()

Create new classes in the ontology, possibly mixing OWL restrictions and Python methods:

  >>> class NonVegetarianPizza(onto.Pizza):
  ...   equivalent_to = [
  ...     onto.Pizza
  ...   & ( restriction("has_topping", SOME, onto.MeatTopping)
  ...     | restriction("has_topping", SOME, onto.FishTopping)
  ...     ) ]
  ...   def eat(self): print("Beurk! I'm vegetarian!")

Access ontology class, and create new instances / individuals:

  >>> onto.Pizza
  pizza_onto.Pizza
  >>> test_pizza = onto.Pizza("test_pizza_owl_identifier")
  >>> test_pizza.has_topping = [ onto.CheeseTopping(),
  ...                            onto.TomatoTopping(),
  ...                            onto.MeatTopping  () ]

Export to OWL/XML file:

  >>> test_onto.save()

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

For more documentation, look at the doc/ and doc/examples/ directories in the source.

Changelog
---------

0.2
***

* Fix sync_reasonner and Hermit call under windows (thanks Clare Grasso)

0.3
***

* Add warnings
* Accepts ontologies files that do not ends with '.owl'
* Fix a bug when loading ontologies including concept without a '#' in their IRI


Links
-----

Owlready on BitBucket (development repository): https://bitbucket.org/jibalamy/owlready

Owlready on PyPI (Python Package Index, stable release): https://pypi.python.org/pypi/Owlready

Documentation: http://pythonhosted.org/Owlready

Mail me for any comment, problem, suggestion or help !

Jiba -- Jean-Baptiste LAMY -- jibalamy @ free.fr
