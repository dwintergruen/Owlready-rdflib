Annotations
===========

In Owlready, annotations are accessed with the ANNOTATIONS pseudo-dictionary.
Annotations are **not** inherited; this is why they are not stored in the Classes or Instances, but
rather in a separate dictionary.


Adding an annotation
--------------------

For a given object 'obj' (a Class, an individual, etc), the following syntax can be used to **add an
annotation** of a given type:

::

   >>> from owlready import *
   
   >>> onto = get_ontology("http://test.org/onto.owl")
   
   >>> class Drug(Thing):
   ...     ontology = onto
   
   >>> ANNOTATIONS[Drug].add_annotation(rdfs.comment, "A comment on the Drug class")

The following annotations are available by default: rdfs.comment, rdfs.isDefinedBy, rdfs.label, rdfs.seeAlso,
owl.backwardCompatibleWith, owl.deprecated, owl.incompatibleWith, owl.priorVersion, owl.versionInfo. When
using ANNOTATIONS, annotation classes can also be identified by a string indicating their name:

::

   >>> ANNOTATIONS[Drug].add_annotation("comment", "A second comment on the Drug class")

The language can be specified (currently only supported for string annotations):

::
   
   >>> ANNOTATIONS[Drug].add_annotation((rdfs.comment, "fr"), "Un commentaire en français")

Owlready supports annotations on Classes, Instances (=Individuals), but also relation triples.

::

   >>> class HealthProblem(Thing):
   ...     ontology = onto

   >>> class is_prescribed_for(Property):
   ...     ontology = onto
   ...     domain   = [Drug]
   ...     range    = [HealthProblem]

   >>> acetaminophen = Drug("acetaminophen")
   
   >>> pain = HealthProblem("pain")
   >>> acetaminophen.is_prescribed_for.append(pain)

   >>> ANNOTATIONS[acetaminophen].add_annotation("comment", "A comment on this particular drug")
   >>> ANNOTATIONS[acetaminophen, is_prescribed_for, pain].add_annotation("comment", "A comment on a relation")

Special pseudo-properties are provided for annotating subclasses (owl.is_a), equivalence (owl.equivalent_to),
domains (owl.domain) and ranges (owl.range).

::

   >>> ANNOTATIONS[Drug, owl.is_a, Thing].add_annotation("comment", "A comment on an is-a relation")
   >>> ANNOTATIONS[is_prescribed_for, owl.domain, Drug].add_annotation("comment", "A comment on a property domain")
   >>> ANNOTATIONS[is_prescribed_for, owl.range, HealthProblem].add_annotation("comment", "A comment on a property range")


For **replacing a single existing annotation** of a given type by a new value:

::
   
   >>> ANNOTATIONS[acetaminophen]["comment"] = "This comment replaces the first existing comment on acetaminophen"


Querying annotations
--------------------

The following syntax can be used to get a list of
the annotations of a given type (given as a string or an AnnotationProperty subclass):

::

   >>> print(ANNOTATIONS[Drug][rdfs.comment])
   ['A comment on the Drug class', 'A second comment on the Drug class', 'Un commentaire en français']
   
   >>> print(ANNOTATIONS[Drug][rdfs.comment, "fr"])
   ['Un commentaire en français']

   >>> print(ANNOTATIONS[acetaminophen, is_prescribed_for, pain]["comment"])
   ['A comment on a relation']

   >>> print(ANNOTATIONS[Drug, owl.is_a, Thing]["comment"])
   ['A comment on an is-a relation']

   >>> print(ANNOTATIONS[Drug, owl.is_a, Thing].get_first("comment")
   'A comment on an is-a relation'


Iterating through annotations
-----------------------------

The following syntax can be used for iterating through **all** annotations for a given object:

::

   >>> for annotation_property, annotation_value, annotation_lang in ANNOTATIONS[Drug].items():
   ...     print(annotation_property, annotation_value, annotation_lang)
   comment This comment replaces all existing comment on the Drug class 
   comment A second comment on the Drug class 
   comment Un commentaire en français fr

'annotation_lang' defaults to an empty string if not specified.


Deleting annotations
--------------------

For removing **a given** annotation:

::
   
   >>> ANNOTATIONS[acetaminophen].del_annotation("comment", "This comment replaces all existing comment on the Drug class")


For removing **all** annotations of a given type:

::
   
   >>> del ANNOTATIONS[acetaminophen]["comment"]


Creating a new class of annotation
----------------------------------

The AnnotationProperty class can be subclasses to create a new class of annotation:

::

   >>> class my_annotation(AnnotationProperty):
   ...     ontology = onto

You can also create a subclass of an existing annotation class:

::

   >>> class pharmaceutical_comment(rdfs.comment):
   ...     ontology = onto

   >>> ANNOTATIONS[acetaminophen].add_annotation(pharmaceutical_comment, "A comment related to pharmacology of acetaminophen")

