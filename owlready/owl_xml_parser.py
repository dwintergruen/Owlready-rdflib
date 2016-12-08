# -*- coding: utf-8 -*-
# Owlready
# Copyright (C) 2013-2014 Jean-Baptiste LAMY
# LIMICS (Laboratoire d'informatique médicale et d'ingénierie des connaissances en santé), UMR_S 1142
# University Paris 13, Sorbonne paris-Cité, Bobigny, France

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, warnings
import xml, xml.sax as sax, xml.sax.handler
from collections import defaultdict

import owlready
from owlready import *

_TAG_2_PROP_TYPE = {}
_TAG_2_REST_TYPE = {}
for (key, value) in owlready._TYPE_2_TAG.items():
  _TAG_2_REST_TYPE["Object%s" % value] = key
  _TAG_2_REST_TYPE["Data%s"   % value] = key
for Prop in owlready._TYPES:
  _TAG_2_PROP_TYPE[Prop.name.replace("Property", "ObjectProperty")] = _TAG_2_PROP_TYPE[Prop.name.replace("Property", "DataProperty")] = Prop

def _parse_datatype(datatype, s, lang = ""):
  if datatype is bool:               return s.lower() != "false"
  if datatype is datetime.datetime:  return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
  if datatype is datetime.date:      return datetime.datetime.strptime(s, "%Y-%m-%d").date()
  if datatype is datetime.time:      return datetime.datetime.strptime(s, "T%H:%M:%S").time()
  return datatype(s)

class OWLXMLHandler(sax.handler.ContentHandler):
  def __init__(self, ontology = None):
    self.objs                   = []
    self.annots                 = []
    self.current_content        = u""
    self.ontology               = ontology or Ontology("", "")
    self.prefixes               = {}
    self.relations              = []
    self.ontologies_to_import   = []
    self.current_lang           = None
    self.datatype_properties    = set()
  
  def push_value    (self, value): self.objs.append(value)
  def push_obj      (self, attrs, type): self.objs.append(self.ontology.get_object(self.get_IRI(attrs), type))# self,base_iri=self.base_iri))
  def push_anonymous(self, attrs, type): self.objs.append(anonymous.get_object(attrs["nodeID"], type, self))
  
  def unabbreviate_IRI(self, abbreviated_iri):
    prefix, name = abbreviated_iri.split(":", 1)
    return self.prefixes[prefix] + name
  
  def get_IRI(self, attrs):
    if "IRI" in attrs: return attrs["IRI"]
    return self.unabbreviate_IRI(attrs["abbreviatedIRI"])
  
  def get_loc(self): return self._locator.getSystemId(), self._locator.getLineNumber(), self._locator.getColumnNumber()
  
  def startElement(self, tag, attrs):
    self.current_content = u""
    if   (tag == "Prefix"): self.prefixes[attrs["name"]] = attrs["IRI"]
    #hole iri aus dem Ontology file
    elif (tag == "Ontology"):
        self.ontology.ontologyIRI=attrs["ontologyIRI"]
        
    elif (tag == "Class"):
      self.push_obj(attrs, ThingClass)
      if not isinstance(self.objs[-1], ThingClass): raise ValueError("'Punning' detected for %s (there is both a class and an individual with the same IRI); punning is not supported by OwlReady." % self.objs[-1])
      
    elif (tag == "NamedIndividual"):
      self.push_obj(attrs, Thing)
      if not isinstance(self.objs[-1], Thing): raise ValueError("'Punning' detected for %s (there is both a class and an individual with the same IRI); punning is not supported by OwlReady." % self.objs[-1])
      
    elif (tag == "ObjectProperty"):     self.push_obj(attrs, PropertyClass)
    elif (tag == "DataProperty"):       self.push_obj(attrs, PropertyClass); self.datatype_properties.add(self.objs[-1])
    elif (tag == "AnnotationProperty"): self.push_obj(attrs, AnnotationPropertyClass)
    elif (tag == "Datatype"):           self.push_value(owlready._DATATYPES_2_PYTHON[self.get_IRI(attrs)])
    elif (tag == "Literal"):            self.push_value(attrs["datatypeIRI"]); self.current_lang = attrs.get("xml:lang", "")
    
    elif((tag == "ObjectIntersectionOf") or (tag == "ObjectUnionOf") or (tag == "ObjectOneOf") or
         (tag == "DataIntersectionOf") or (tag == "DataUnionOf") or
         (tag == "DisjointClasses") or (tag == "DisjointObjectProperties") or (tag == "DisjointDataProperties") or (tag == "DifferentIndividuals")):
      self.push_value("(")
      
    elif((tag == "ObjectExactCardinality") or (tag == "ObjectMinCardinality") or (tag == "ObjectMaxCardinality") or
         (tag == "DataExactCardinality"  ) or (tag == "DataMinCardinality"  ) or (tag == "DataMaxCardinality"  )):
      self.push_value("(")
      self.last_cardinality = int(attrs["cardinality"])
      
    elif (tag == "AnonymousIndividual"): self.push_anonymous(attrs, Thing)
    
    elif (tag == "AnnotationAssertion") or (tag == "Annotation"): self.current_lang = None
    
    elif (tag == "RDF") or (tag == "rdf:RDF"): raise ValueError("OwlReady does not support OWL/RDF format. Please use OWL/XML.")
    
  def endElement(self, tag):
    if   (tag == "Literal"):
      self.objs[-1] = _parse_datatype(owlready._DATATYPES_2_PYTHON[self.objs[-1]], self.current_content, self.current_lang)
      
    elif (tag == "SubClassOf") or (tag == "SubObjectPropertyOf") or (tag == "SubDataPropertyOf") or (tag == "SubAnnotationPropertyOf"):
     
      parent = self.objs.pop()
      child  = self.objs.pop()
      if isinstance(parent, EntityClass) and issubclass(parent, child): # Cycle detected!
        parent.equivalent_to.append(child)
        child .equivalent_to.append(parent)
      else:
        if not (isinstance(parent, EntityClass) and (issubclass(child, parent) or issubclass(child, parent))): # Some relations might be stated twice
          child.is_a.append(parent)
      self.purge_annotations((child, owl.is_a, parent))
      
    elif (tag == "ClassAssertion"):
      child  = self.objs.pop() # Order is reversed compared to SubClassOf!
      parent = self.objs.pop()
      if not isinstance(child, Thing):
        raise ValueError("%s is not an individual but there is a ClassAssertion with class %s !" % (child, parent))
        assert False
      child.is_a.append(parent)
      self.purge_annotations((child, owl.is_a, parent))
      
    elif (tag == "EquivalentClasses") or (tag == "EquivalentObjectProperties") or (tag == "EquivalentDataProperties"):
      o1 = self.objs.pop()
      o2 = self.objs.pop()
      if isinstance(o2, Restriction): o2, o1 = o1, o2
      o2.equivalent_to.append(o1)
      self.purge_annotations((o2, owl.equivalent_to, o1))
      
    elif (tag == "ObjectPropertyDomain") or (tag == "DataPropertyDomain") or (tag == "AnnotationPropertyDomain"):
      val = self.objs.pop(); obj = self.objs.pop();
      obj.domain.append(val)
      self.purge_annotations((obj, owl.domain, val))
      
    elif (tag == "ObjectPropertyRange") or (tag == "DataPropertyRange") or (tag == "AnnotationPropertyRange"):
      val = self.objs.pop(); obj = self.objs.pop();
      obj.range.append(val)
      self.purge_annotations((obj, owl.range, val))
      
    elif (tag in _TAG_2_PROP_TYPE):
      prop_type = _TAG_2_PROP_TYPE[tag]
      obj = self.objs.pop()
      if not issubclass(obj, prop_type): obj.is_a.append(prop_type)
      
    elif (tag == "InverseObjectProperties") or (tag == "InverseDataProperties"):
      self.objs.pop().inverse_property = self.objs.pop()
      
    elif (tag == "DisjointClasses") or (tag == "DisjointObjectProperties") or (tag == "DisjointDataProperties") or (tag == "DifferentIndividuals"):
      start = _rindex(self.objs, "(")
      AllDisjoint(*self.objs[start + 1 : ], ontology = self.ontology)
      del self.objs[start :]
      
    elif (tag == "ObjectPropertyAssertion") or (tag == "DataPropertyAssertion"):
      self.relations.add(self.objs[-3 :])
      self.purge_annotations((self.objs[-2], self.objs[-3], self.objs[-1]))
      del self.objs[-3 :]
      
    elif (tag == "ObjectComplementOf") or (tag == "DataComplementOf"): self.objs[-1] = NOT(self.objs[-1])
    
    elif (tag == "ObjectSomeValuesFrom") or (tag == "ObjectAllValuesFrom") or (tag == "ObjectHasValue") or (tag == "DataSomeValuesFrom") or (tag == "DataAllValuesFrom") or (tag == "DataHasValue"):
      self.push_value(restriction(self.objs.pop(-2), _TAG_2_REST_TYPE[tag], self.objs.pop()))
      
    elif (tag == "ObjectExactCardinality") or (tag == "ObjectMinCardinality") or (tag == "ObjectMaxCardinality") or (tag == "DataExactCardinality") or (tag == "DataMinCardinality") or (tag == "DataMaxCardinality"):
      start = _rindex(self.objs, "(")
      objs = self.objs[start + 1 : ]
      del self.objs[start :]
      if len(objs) == 2:             self.push_value(restriction(objs[0], _TAG_2_REST_TYPE[tag], self.last_cardinality, objs[-1]))
      elif tag.startswith("Object"): self.push_value(restriction(objs[0], _TAG_2_REST_TYPE[tag], self.last_cardinality, Thing))
      else:                          self.push_value(restriction(objs[0], _TAG_2_REST_TYPE[tag], self.last_cardinality, str))
      
    elif (tag == "ObjectOneOf"):
      start = _rindex(self.objs, "(")
      self.objs[start :] = [one_of(*self.objs[start + 1 : ])]
      
    elif (tag == "ObjectIntersectionOf") or (tag == "ObjectUnionOf") or (tag == "DataIntersectionOf") or (tag == "DataUnionOf"):
      start = _rindex(self.objs, "(")
      if tag.endswith("IntersectionOf"): r = AndRestriction(*self.objs[start + 1 : ])
      else:                              r = OrRestriction (*self.objs[start + 1 : ])
      self.objs[start :] = [r]
      
    elif (tag == "Import"):
      self.ontology.imported_ontologies.append(get_ontology(self.current_content).load())
      
    elif (tag == "IRI"): self.push_value(self.ontology.get_object(self.current_content, None, self))
    
    elif (tag == "AbbreviatedIRI"):
      iri = self.unabbreviate_IRI(self.current_content)
      if iri in owlready._DATATYPES_2_PYTHON: self.push_value(owlready._DATATYPES_2_PYTHON[iri])
      else:                                   self.push_value(self.ontology.get_object(iri, None, self))
      
    elif (tag == "AnnotationAssertion"):
      ANNOTATIONS[self.objs[-2]].add_annotation((self.objs[-3], self.current_lang), self.objs[-1])
      del self.objs[-3:]
      
    elif (tag == "Annotation"):
      if len(self.objs) == 2: # On ontology
        ANNOTATIONS[self.ontology].add_annotation((self.objs[-2], self.current_lang), self.objs[-1])
      else:
        self.annots.add(((self.objs[-2], self.current_lang), self.objs[-1]))
      if (self.objs[-2].name == "python_module") and (self.objs[-2].ontology.name == "owlready_ontology"):
        print("* Owlready *     ...importing Python module '%s' required by ontology '%s'..." % (self.objs[-1], self.ontology.name), file = sys.stderr)
        try: __import__(self.objs[-1])
        except ImportError:
          print("\n* Owlready * ERROR: cannot import Python module!\n", file = sys.stderr)
          sys.excepthook(*sys.exc_info())
          print("\n\n\n", file = sys.stderr)
      del self.objs[-2:]
      
    elif (tag == "HasKey"):
      self.objs[-1].indexes[self.objs[-2]] = {}
      self.purge_annotations((self.objs[-1], "indexes", self.objs[-2]))
      del self.objs[-2:]
      
  def characters(self, content): self.current_content += content
  
  def purge_annotations(self, obj):
    if self.annots:
      for annot in self.annots: ANNOTATIONS[obj].add_annotation(*annot)
      self.annots = []
      
  def end_parsing(self):
    for Prop, subject, object in self.relations:
      if Prop.is_functional_for(subject): setattr(subject, Prop.python_name, object)
      else:
        values = getattr(subject, Prop.python_name)
        if not object in values: getattr(subject, Prop.python_name).append(object)
      
    for instance in self.ontology.instances:
      if isinstance(instance, GeneratedName): instance.name # Ensure all names are generated properly
      
    for prop in self.datatype_properties:
      if not prop.range: 
        warnings.warn("%s is a range-less DataProperty, this is not supported by OwlReady! Please specify at least a very broad range, such as 'float or int or str'." % prop, OwlReadyRangelessDataProperty, 4)
      
    
def _rindex(l, o): return len(l) - list(reversed(l)).index(o) - 1

def fix_mro():
  broken_classes = owlready._MRO_BROKEN_CLASSES
  owlready._MRO_BROKEN_CLASSES = set()
  for Class in broken_classes: Class._recalc_mro()
  if owlready._MRO_BROKEN_CLASSES:
    if owlready._MRO_BROKEN_CLASSES == broken_classes: # Nothing fixed => failed!
      print(file = sys.stderr)
      warnings.warn("Inconsistent MRO for %s! Using a simplified degraded MRO computation algorithm." % ", ".join(Class.__name__ for Class in broken_classes), OwlReadyMROWarning, 4)
    else:
      fix_mro()
  else:
    print(" ok.", file = sys.stderr)
    
def parse(f, ontology = None):
  saved_default_onto = owlready.DEFAULT_ONTOLOGY
  owlready.DEFAULT_ONTOLOGY = None
  owlready._MRO_BROKEN_CLASSES = set() # Collect MRO broken classes instead of warning about them
  handler = OWLXMLHandler(ontology)
  parser = sax.make_parser()
  parser.setContentHandler(handler)
  parser.parse(f)
  handler.end_parsing()
  owlready.DEFAULT_ONTOLOGY = saved_default_onto
  if owlready._MRO_BROKEN_CLASSES:
    print("* Owlready * Fixing MRO for ontology %s..." % handler.ontology, end = "", file = sys.stderr)
    fix_mro()
  owlready._MRO_BROKEN_CLASSES = None
  return handler.ontology

