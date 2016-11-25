Limitations
===========

Current limits
--------------

The following limitions currently apply to Owlready (but may be fixed in future version):

 * Owlready supports only OWL/XML file format.
   
 * Owlready loads ontology in memory
   (might be problematic for very big ontologies).
   
 * Owlready associates each entity to a single ontology when saving OWL files, while OWL
   allows to spread the various facts and assertions in several ontologies.
   
 * Owlready does not take into account subproperties when obtaining the values
   of a property  (unless using get_relation()).

 * Owlready does not support 'punning', and the same name should not be used
   for two distinct entities, even if their types differ (e.g. a class and a property).

 * Instance edition is still experimental (especially the HTML support).
