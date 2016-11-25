Managing ontologies
===================

Creating an ontology
--------------------

A new empty ontology can be created with the Ontology class; it takes a single parameter,
the IRI of the ontology.
The IRI is a sort of URL; IRIs are used as identifier for ontologies.

::

   >>> from owlready import *
   
   >>> onto = Ontology("http://test.org/onto.owl")


.. note::
   
   It is a good idea to use the same name for the Python variable and the ontology file (without extention,
   *e.g.* 'onto' for 'onto.owl').



Loading an ontology from OWL
----------------------------

When loading an ontology from OWL file, Owlready first searches for a local copy of the OWL file and,
if not found, tries to download it from the Internet.

::

   >>> onto_path.append("/path/to/owlready/onto/")
   
   >>> owlready_ontology = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/owlready_ontology.owl").load()

The onto_path global variable contains a list of directories for searching local copies of ontologies.
It behaves similarly to sys.path for Python modules.

The get_ontology() function returns an ontology from its IRI, and creates a new ontology if needed.

The .load() method loads an ontology from a local copy or from Internet. It is **safe** to call .load() several times on the same ontology. It will be loaded only once.

.. note::
   
   **Owlready currently supports only the OWL/XML file format.** Other formats like RDFS are not supported yet.
   
   It has been tested mostly with OWL files created with the Protégé editor or with Owlready itself.


Accessing to the content of an ontology
---------------------------------------

You can access to the content of an ontology using the 'dot' notation, as usual in Python or more generally
in Object-Oriented Programming. In this way, you can access the Classes, Instances, Properties,
Annotation Properties,... defined in the ontology.

::

   >>> print(owlready_ontology.python_name)

An ontology has the following attributes:

 * .base_iri : base IRI for the ontology
 * .imported_ontologies : the list of imported ontologies (see below)
 * .classes : the list of Classes defined in the ontology (see :doc:`class`)
 * .instances : the list of Instances defined in the ontology (see :doc:`class`)
 * .properties : the list of Properties defined in the ontology (see :doc:`properties`)
 * .annotation_properties : the list of Annotation Properties defined in the ontology (see :doc:`annotations`)
 * .all_disjoints : the list of Disjointness and Distinctness defined in the ontology (see :doc:`disjoint`)

and includes the following methods:

 * .instances_of(Class) : returns an iterator listing all instances of the given Class (including subclasses) in this ontology
 * .subclasses_of(Class) : returns an iterator listing all subclasses of the given Class (recursively) in this ontology
 * .remove_unreachables(Classes_and_instances) : removes from the ontology  **ALL** classes and instances
   that are not referenced by at least one of the entities given in argument
   (recursively), and returns the list of removed entities.
   Useful for 'garbage collecting' your ontology!
   
Importing other ontologies
--------------------------

An ontology can import other ontologies, like a Python module can import other modules.

The imported_ontologies attribute of an ontology is a list of the ontology it imports. You can add
or remove items in that list:

::

   >>> onto.imported_ontologies.append(owlready_ontology)


Saving an ontology to an OWL file
---------------------------------

The .save() method of an ontology can be used to save it to an OWL/XML file.
It will be saved in the first directory in onto_path.

::

   >>> onto.save()

You can also use the to_owl() function to get an OWL string for a given ontology:

::

   >>> print(to_owl(onto))
