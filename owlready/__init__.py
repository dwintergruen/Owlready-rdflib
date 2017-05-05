# -*- coding: utf-8 -*-
# Owlready
# Copyright (C) 2013-2014 Jean-Baptiste LAMY
# LIMICS (Laboratoire d'informatique médicale et d'ingénierie des connaissances en santé), UMR_S 1142
# University Paris 13, Sorbonne paris-Cité, Bobigny, France
from eulxml.xmlmap.dc import rdflib
from rdflib.term import URIRef
from IPython.utils.sysinfo import sys_info
from lib2to3.fixer_util import Attr
from cssselect.parser import Attrib

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

#modfied by DW
VERSION = "0.3a"


import sys, os, types, tempfile, subprocess, weakref, re, urllib.request, warnings
from io import StringIO
from collections import defaultdict, OrderedDict
#from xml.sax.saxutils import escape
from urllib.parse import quote
import datetime
import rdflib
#from datetime import date, time, datetime, timedelta

try: import pyxb.binding.datatypes
except: pyxb = None

JAVA_EXE = "java"

def escape(x):
    try:
        return quote(x)
    except:
        return x

_HERE = os.path.dirname(__file__)
_HERMIT_CLASSPATH = os.pathsep.join([os.path.join(_HERE, "hermit"), os.path.join(_HERE, "hermit", "HermiT.jar")])

# For compiling and running HermiT manually:
#   cd /home/jiba/src/owlready/hermit
#   javac -cp .:HermiT.jar ./org/semanticweb/HermiT/cli/CommandLine.java
#   java  -cp .:HermiT.jar org.semanticweb.HermiT.cli.CommandLine -c -O -D -I /tmp/t.owl

class OwlReadyWarning               (UserWarning): pass
class OwlReadyUndefinedIRIWarning   (OwlReadyWarning): pass
class OwlReadyOntologyIRIWarning    (OwlReadyWarning): pass
class OwlReadyMROWarning            (OwlReadyWarning): pass
class OwlReadyGeneratedNameWarning  (OwlReadyWarning): pass
class OwlReadyDupplicatedNameWarning(OwlReadyWarning): pass
class OwlReadyRangelessDataProperty (OwlReadyWarning): pass


def URIref2(url):
    if url.startswith("<") and url.endswith(">"):
        url =url[1:-1]
    return rdflib.URIRef(url);
    
    
def unload_all_ontologies():
  global onto_path
  onto_path = []
  global ONTOLOGIES
  keys_ONTOLOGIES = {u'http://anonymous',u'http://www.lesfleursdunormal.fr/static/_downloads/owlready_ontology.owl',u'http://www.w3.org/1999/02/22-rdf-syntax-ns',u'http://www.w3.org/2000/01/rdf-schema',u'http://www.w3.org/2001/XMLSchema',u'http://www.w3.org/2002/07/owl'}
  del_key=[]
  for key in ONTOLOGIES:
    if key not in keys_ONTOLOGIES:
      del_key.append(key)
  for key in del_key: del ONTOLOGIES[key]
  global IRIS
  keys_IRIS = {
    u'http://www.w3.org/2000/01/rdf-schema#seeAlso',
    u'http://www.w3.org/2002/07/owl#range',
    u'http://anonymous',
    u'http://www.w3.org/1999/02/22-rdf-syntax-ns',
    u'http://www.lesfleursdunormal.fr/static/_downloads/owlready_ontology.owl#python_name',
    u'http://www.lesfleursdunormal.fr/static/_downloads/owlready_ontology.owl',
    u'http://www.lesfleursdunormal.fr/static/_downloads/owlready_ontology.owl#python_module',
    u'http://www.w3.org/2002/07/owl#domain',
    u'http://www.w3.org/2002/07/owl',
    u'http://www.w3.org/2002/07/owl#ReflexiveProperty',
    u'http://www.w3.org/2002/07/owl#IrreflexiveProperty',
    u'http://www.w3.org/2002/07/owl#versionInfo',
    u'http://www.w3.org/2002/07/owl#backwardCompatibleWith',
    u'http://www.w3.org/2002/07/owl#Property',
    u'http://www.w3.org/2002/07/owl#SymmetricProperty',
    u'http://www.w3.org/2002/07/owl#Nothing',
    u'http://www.w3.org/2000/01/rdf-schema#isDefinedBy',
    u'http://www.w3.org/2002/07/owl#equivalent_to',
    u'http://www.w3.org/2002/07/owl#sameAs',
    u'http://www.w3.org/2002/07/owl#FunctionalProperty',
    u'http://www.w3.org/2002/07/owl#InverseFunctionalProperty',
    u'http://www.w3.org/2002/07/owl#is_a',
    u'http://www.w3.org/2000/01/rdf-schema#label',
    u'http://www.w3.org/2000/01/rdf-schema',
    u'http://www.lesfleursdunormal.fr/static/_downloads/owlready_ontology.owl#editobj_priority',
    u'http://www.w3.org/2000/01/rdf-schema#comment',
    u'http://www.w3.org/2002/07/owl#TransitiveProperty',
    u'http://www.w3.org/2002/07/owl#deprecated',
    u'http://www.w3.org/2002/07/owl#incompatibleWith',
    u'http://www.w3.org/2002/07/owl#priorVersion',
    u'http://www.w3.org/2002/07/owl#Thing',
    u'http://www.w3.org/2002/07/owl#AsymmetricProperty',
    u'http://www.w3.org/2001/XMLSchema',
    u'http://www.w3.org/2002/07/owl#AnnotationProperty'
    }
  del_key=[]
  for key in IRIS:
    if key not in keys_IRIS:
      del_key.append(key)
  for key in del_key: del IRIS[key]
    
class normstr(str): pass


PROPS       = {}
ANNOT_PROPS = {}
IRIS        = {}

def forward_declaration(o):
  o._forward_declared = True
  return o

def to_owl(self, **kargs):
  definition = StringIO()
  content    = StringIO()
  if isinstance(self, EntityClass) or isinstance(self, Restriction): self._class_to_owl   (definition, content, **kargs)
  else:                                                              self._instance_to_owl(definition, content, **kargs)
  return "%s\n%s" % (definition.getvalue(), content.getvalue())


def to_rdflib(self, g, **kargs):

  if isinstance(self, EntityClass) or isinstance(self, Restriction): self._class_to_rdflib   (g, **kargs)
  else:                                                              self._instance_to_rdflib(g, **kargs)
  #return "%s\n%s" % (definition.getvalue(), content.getvalue())

def to_n3(self, **kargs):
  definition = StringIO()
  content    = StringIO()
  if isinstance(self, EntityClass) or isinstance(self, Restriction): self._class_to_n3   (definition, content, **kargs)
  else:                                                              self._instance_to_n3(definition, content, **kargs)
  return "%s\n%s" % (definition.getvalue(), content.getvalue())

def to_python(self):
  serializer = _PythonSerializer()
  if isinstance(self, EntityClass) or isinstance(self, Restriction): self._class_to_python   (serializer)
  else:                                                              self._instance_to_python(serializer)
  return serializer.get_code()

class _PythonSerializer(object):
  def __init__(self):
    self.class_definition    = StringIO()
    self.class_content       = StringIO()
    self.instance_definition = StringIO()
    self.instance_content    = StringIO()
    self.need_forward_decls  = set()
    self.declareds           = set(_PYTHON_2_DATATYPES.keys())
    
  def referenced(self, Class):
    if   isinstance(Class, Restriction): Class._referenced(self)
    elif not Class in self.declareds: self.need_forward_decls.add(Class)


  def get_code(self):
    for Class in self.need_forward_decls:
      Class._class_to_python_forward_decl(self)
    return "%s\n%s\n%s\n%s" % (self.class_definition.getvalue(), self.class_content.getvalue(), self.instance_definition.getvalue(), self.instance_content.getvalue())
  
class AllDisjoint(object):
  def __init__(self, *Entities, ontology = None):
    self.Entities = list(Entities)
    if ontology is None: ontology = Entities[0].ontology
    ontology.add(self)
    
  def __str__ (self): return "AllDisjoint(%s)" % ", ".join(str (e) for e in self.Entities)
  def __repr__(self): return "AllDisjoint(%s)" % ", ".join(repr(e) for e in self.Entities)
  def _instance_to_python(self, s):
    for e in self.Entities:
      if isinstance(self.Entities[0], ThingClass) or isinstance(self.Entities[0], PropertyClass):
        s.referenced(e)
    s.class_content.write("AllDisjoint(%s)" % ", ".join(repr(e) for e in self.Entities))
    
  def _instance_to_owl(self, definition, content):
    if   isinstance(self.Entities[0], ThingClass):
      content.write("""<DisjointClasses>%s</DisjointClasses>\n""" % "".join(_owl_name(Class) for Class in self.Entities))
    elif isinstance(self.Entities[0], PropertyClass):
      if self.Entities[0]._is_data_property():
        content.write("""<DisjointDatatypeProperties>%s</DisjointDatatypeProperties>\n""" % "".join(_owl_name(Class) for Class in self.Entities))
      else:
        content.write("""<DisjointObjectProperties>%s</DisjointObjectProperties>\n""" % "".join(_owl_name(Class) for Class in self.Entities))
    else:
      content.write("""<DifferentIndividuals>%s</DifferentIndividuals>\n""" % "".join(_owl_name(instance) for instance in self.Entities))
      
   #todo restrictions in rdflib
  def _restriction_to_rdflib(self):
      return
  def _instance_to_n3(self, definition, content):
    if   isinstance(self.Entities[0], ThingClass):
      content.write("""[ a owl:allDisjointClasses""")
      for Class in self.Entities: content.write(""" ; owl:members %s""" % _n3_name(Class))
    elif isinstance(self.Entities[0], PropertyClass):
      content.write("""[ a owl:allDisjointProperties""")
      for Property in self.Entities: content.write(""" ; owl:members %s""" % _n3_name(Property))
    else:
      content.write("""[ a owl:allDifferent""")
      for instance in self.Entities: content.write(""" ; owl:distinctMembers %s""" % _n3_name(instance))
    content.write("""].\n""")
      
AllDistinct = AllDisjoint

onto_path = []

def _open_onto_file(base_iri, name, mode = "r", only_local = False):
  #if base_iri == OWLREADY_ONTOLOGY_IRI: return open(os.path.join(_HERE, "owl", "owlready_ontology.owl"), mode)
  if base_iri.startswith("file://"): return open(base_iri[7:], mode)
  for dir in onto_path:
    filename = os.path.join(dir, "%s.owl" % name)
    if os.path.exists(filename): return open(filename, mode,encoding="utf-8")
  if (mode == "r") and not only_local: return urllib.request.urlopen(base_iri)
  if (mode == "w"): return open(os.path.join(onto_path[0], "%s.owl" % name), "w")
  raise FileNotFoundError

ONTOLOGIES = {}
#this is not correct the base uri has to be read from the o_wl ontolofy
def get_ontology(base_iri=None,owl_url=None):
     
    if base_iri is None and owl_url is None:
        raise Exception("base_iri or owl_url has to be defined!")
    if base_iri is  None and owl_url is None:
        raise Exception("Only one!: base_iri or owl_url has to be defined!")
    
    if base_iri is not None:
        if base_iri in ONTOLOGIES: return ONTOLOGIES[base_iri]
        return Ontology(base_iri=base_iri)
    
    if owl_url in ONTOLOGIES: return ONTOLOGIES[owl_url]
    return Ontology(owl_url=owl_url)
    
    
    

def get_object(iri, type = None, parser = 2):
  if not (iri.startswith("http:") or iri.startswith("file:")): raise ValueError
  if iri in IRIS: return IRIS[iri]
  if type is None:
    msg = "Undefined IRI '%s' referenced, OwlReady assumes it is an individual." % iri
    if isinstance(parser, int):
      warnings.warn(msg, OwlReadyUndefinedIRIWarning, parser)
    else:
      filename, lineno, colno = parser.get_loc()
      warnings.warn_explicit(msg, OwlReadyUndefinedIRIWarning, filename or "(unknown file)", lineno)
    type = Thing
    
  attr_dict = {}
  if "#" in iri: base_iri, name = iri.split("#", 1)
  else:          base_iri, name = iri.rsplit("/", 1); attr_dict["owl_separator"] = "/"
  
  self = get_ontology(base_iri)
  attr_dict["ontology"] = self
 
  if name.startswith("'") and name.endswith("'"): name = name[1:-1]
  if   type is ThingClass:              r = ThingClass             (name, (Thing             ,), attr_dict)
  elif type is PropertyClass:           r = PropertyClass          (name, (Property          ,), attr_dict)
  elif type is AnnotationPropertyClass: r = AnnotationPropertyClass(name, (AnnotationProperty,), attr_dict)
  elif type is Thing:                   r = Thing                  (name, **attr_dict)
  else:
    raise ValueError(type)
  IRIS[iri]=r
  return r

DEFAULT_ONTOLOGY = None

class Ontology(object):
  def __init__(self, base_iri, force_non_dot_owl_iri = False):
    self.base_iri  = base_iri
   
    if base_iri is not None:
        if base_iri.endswith("/") or base_iri.endswith("#"): raise ValueError("Ontology IRI must not ends with '/' or '#'; please remove it.")
       
        self.name                  = base_iri.rsplit("/", 1)[-1]
        if self.name.endswith(".owl"): self.name = self.name[:-4]
        self.imported_ontologies   = []
        self.classes               = []
        self.properties            = []
        self.annotation_properties = []
        self.all_disjoints         = []
        self.instances             = []
        self.loaded                = False
        if self.base_iri in ONTOLOGIES: raise ValueError("An ontology named '%s' already exists!" % self.base_iri)
        ONTOLOGIES[self.base_iri]  = IRIS[self.base_iri] = self
        print("* Owlready * Creating new ontology %s <%s>." % (self.name, self.base_iri), file = sys.stderr)
        if (not base_iri.endswith(".owl")) and (not force_non_dot_owl_iri):
            warnings.warn("Ontology IRI '%s' does not ends with '.owl' as expected." % base_iri, OwlReadyOntologyIRIWarning, 3)
          
  
        
          
  def indirectly_imported_ontologies(self):
    ontologies = set([self])
    for ontology in self.imported_ontologies: ontologies.update(ontology.indirectly_imported_ontologies())
    return ontologies
  
  #changed assume now that there is owl_url set and the base_uri is taken out of the file
  def load(self, only_local = False):
    if self.loaded: return self
    if self.base_iri is not None:
        filepath = self.base_iri 
    else:
        filepath = self.owl_url
        
    f = _open_onto_file(filepath, self.name, "r", only_local)
    self.loaded = True
    print("* Owlready *     ...loading ontology %s from %s..." % (self.name, getattr(f, "name", "") or getattr(f, "url", "???")), file = sys.stderr)
    import owlready.owl_xml_parser

    parsed = owlready.owl_xml_parser.parse(f, self)
    
    if hasattr(parsed, "ontologyIRI"):
        self.base_iri=parsed.ontologyIRI
    return parsed

  def save(self, filename = None):
    owl = to_owl(self)
    if filename: f = open(filename, "w")
    else:        f = _open_onto_file(self.base_iri, self.name, "w")
    print("* Owlready * Saving ontology %s to %s..." % (self.name, getattr(f, "name", "???")), file = sys.stderr)
    f.write(owl)
    
  def add(self, o):
    if   isinstance(o, AllDisjoint):             self.all_disjoints        .append(o); return # No name => skip last line
    elif isinstance(o, ThingClass):              self.classes              .append(o)
    elif isinstance(o, PropertyClass):           self.properties           .append(o)
    elif isinstance(o, AnnotationPropertyClass): self.annotation_properties.append(o)
    elif isinstance(o, Thing):                   self.instances            .append(o)
    else: raise ValueError
    if hasattr(o.ontology,'ontologyIRI'):
        iri = o.ontology.ontologyIRI
        if iri.endswith("/") or iri.endswith("#"):
            sep = ""
            o.owl_separator = ""
        else:
            sep=o.owl_separator
        
    else:
        iri = o.ontology.base_iri
        sep=o.owl_separator
    
    _iri_changed(o, "%s%s%s" % (iri,sep, o.name), "%s%s%s" % (iri, sep, o.name))
    o.ontology = self

  def remove_unreachables(self, from_classes_and_instances):
    reachables = set()
    
    for o in from_classes_and_instances:
      if isinstance(o, Thing): o._instance_refered_object(reachables)
      else:                    o.         _refered_object(reachables)
      
    classes      = [o for o in self.classes   if o in reachables]
    instances    = [o for o in self.instances if o in reachables]
    unreachables = [o for o in self.classes   if not o in reachables] + [o for o in self.instances if not o in reachables]
    self.classes   = classes
    self.instances = instances
    return unreachables
    
  def instances_of (self, Class): return (instance for instance in self.instances if isinstance(instance, Class))
  def subclasses_of(self, Class): return (klass    for klass    in self.classes   if issubclass(klass   , Class))
  
  def get_object(self, iri, type = None, parser = None,base_iri=None):
    if base_iri is not None:
        self.base_iri = base_iri
    if not parser: parser = 3
    if iri.startswith("http:") or iri.startswith("file:"): return get_object(iri, type, parser)
    if iri.startswith("#"): return get_object("%s%s" % (self.base_iri, iri), type, parser)
    if iri.startswith("/"): return get_object("%s%s" % (self.base_iri, iri), type, parser)
    if self.base_iri.endswith("/") or self.base_iri.endswith("#"):
        return get_object("%s%s" % (self.base_iri, iri), type, parser)   
    return get_object("%s#%s" % (self.base_iri, iri), type, parser)
  
  def __getattr__(self, attr):
    if self.base_iri.endswith("/") or self.base_iri.endswith("#"):
        iri = "%s%s" % (self.base_iri, attr)
    else: 
        iri = "%s#%s" % (self.base_iri, attr)
    if iri in IRIS: return IRIS[iri]
    #neuer versuch
    
    iri = "%s/%s" % (self.base_iri, attr)
    if iri in IRIS: return IRIS[iri]
   
    raise AttributeError("Ontology '%s' has not object '%s'!" % (self, attr))
  
  def __getitem__(self, attr): return getattr(self, attr)
  
  #_HERMIT_RESULT_REGEXP = re.compile("^([A-Za-z]+)\\( <([^>]+)> <([^>]+)> \\)$", re.MULTILINE)
  _HERMIT_RESULT_REGEXP = re.compile("^([A-Za-z]+)\\( ((?:<(?:[^>]+)>\s*)+) \\)$", re.MULTILINE)
  def sync_reasoner(self, rules = None, debug = 1, keep_tmp_file = 0):
    if isinstance(rules, Rules): rules = (rules,)
    tmp = tempfile.NamedTemporaryFile("w", delete = 0)
    tmp.write(to_owl(self, write_import = 0, rules = rules))
    tmp.close()
    command = [JAVA_EXE, "-Xmx2000M", "-cp", _HERMIT_CLASSPATH, "org.semanticweb.HermiT.cli.CommandLine", "-c", "-O", "-D", "-I", "file:///%s" % tmp.name.replace('\\','/')]
    if debug:
      import time
      print("* Owlready * Running HermiT...", file = sys.stderr)
      print("    %s" % " ".join(command), file = sys.stderr)
      t0 = time.time()
    output = subprocess.check_output(command)
    output = output.decode("utf8").replace("\r","")
    if debug:
      print("* Owlready * HermiT took %s seconds" % (time.time() - t0), file = sys.stderr)
      if debug > 1:
        print("* Owlready * HermiT output:", file = sys.stderr)
        print(output, file = sys.stderr)
        
    print(output, file = open("/tmp/sortie_hermit.txt", "w"))
        
    is_a_relations  = {"SubClassOf", "SubObjectPropertyOf", "SubDataPropertyOf", "Type"}
    equiv_relations = {"EquivalentClasses", "EquivalentObjectProperties", "EquivalentDataProperties"}
    
    #new_parents = defaultdict(list)
    #for relation, child, parent in self._HERMIT_RESULT_REGEXP.findall(output):
    #  if relation in is_a_relations:
    #    if child.startswith(self.base_iri):
    #      child  = IRIS[child ]
    #      parent = IRIS[parent]
    #      new_parents[child].append(parent)
    
    new_parents = defaultdict(list)
    for relation, concepts in self._HERMIT_RESULT_REGEXP.findall(output):
      concepts = concepts[1:-1].split("> <")
      if  relation in is_a_relations:
        if concepts[0].startswith(self.base_iri):
          child  = IRIS[concepts[0]]
          parent = IRIS[concepts[1]]
         
          new_parents[child].append(parent)
          
      elif relation in equiv_relations:
        for concept_iri in concepts:
          if concept_iri.startswith(self.base_iri):
            concept = IRIS[concept_iri]
            if "http://www.w3.org/2002/07/owl#Nothing" in concepts:
              concept.equivalent_to.append(Nothing)
              if debug: print("* Owlready * Equivalenting:", concept, "Nothing", file = sys.stderr)
              
            else:
              for other_concept_iri in concepts:
                if concept_iri == other_concept_iri: continue
                other_concept = IRIS[other_concept_iri]
                concept.equivalent_to.append(other_concept)
                if debug: print("* Owlready * Equivalenting:", concept, other_concept, file = sys.stderr)
                
    for child, parents in new_parents.items():
      old = set(parent for parent in child.is_a if not isinstance(parent, Restriction))
      new = set(parents)
      for parent in set(new):
        for parent_eq in parent.equivalent_to:
          if isinstance(parent_eq, ThingClass):
            new.add(parent_eq)
        
      new.update(old & _TYPES) # Types are not shown by HermiT
      if old == new: continue
      new = _keep_most_specific(new, consider_equivalence = False)
      if old == new: continue
      
      if debug: print("* Owlready * Reparenting %s:" % child, old, "=>", new, file = sys.stderr)
      new_is_a = list(child.is_a)
      for removed in old - new: new_is_a.remove(removed)
      for added   in new - old: new_is_a.append(added)
      child.is_a.reinit(new_is_a)
      
      for child_eq in child.equivalent_to:
        if isinstance(child_eq, ThingClass):
          if debug: print("* Owlready * Reparenting %s (since equivalent):" % child_eq, old, "=>", new, file = sys.stderr)
          new_is_a = list(child_eq.is_a)
          for removed in old - new:
            if removed in new_is_a: new_is_a.remove(removed)
          for added   in new - old: new_is_a.append(added)
          child_eq.is_a.reinit(new_is_a)
          
    if not keep_tmp_file: os.unlink(tmp.name)
    
  def __str__ (self): return self.name
  def __repr__(self): return "<Ontology %s>" % self.name
  
  def _instance_to_owl(self, definition, content, write_header = 1, write_import = 1, already_included = None, rules = None):
    if write_header:
      definition.write("""<?xml version="1.0"?>\n""")
      
      definition.write("""<!DOCTYPE Ontology [\n""")
      definition.write('''    <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >\n''')
      definition.write('''    <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >\n''')
      definition.write('''    <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >\n''')
      definition.write('''    <!ENTITY owl "http://www.w3.org/2002/07/owl#" >\n''')
      for onto in self.imported_ontologies:
        definition.write("""    <!ENTITY %s "%s" >\n""" % (onto.name, onto.base_iri))
      definition.write("""]>\n""")
      
      definition.write('''<Ontology xmlns="http://www.w3.org/2002/07/owl#" xml:base="%s" ontologyIRI="%s"\n''' % (self.base_iri, self.base_iri))
      definition.write('''     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n''')
      definition.write('''     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n''')
      definition.write('''     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n''')
      definition.write('''     xmlns:xml="http://www.w3.org/XML/1998/namespace"\n''')
      definition.write('''>\n''')
      definition.write('''<Prefix name="" IRI="%s"/>\n''' % self.base_iri)
      definition.write('''<Prefix name="owl" IRI="http://www.w3.org/2002/07/owl#"/>\n''')
      definition.write('''<Prefix name="rdf" IRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>\n''')
      definition.write('''<Prefix name="xsd" IRI="http://www.w3.org/2001/XMLSchema#"/>\n''')
      definition.write('''<Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>\n''')
      definition.write('''<Prefix name="%s" IRI="%s"/>\n''' % (self.name, self.base_iri))
      
    if write_import:
      for imported_ontology in self.imported_ontologies:
        definition.write('''<Import>%s</Import>\n''' % imported_ontology.base_iri)
        
      for AProp, annot_value, lang in ANNOTATIONS[self].items():
        definition.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
        
    else:
      if already_included is None: already_included = set([self])
      for imported_ontology in self.imported_ontologies:
        if not imported_ontology in already_included:
          already_included.add(imported_ontology)
          definition.write(to_owl(imported_ontology, write_header = 0, write_import = 0, already_included = already_included))
          
    definition.write('''\n''')
    
    for entity in self.properties + self.classes:
      entity._class_to_owl(definition, content)
      
    for all_disjoint in self.all_disjoints:
      all_disjoint._instance_to_owl(definition, content)
      
    for instance in self.instances:
      instance._instance_to_owl(definition, content)
      
    if rules:
      for r in rules: content.write("""%s\n""" % r.get_rules())
      
    if write_header: content.write("""</Ontology>\n""")
    
  def _instance_to_rdflib(self, g, write_header = 1, write_import = 1, already_included = None, rules = None):
    if write_header:
     
      g.add((URIref2("<%s>"%self.base_iri), rdflib.RDF.type, rdflib.OWL.type))
      
    if write_import:
      for imported_ontology in self.imported_ontologies:
        g.add((URIref2("%s"%imported_ontology.base_iri[0]), rdflib.OWL.imports,URIref2("<%s>" % imported_ontology.base_iri[1])))
        
     
    else:
      if already_included is None: already_included = set([self])
      for imported_ontology in self.imported_ontologies:
        if not imported_ontology in already_included:
          already_included.add(imported_ontology)
          g.add(to_rdflib(imported_ontology, write_header = 0, write_import = 0, already_included = already_included))
          
    
    
    for entity in self.properties + self.classes:
      entity._class_to_rdflib(g)
    for all_disjoint in self.all_disjoints:
        pass #TODO DW: not implemented yet.    
        #all_disjoint._instance_to_rdflib(g)
      
    for instance in self.instances:
      instance._instance_to_rdflib(g)
    
    #TODO: transform rules to RDFLIb  
    #if rules:
    # for r in rules: content.write("""%s\n""" % r.get_rules())
    
  def _instance_to_n3(self, definition, content, write_header = 1, write_import = 1, already_included = None, rules = None):
    if write_header:
      definition.write("""@prefix log: <http://www.w3.org/2000/10/swap/log#>.\n""")
      definition.write("""@prefix math: <http://www.w3.org/2000/10/swap/math#>.\n""")
      definition.write("""@prefix owl: <http://www.w3.org/2002/07/owl#>.\n""")
      definition.write("""@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.\n""")
      definition.write("""@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.\n""")
      definition.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.\n""")
      definition.write("""\n""")
      #for onto in self.imported_ontologies:
      #  definition.write("""%s owl:imports \n""" % (onto.name, onto.base_iri))
      
      definition.write("""<%s> a owl:Ontology.\n""" % self.base_iri)
      
    if write_import:
      for imported_ontology in self.imported_ontologies:
        definition.write("""%s owl:imports <%s>.\n""" % imported_ontology.base_iri)
        
      #for AProp, annot_value, lang in ANNOTATIONS[self].items():
      #  definition.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
      
    else:
      if already_included is None: already_included = set([self])
      for imported_ontology in self.imported_ontologies:
        if not imported_ontology in already_included:
          already_included.add(imported_ontology)
          definition.write(to_n3(imported_ontology, write_header = 0, write_import = 0, already_included = already_included))
          
    definition.write("\n")
    
    for entity in self.properties + self.classes:
      entity._class_to_n3(definition, content)
      
    for all_disjoint in self.all_disjoints:
      all_disjoint._instance_to_n3(definition, content)
      
    for instance in self.instances:
      instance._instance_to_n3(definition, content)
      
    if rules:
      for r in rules: content.write("""%s\n""" % r.get_rules())
    
  def _instance_to_python(self, s):
    s.class_definition.write("""from owlready import *\n\n""")
    s.class_definition.write("""%s = Ontology("%s", imported_ontologies = [%s])\n\n""" % (self.name, self.base_iri, ", ".join(onto.name for onto in self.imported_ontologies)))
    
    for entity in self.classes + self.properties:
      entity._class_to_python(s)
      s.class_content.write("""\n""")
      
    for all_disjoint in self.all_disjoints:
      s.class_content.write("""%s.add(""" % self.name)
      all_disjoint._instance_to_python(s)
      s.class_content.write(""")\n""")
    s.class_content.write("""\n""")
    
    for instance in self.instances:
      s.instance_definition.write("""%s.add(""" % self.name)
      instance._instance_to_python(s)
      s.instance_definition.write(""")\n""")
      s.instance_content.write("""\n""")
  

owl       = Ontology("http://www.w3.org/2002/07/owl"             , force_non_dot_owl_iri = True)
rdf       = Ontology("http://www.w3.org/1999/02/22-rdf-syntax-ns", force_non_dot_owl_iri = True)
rdfs      = Ontology("http://www.w3.org/2000/01/rdf-schema"      , force_non_dot_owl_iri = True)
xsd       = Ontology("http://www.w3.org/2001/XMLSchema"          , force_non_dot_owl_iri = True)
anonymous = Ontology("http://anonymous"                          , force_non_dot_owl_iri = True)

class Property:           pass # Fake "fordward" declaration
class AnnotationProperty: pass # Fake "fordward" declaration

class _CallbackList(list):
  def __init__(self, l, obj, func_name, Prop):
    super().__init__(l)
    self._obj       = obj
    self._func_name = func_name
    self._Prop      = Prop
  def _call_callback(self, old): getattr(self._obj, self._func_name)(self, self._Prop, old)
  def _set  (self, l):          super().__init__(l)
  def _remove(self, x):         super().remove(x)
  def reinit(self, l):          old = list(self); super().__init__(l)       ; self._call_callback(old)
  def append(self, x):          old = list(self); super().append(x)         ; self._call_callback(old)
  def insert(self, i, x):       old = list(self); super().insert(i, x)      ; self._call_callback(old)
  def extend(self, l):          old = list(self); super().extend(l)         ; self._call_callback(old)
  def remove(self, x):          old = list(self); super().remove(x)         ; self._call_callback(old)
  def __delitem__(self, i):     old = list(self); super().__delitem__(i)    ; self._call_callback(old)
  def __setitem__(self, i, x):  old = list(self); super().__setitem__(i, x) ; self._call_callback(old)
  def __delslice__(self, i):    old = list(self); super().__delslice__(i)   ; self._call_callback(old)
  def __setslice__(self, i, x): old = list(self); super().__setslice__(i, x); self._call_callback(old)
  def pop(self, i):             old = list(self); r = super().pop(i)        ; self._call_callback(old); return r


class GeneratedName(object):
  def generate_name(self): return "__generated_name__"

def _iri_changed(obj, old_iri, new_iri):
  if new_iri == "http://purl.obolibrary.org/obo#BFO_0000050": efjozeif
  if IRIS.get(old_iri) is obj: del IRIS[old_iri]
 
  
  IRIS[new_iri] = obj

def _unique_name(instance, name, add_1 = False):
  base_name = name
  if add_1: name = "%s_1" % base_name
  current = IRIS.get("%s%s%s"   % (instance.ontology.base_iri, instance.owl_separator, name))
  if (not current is None) and (not current is instance): # Dupplicated IRI => rename
    i = 2
    while 1:
      name = "%s_%s" % (base_name, i)
      current = IRIS.get("%s%s%s" % (instance.ontology.base_iri, instance.owl_separator, name))
      if (current is None) or (current is instance): break
      i += 1
  return name
  
  
class _NameDescriptor(object):
  def __get__(self, instance, owner):
    if isinstance(instance, GeneratedName):
      try: name = instance.generate_name()
      except:
        warnings.warn("Error while generating name for %s instance:" % instance.__class__.__name__, OwlReadyWarning, 2)
        sys.excepthook(*sys.exc_info())
        name = "__error_while_generating_name_for_%s_instance__" % instance.__class__.__name__
      if name != instance._name:
        name = _unique_name(instance, name)
        _iri_changed(instance, "%s%s%s" % (instance.ontology.base_iri, instance.owl_separator, instance._name), "%s%s%s" % (instance.ontology.base_iri, instance.owl_separator, name))
        instance._name = name
      return name
    return ((instance is None) and owner._name) or instance._name
    
  def __set__(self, instance, new_name): # instance is a Class or an instance
    
    if hasattr(instance.ontology, "ontologyIRI"):
        if instance.ontology.ontologyIRI.endswith("/") or  instance.ontology.ontologyIRI.endswith("#"):
            sep = ""
            instance.owl_separator=""
        else:
            sep =  instance.owl_separator
        
        _iri_changed(instance, "%s%s%s" % (instance.ontology.ontologyIRI, sep, instance._name), "%s%s%s" % (instance.ontology.ontologyIRI, sep, new_name))
    else:
        _iri_changed(instance, "%s%s%s" % (instance.ontology.base_iri, instance.owl_separator, instance._name), "%s%s%s" % (instance.ontology.base_iri, instance.owl_separator, new_name))
    instance._name = new_name
    

#class _OntologyDescriptor(object):
#  def __get__(self, instance, owner): return ((instance is None) and owner._ontology) or instance._ontology
#  
#  def __set__(self, instance, new_ontology): # instance is a Class or an instance
#    _iri_changed(instance, "%s%s%s" % (instance.ontology.base_iri, instance.owl_separator, instance.name), "%s%s%s" % (new_ontology.base_iri, instance.owl_separator, instance.name))
#    instance._ontology = new_ontology

    
class EntityClass(type):
  owl_separator = "#"
  ontology      = owl
  name          = _NameDescriptor()
  _name         = "EntityClass"
  
  def __and__(a, b): return AndRestriction(a, b)
  def __or__ (a, b): return OrRestriction (a, b)
  def __invert__(a): return NotRestriction(a)
  
  def __new__(MetaClass, name, superclasses, obj_dict, ontology = None):
      
    #makesure that the name is url-save
    name =urllib.parse.quote(name)
      
    if "is_a" in obj_dict:
      _is_a = list(superclasses) + obj_dict.pop("is_a")
      superclasses = tuple(superclass for superclass in _is_a if isinstance(superclass, EntityClass))
    else:
      _is_a = list(superclasses)
    if not "equivalent_to" in obj_dict: obj_dict["equivalent_to"] = []
    
    if not ontology:
      if DEFAULT_ONTOLOGY:
        ontology = DEFAULT_ONTOLOGY
      else:
        ontology = obj_dict.get("ontology")
        if (not ontology) and superclasses: ontology = superclasses[0].ontology
        
    if ontology:
      Class = IRIS.get("%s%s%s" % (ontology.base_iri, obj_dict.get("owl_separator", "#"), name))
      if Class and (not getattr(Class, "_forward_declared", False)): Class = None
    else: Class = None
      
    if Class:
      del Class._forward_declared
      if Class.is_a != _is_a: Class.is_a.reinit(_is_a)
      for k, v in obj_dict.items(): type.__setattr__(Class, k, v)
    else:
      Class = type.__new__(MetaClass, name, superclasses, obj_dict)
      Class.name = name
      type.__setattr__(Class, "is_a", _CallbackList(_is_a, Class, "_class_is_a_changed", "is_a"))
      if   issubclass(Class, Property):           PROPS      [name] = Class
      elif issubclass(Class, AnnotationProperty): ANNOT_PROPS[name] = Class
      ontology.add(Class)
    return Class
  
  def mro(Class):
    try: return type.mro(Class)
    except:
      if _MRO_BROKEN_CLASSES is None: warnings.warn("* Owlready * Inconsistent MRO for %s! Using a simplified degraded MRO computation algorithm." % Class, OwlReadyMROWarning)
      else:                           _MRO_BROKEN_CLASSES.add(Class)
      mro = [Class]
      for base in Class.__bases__:
        for base_mro in base.__mro__:
          if base_mro in mro: mro.remove(base_mro)
          mro.append(base_mro)
      return mro
    
  def _recalc_mro(Class):
    Class.__bases__  = Class.__bases__ + () # Force MRO recalculation

  def __subclasscheck__(Class, Subclass):
    if type.__subclasscheck__(Class, Subclass): return True
    for Equivalent in Class.equivalent_to:
      if isinstance(Equivalent, EntityClass) and type.__subclasscheck__(Equivalent, Subclass): return True
    return False
  
  def __instancescheck__(Class, instance):
    if type.__instancecheck__(Class, instance): return True
    return issubclass(instance.__class__, Class)
    
  def __setattr__(Class, attr, value):
    if attr == "is_a":
      old = Class.is_a
      type.__setattr__(Class, "is_a", _CallbackList(value, Class, "_class_is_a_changed", "is_a"))
      Class._class_is_a_changed(Class.is_a, "is_a", old)
    type.__setattr__(Class, attr, value)
    
  def _class_is_a_changed(Class, is_a, Prop, old):
    bases = tuple(i for i in Class.is_a if isinstance(i, EntityClass)) + tuple(i for i in Class.is_a if (not isinstance(i, EntityClass)) and (not isinstance(i, Restriction)))
    Class.__bases__ = bases
  def __str__ (Class): return Class.name
  def __repr__(Class): return "%s.%s" % (Class.ontology.name, Class.name)
  
  def _satisfied_by(Class, x):
    return (isinstance(x, EntityClass) and issubclass(x, Class)) or isinstance(x, Class)
  
  def _class_to_python_forward_decl(Class, s):
    bases = [base.__name__ for base in Class.__bases__ if (base in _TYPES) or (base is Thing) or (base is Property)]
    if not bases:
      if isinstance(Class, ThingClass): bases = ["Thing"]
      else:                             bases = ["Property"]
    s.class_definition.write("""@forward_declaration\n""")
    s.class_definition.write("""class %s(%s): ontology = %s\n\n""" % (Class.name, ", ".join(bases), Class.ontology.name))
    
  def _class_to_python(Class, s):
    need_pass = 1
    s.declareds.add(Class)
    s.class_content.write("""class %s(%s):""" % (Class.name, ", ".join(base.__name__ for base in Class.__bases__)))
    if not Class.ontology is Class.__bases__[0].ontology:
      if need_pass: need_pass = 0; s.class_content.write("\n")
      s.class_content.write("""  ontology = %s\n""" % (Class.ontology.name))
      
    is_a = [i for i in Class.is_a if isinstance(i, Restriction)]
    for o in is_a + Class.equivalent_to: s.referenced(o)
    need_pass = _class_relation_2_python("is_a"         , 0, is_a               , s.class_content, need_pass)
    need_pass = _class_relation_2_python("equivalent_to", 0, Class.equivalent_to, s.class_content, need_pass)
    return need_pass
  
  def descendant_subclasses(Class):
    yield Class
    for subclass in Class.__subclasses__(): yield from subclass.descendant_subclasses()
    
_MRO_BROKEN_CLASSES = None

def _class_relation_2_owl(Class, Prop, prop_name, functional, value, f):
  if not functional:
    for val in value: _class_relation_2_owl(Class, Prop, prop_name, 1, val, f)
  elif not value is None:
    if ((prop_name == "SubClassOf") or (prop_name == "SubObjectPropertyOf") or (prop_name == "SubDataPropertyOf")) and (value in _TYPES):
      spc = 1
      prop_name = value.name
      if isinstance(Class, PropertyClass):
        if Class._is_data_property(): type = "Data"
        else:                         type = "Object"
        prop_name = prop_name.replace("Propert", "%sPropert" % type)
    else: spc = 0
    
    f.write("<%s>" % prop_name)
    
    if Prop:
      for AProp, annot_value, lang in ANNOTATIONS[Class, Prop, value].items():
        f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
        
    if spc: f.write("%s</%s>\n" % (_owl_name(Class), prop_name))
    else:   f.write("%s%s</%s>\n" % (_owl_name(Class), _owl_name(value), prop_name))
      
def _class_relation_2_n3(Class, Prop, prop_name, functional, value, f):
    if not functional:
        for val in value: _class_relation_2_n3(Class, Prop, prop_name, 1, val, f)
    elif not value is None:
    #if ((prop_name == "SubClassOf") or (prop_name == "SubObjectPropertyOf") or (prop_name == "SubDataPropertyOf")) and (value in _TYPES):
      #spc = 1
      #prop_name = value.name
      #if isinstance(Class, PropertyClass):
      #  if Class._is_data_property(): type = "Data"
      #  else:                         type = "Object"
      #  prop_name = prop_name.replace("Propert", "%sPropert" % type)
    #else: spc = 0
    
        f.write("%s %s %s.\n" % (_n3_name(Class), prop_name, _n3_name(value)))
    
    #if Prop:
    #  for AProp, annot_value, lang in ANNOTATIONS[Class, Prop, value].items():
    #    f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
        
    #if spc: f.write("%s</%s>\n" % (_owl_name(Class), prop_name))
    #else:   f.write("%s%s</%s>\n" % (_owl_name(Class), _owl_name(value), prop_name))
    
def _class_relation_2_rdflib(Class, Prop, prop_name, functional, value, g):
    if not functional:
        for val in value: _class_relation_2_rdflib(Class, Prop, prop_name, 1, val, g)
    elif not value is None:
        g.add((URIref2(_n3_name(Class)),URIref2(prop_name),URIref2(_n3_name(value))))

    
def _class_relation_2_python(prop_name, functional, value, f, need_pass):
  if functional:
    if value is None: return need_pass
    if need_pass: need_pass = 0; f.write("\n")
    f.write("""  %s = %s\n""" % (prop_name, _python_name(value)))
  else:
    if len(value) == 0: return need_pass
    if need_pass: need_pass = 0; f.write("\n")
    if len(value) == 1:
      f.write("""  %s = [%s]\n""" % (prop_name, _python_name(value[0])))
    else:
      f.write("""  %s = [\n""" % prop_name)
      for i in value:
        f.write("""    %s,\n""" % _python_name(i))
      f.write("""  ]\n""")
  return 0


class ThingClass(EntityClass):
  def __init__(Class, name, bases, obj_dict, ontology = None):
    super().__init__(name, bases, obj_dict)
    Class._direct_instances = weakref.WeakSet()
    
  def instances(Class):
    for instance in Class._direct_instances: yield instance
    for subclass in Class.__subclasses__():
      for instance in subclass.instances(): yield instance
      
  def _class_is_a_changed(Class, is_a, Prop, old):
    if Thing in Class.is_a: Class.is_a._remove(Thing)
    if not [superclass for superclass in Class.is_a if isinstance(superclass, EntityClass)]: Class.is_a._set([Thing] + Class.is_a)
    super()._class_is_a_changed(is_a, Prop, old)
    
  def _class_to_python(Class, s):
    need_pass = EntityClass._class_to_python(Class, s)
    if need_pass: s.class_content.write(""" pass\n""")
    
  def _class_to_owl(Class, definition, content):
    definition.write("""<Declaration>%s</Declaration>\n""" % _owl_name(Class))
    _class_relation_2_owl(Class, owl.is_a         , "SubClassOf"       , 0, [Parent for Parent in Class.is_a if (not Parent in _IGNORED_ISA) and (isinstance(Parent, EntityClass) or isinstance(Parent, Restriction))], content)
    _class_relation_2_owl(Class, owl.equivalent_to, "EquivalentClasses", 0, Class.equivalent_to, content)
    for AProp, value, lang in ANNOTATIONS[Class].items():
      content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), Class.ontology.base_iri, Class.owl_separator, Class.name, _owl_name(value, lang)))
    content.write("\n")
    
  def _class_to_n3(Class, definition, content):
    definition.write("""%s a owl:Class.\n""" % _n3_name(Class))
    _class_relation_2_n3(Class, owl.is_a         , "rdfs:subClassOf"    , 0, [Parent for Parent in Class.is_a if (not Parent in _IGNORED_ISA) and (isinstance(Parent, EntityClass) or isinstance(Parent, Restriction))], content)
    _class_relation_2_n3(Class, owl.equivalent_to, "owl:equivalentClass", 0, Class.equivalent_to, content)
    for AProp, value, lang in ANNOTATIONS[Class].items():
       content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), Class.ontology.base_iri, Class.owl_separator, Class.name, _owl_name(value, lang)))
    content.write("\n")
    
  def _class_to_rdflib(Class,g):
    cl = URIref2("%s"% _n3_name(Class))
    g.add((cl, rdflib.RDF.type, rdflib.OWL.Class))
    _class_relation_2_rdflib(Class, owl.is_a         , "rdfs:subClassOf"    , 0, [Parent for Parent in Class.is_a if (not Parent in _IGNORED_ISA) and (isinstance(Parent, EntityClass) or isinstance(Parent, Restriction))], g)
    _class_relation_2_rdflib(Class, owl.equivalent_to, "owl:equivalentClass", 0, Class.equivalent_to, g)
   
    for AProp, value, lang in ANNOTATIONS[Class].items():
        g.add((cl,URIref2("%s"% _n3_name(AProp)),rdflib.Literal(value,lang)))
      
  def _get_class_possible_relations(Class):
    Props = []
    for Prop in PROPS.values():
      if Prop in _HIDDEN_PROPS: continue
      for domain in Prop.domains_indirect():
        if not domain._satisfied_by(Class): break
      else:
        Props.append(Prop)
    return Props

  def _refered_object(self, l):
    if self in l: return
    l.add(self)
    for Class in self.is_a:
      if isinstance(Class, ThingClass): Class._refered_object(l)
    for Class in self.equivalent_to: Class._refered_object(l)


  # Role-fillers as class properties

  def _get_prop_for_self(self, attr):
    Prop = PROPS.get(attr)
    if Prop is None: raise AttributeError("'%s' property is not defined." % attr)
    for domain in Prop.domain:
      if not domain._satisfied_by(self): raise AttributeError("'%s' property has incompatible domain for %s." % (Prop, self))
    return Prop
    
  def __getattr__(self, attr):
    Prop = self._get_prop_for_self(attr)
    functional = Prop.is_functional_for(self)
    
    if functional:
      for r in _ancestor_property_value_restrictions(self, Prop):
        if (r.type == VALUE): return r.Class
      return Prop.get_default_value(self)
    else:
      values = []
      for r in _ancestor_property_value_restrictions(self, Prop):
        if (r.type == VALUE): values.append(r.Class)
      return _CallbackList(values, self, "_on_class_prop_changed", Prop)
    
  def _on_class_prop_changed(self, new, Prop, old):
    if Prop._is_data_property(): Inverse = None
    else:                        Inverse = Prop.inverse_property
    
    previous = set(old)
    news     = set(new)
    removed = previous - news
    added   = news - previous
    for r in list(_ancestor_property_value_restrictions(self, Prop)):
      if (r.type == VALUE):
        if (r.Class in removed) and (r in self.is_a):
          self.is_a.remove(r)
          if Inverse:
            for r2 in r.Class.is_a:
              if isinstance(r2, PropertyValueRestriction) and (r2.Prop is Inverse) and (r2.type == SOME) and (r2.Class is self):
                r.Class.is_a.remove(r2)
                break
    for v in added:
      self.is_a.append(restriction(Prop, VALUE, v))
      if Inverse: v.is_a.append(Inverse(SOME, self))
      
  def __setattr__(self, attr, value):
    if attr in _SPECIAL_ATTRS:
      super().__setattr__(attr, value)
      return
    
    Prop       = self._get_prop_for_self(attr)
    functional = Prop.is_functional_for(self)
    
    if functional:
      if value is None: self._on_class_prop_changed([],      Prop, getattr(self, attr) or [])
      else:             self._on_class_prop_changed([value], Prop, getattr(self, attr) or [])
    else:
      self._on_class_prop_changed(value, Prop, getattr(self, attr))
      
  def __delattr__(self, attr):
    if attr in _SPECIAL_ATTRS:
      super().__delattr__(attr)
      return
    
    Prop = self._get_prop_for_self(attr)
    self._on_class_prop_changed([], Prop, getattr(self, attr))
        
    
  
class PropertyClass(EntityClass):
  def __init__(Prop, name, bases, obj_dict, ontology = None):
    super().__init__(name, bases, obj_dict)
    #Prop.python_name = name
    if not "domain"           in obj_dict: Prop.domain           = []
    if not "range"            in obj_dict: Prop.range            = []
    if not "inverse_property" in obj_dict: EntityClass.__setattr__(Prop, "inverse_property", None)
    else:                                  EntityClass.__setattr__(Prop.inverse_property, "inverse_property", Prop)
    Prop.indexes = {}

  def create_index(Prop, Class = None):
    Prop.indexes[Class] = d = {}
    prop_python_name = Prop.get_python_name()
    for instance in Class.instances():
      d[getattr(instance, prop_python_name, None)] = instance
      
  def get_python_name(self):
    python_names = ANNOTATIONS[self]["python_name"]
    if python_names: return python_names[0]
    return self.name
  python_name = property(get_python_name)
  
  def _class_is_a_changed(Prop, is_a, Prop2, old):
    if Property in Prop.is_a: Prop.is_a._remove(Property)
    if not [superclass for superclass in Prop.is_a if isinstance(superclass, EntityClass)]: Prop.is_a._set([Property] + Prop.is_a)
    super()._class_is_a_changed(is_a, Prop2, old)
    
  def _is_data_property(Prop):
    return Prop.range and ((Prop.range[0] in _PYTHON_2_DATATYPES) or (isinstance(Prop.range[0], OperatorRestriction) and Prop.range[0].Classes[0] in _PYTHON_2_DATATYPES))
    
  def __setattr__(Prop, attr, value):
    if attr == "inverse_property":
      if value is None:
        if Prop.inverse_property: EntityClass.__setattr__(Prop.inverse_property, "inverse_property", None)
        EntityClass.__setattr__(Prop,  "inverse_property", None)
      else:
        EntityClass.__setattr__(Prop,  "inverse_property", value)
        EntityClass.__setattr__(value, "inverse_property", Prop)
    else:
      EntityClass.__setattr__(Prop, attr, value)
      
  def _class_to_python(Prop, s):
    for o in Prop.domain + Prop.range: s.referenced(o)
    if Prop.inverse_property: s.referenced(Prop.inverse_property)
    need_pass = EntityClass._class_to_python(Prop, s)
    need_pass = _class_relation_2_python("domain"          , 0, Prop.domain          , s.class_content, need_pass)
    need_pass = _class_relation_2_python("range"           , 0, Prop.range           , s.class_content, need_pass)
    need_pass = _class_relation_2_python("inverse_property", 1, Prop.inverse_property, s.class_content, need_pass)
    if need_pass: s.class_content.write(""" pass\n""")
    
  def _class_to_owl(Prop, definition, content):
    if Prop._is_data_property(): type = "Data"
    else:                        type = "Object"
    definition.write("""<Declaration>%s</Declaration>\n""" % _owl_name(Prop))
    _class_relation_2_owl(Prop, owl.is_a         , "Sub%sPropertyOf"        % type, 0, [Parent for Parent in Prop.is_a if (not Parent in _IGNORED_ISA) and (isinstance(Parent, EntityClass) or isinstance(Parent, Restriction))], content)
    _class_relation_2_owl(Prop, owl.equivalent_to, "Equivalent%sProperties" % type, 0, Prop.equivalent_to   , content)
    _class_relation_2_owl(Prop, None             , "Inverse%sProperties"    % type, 1, Prop.inverse_property, content)
    _class_relation_2_owl(Prop, owl.domain       , "%sPropertyDomain"       % type, 0, Prop.domain          , content)
    _class_relation_2_owl(Prop, owl.range        , "%sPropertyRange"        % type, 0, Prop.range           , content)
    for Class in Prop.indexes:
      content.write('''<HasKey>''')
      for AProp, annot_value, lang in ANNOTATIONS[Prop, "indexes", Class].items():
        f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
      content.write('''%s%s</HasKey>\n''' % (_owl_name(Class), _owl_name(Prop)))
    for AProp, value, lang in ANNOTATIONS[Prop].items():
      content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), Prop.ontology.base_iri, Prop.owl_separator, Prop.name, _owl_name(value, lang)))
    content.write("\n")
    
  def _class_to_n3(Prop, definition, content):
    definition.write("""%s a rdf:Property.\n""" % _n3_name(Prop))
    _class_relation_2_n3(Prop, owl.is_a         , "rdfs:subPropertyOf"    , 0, [Parent for Parent in Prop.is_a if (not Parent in _IGNORED_ISA) and (isinstance(Parent, EntityClass) or isinstance(Parent, Restriction))], content)
    _class_relation_2_n3(Prop, owl.equivalent_to, "owl:equivalentProperty", 0, Prop.equivalent_to   , content)
    _class_relation_2_n3(Prop, None             , "owl:inverseOf"         , 1, Prop.inverse_property, content)
    _class_relation_2_n3(Prop, owl.domain       , "rdfs:domain"           , 0, Prop.domain          , content)
    _class_relation_2_n3(Prop, owl.range        , "rdfs:range"            , 0, Prop.range           , content)
    #for Class in Prop.indexes:
    #  content.write('''<HasKey>''')
    #  for AProp, annot_value, lang in ANNOTATIONS[Prop, "indexes", Class].items():
    #    f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
    #  content.write('''%s%s</HasKey>\n''' % (_owl_name(Class), _owl_name(Prop)))
    for AProp, value, lang in ANNOTATIONS[Prop].items():
      content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), Prop.ontology.base_iri, Prop.owl_separator, Prop.name, _owl_name(value, lang)))
    content.write("\n")
    
  def _class_to_rdflib(Prop, g):
    g.add((URIref2("%s"% _n3_name(Prop)), rdflib.RDF.type,rdflib.RDF.Property))
    _class_relation_2_rdflib(Prop, owl.is_a         , "rdfs:subPropertyOf"    , 0, [Parent for Parent in Prop.is_a if (not Parent in _IGNORED_ISA) and (isinstance(Parent, EntityClass) or isinstance(Parent, Restriction))], g)
    _class_relation_2_rdflib(Prop, owl.equivalent_to, "owl:equivalentProperty", 0, Prop.equivalent_to   , g)
    _class_relation_2_rdflib(Prop, None             , "owl:inverseOf"         , 1, Prop.inverse_property, g)
    _class_relation_2_rdflib(Prop, owl.domain       , "rdfs:domain"           , 0, Prop.domain          , g)
    _class_relation_2_rdflib(Prop, owl.range        , "rdfs:range"            , 0, Prop.range           , g)
    #for Class in Prop.indexes:
    #  content.write('''<HasKey>''')
    #  for AProp, annot_value, lang in ANNOTATIONS[Prop, "indexes", Class].items():
    #    f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
    #  content.write('''%s%s</HasKey>\n''' % (_owl_name(Class), _owl_name(Prop)))
    #for AProp, value, lang in ANNOTATIONS[Prop].items():
    #  content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), Prop.ontology.base_iri, Prop.owl_separator, Prop.name, _owl_name(value, lang)))
        
  def domains_indirect(self):
    for domain in self.domain: yield domain
    for parent_prop in self.is_a:
      if isinstance(parent_prop, PropertyClass):
        for domain in parent_prop.domain: yield domain
        
  def __call__(self, type, Class, c = None): return PropertyValueRestriction(self, type, Class, c)
  
class AnnotationPropertyClass(EntityClass):
  def __init__(Prop, name, bases, obj_dict, ontology = None):
    super().__init__(name, bases, obj_dict)
    #Prop.python_name = name
    if not "domain" in obj_dict: Prop.domain           = []
    if not "range"  in obj_dict: Prop.range            = []
    
  def get_python_name(self):
    python_names = ANNOTATIONS[self]["python_name"]
    if python_names: return python_names[0]
    return self.name
  python_name = property(get_python_name)
  
  def _class_to_owl(Prop, definition, content):
    definition.write("""<Declaration>%s</Declaration>\n""" % _owl_name(Prop))
    _class_relation_2_owl(Prop, owl.is_a  , "SubAnnotationPropertyOf" , 0, [Parent for Parent in Prop.is_a if (not Parent in _IGNORED_ISA) and (isinstance(Parent, EntityClass) or isinstance(Parent, Restriction))], content)
    _class_relation_2_owl(Prop, owl.domain, "AnnotationPropertyDomain", 0, Prop.domain, content)
    _class_relation_2_owl(Prop, owl.range , "AnnotationPropertyRange" , 0, Prop.range , content)
    for AProp, value, lang in ANNOTATIONS[Prop].items():
      content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), Prop.ontology.base_iri, Prop.owl_separator, Prop.name, _owl_name(value, lang)))
    content.write("\n")
    
  def domains_indirect(self):
    for domain in self.domain: yield domain
    for parent_prop in self.is_a:
      if isinstance(parent_prop, PropertyAnnotationClass):
        for domain in parent_prop.domain: yield domain

_SPECIAL_ATTRS = {"ontology",  "name", "_name", "owl_separator", "is_a", "_old_is_a", "equivalent_to", "_direct_instances", "__class__", "__module__", "__doc__", "__bases__" }

class Thing(metaclass = ThingClass):
  owl_separator = "#"
  ontology      = owl
  name          = _NameDescriptor()
  
  def __init__(self, name = None, ontology = None, label= None,**kargs):
    if (ontology is None) and DEFAULT_ONTOLOGY: ontology = DEFAULT_ONTOLOGY
    if not ontology is None: self.ontology = ontology
    #DW
    if label is not None:
         ANNOTATIONS[self].add_annotation(rdfs.label,label)
    
    if isinstance(self.__class__, _FusionClass):
      self.__dict__["is_a"] = _CallbackList(self.__class__.__bases__, self, "_instance_is_a_changed", "isa")
    else:
      self.__dict__["is_a"] = _CallbackList([self.__class__], self, "_instance_is_a_changed", "isa")
    for attr, value in kargs.items():
      setattr(self, attr, value)
    for superclass in self.is_a: superclass._direct_instances.add(self)
    if not isinstance(self, GeneratedName):
      if name: self.name = _unique_name(self, name)
      else:    self.name = self.generate_default_name()
    self.ontology.add(self)
    
  def _get_is_instance_of(self):    return self.is_a
  def _set_is_instance_of(self, v): self.is_a = v
  is_instance_of = property(_get_is_instance_of, _set_is_instance_of)
  
  def generate_default_name(self):
    Class  = self.is_a[0]
    return _unique_name(self, Class.name.lower(), True)
  
  def _instance_is_a_changed(self, is_a, Prop, old):
    for superclass in old:
      if isinstance(superclass, ThingClass): superclass._direct_instances.discard(self)
    if Thing in self.is_a: self.is_a._remove(Thing)
    #if not self.is_a: self.is_a._set([Thing])
    bases = [base for base in self.is_a if not isinstance(base, Restriction)]
    if   not bases:
      self.is_a._set([Thing] + self.is_a)
      self.__class__ = Thing
    elif len(bases) == 1:
      self.__class__ = bases[0]
    else: # Multi-class object
      self.__class__ = _FusionClass._get_fusion_class(*bases)
    for superclass in self.is_a:
      if isinstance(superclass, ThingClass): superclass._direct_instances.add(self)
      
  #def _get_relations(self): return { relation for relation in self.__dict__.keys() if (not relation in _SPECIAL_ATTRS) and (not relation.startswith("_")) }
  def _get_relations(self): return { relation for relation in self.__dict__.keys() if (not relation in _SPECIAL_ATTRS) and relation in PROPS }
  
  def _get_instance_possible_relations(self, ignore_domainless_properties = False):
    Props = []
    for Prop in PROPS.values():
      if Prop in _HIDDEN_PROPS: continue
      all_domains = set(Prop.domains_indirect())
      if ignore_domainless_properties and (not all_domains):
        for restrict in _ancestor_property_value_restrictions(self, Prop):
          Props.append(Prop)
          break
      else:
        for domain in all_domains:
          if not domain._satisfied_by(self): break
        else:
          Props.append(Prop)
    return Props
  
  def _instance_refered_object(self, l):
    if self in l: return
    l.add(self)
    for Class in self.is_a:          Class._refered_object(l)
    for Class in self.equivalent_to: Class._refered_object(l)
    for attr in self._get_relations():
      value = self.__dict__[attr]
      if   isinstance(value, list):
        for value_x in value:
          if isinstance(value_x, Thing): value_x._instance_refered_object(l)
      elif isinstance(value, Thing): value._instance_refered_object(l)
      
  def __str__(self): return self.name
  def __repr__(self): return "%s.%s" % (self.ontology.name, self.name)
  
  def _instance_to_python(self, s):
    s.instance_definition.write('''%s("%s")''' % (_python_name(self.__class__), self.name))
    relations = self._get_relations()
    for attr in relations:
      s.instance_content.write("""%s.%s = %s\n""" % (_python_name(self), attr, _python_name(self.__dict__[attr])))
      
  def _instance_to_owl(self, definition, content):
    definition.write("""<Declaration>%s</Declaration>\n""" % _owl_name(self))
    
    for Class in self.is_a:
      content.write("<ClassAssertion>")
      for AProp, annot_value, lang in ANNOTATIONS[self, owl.is_a, Class].items():
        content.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
      content.write("%s%s</ClassAssertion>\n" % (_owl_name(Class), _owl_name(self)))
      
    for attr in self._get_relations():
      Prop = PROPS[attr]
      _instance_relation_2_owl(self, Prop, self.__dict__[attr], content)
      
    for AProp, value, lang in ANNOTATIONS[self].items():
      content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), self.ontology.base_iri, self.owl_separator, self.name, _owl_name(value, lang)))
    content.write("\n")
    
    
  def _instance_to_rdflib(self, g):
    g.add((URIref2("%s"% _n3_name(self)),rdflib.RDF.type, rdflib.OWL.Thing))
    
    for Class in self.is_a:
      g.add((URIref2("%s"%_n3_name(self)),rdflib.RDF.type,URIref2("%s"% _n3_name(Class))))
      #for AProp, annot_value, lang in ANNOTATIONS[self, owl.is_a, Class].items():
      #  content.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
      
    for attr in self._get_relations():
      Prop = PROPS[attr]
      _instance_relation_2_rdflib(self, Prop, self.__dict__[attr], g)
      
    #for AProp, value, lang in ANNOTATIONS[self].items():
    #  content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), self.ontology.base_iri, self.owl_separator, self.name, _owl_name(value, lang)))
    for AProp, value, lang in ANNOTATIONS[self].items():
       
        g.add((URIref2("%s"% _n3_name(self)),URIref2("%s"% _n3_name(AProp)),rdflib.Literal(value,lang)))
     
    
  def _instance_to_n3(self, definition, content):
    definition.write("""%s a owl:Thing.\n""" % _n3_name(self))
    
    for Class in self.is_a:
      content.write("%s a %s.\n" % (_n3_name(self), _n3_name(Class)))
      #for AProp, annot_value, lang in ANNOTATIONS[self, owl.is_a, Class].items():
      #  content.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
      
    for attr in self._get_relations():
      Prop = PROPS[attr]
      _instance_relation_2_n3(self, Prop, self.__dict__[attr], content)
      
    for AProp, value, lang in ANNOTATIONS[self].items():
        content.write('''<AnnotationAssertion>%s<IRI>%s%s%s</IRI>%s</AnnotationAssertion>\n''' % (_owl_name(AProp), self.ontology.base_iri, self.owl_separator, self.name, _owl_name(value, lang)))
    content.write("\n")
    
  def __attrs__(self): # Not Python standard, but used by EditObj
    import owlready.editor
    return { prop.python_name for prop in self._get_instance_possible_relations(owlready.editor.IGNORE_DOMAINLESS_PROPERTY) } | self.__dict__.keys()
    
  def __getattr__(self, attr):
    Prop = PROPS.get(attr)
    if Prop is None:
      try:    repr_self = repr(self)
      except: repr_self = "<instance of %s>" % self.__class__
      raise AttributeError("%s has no attribute '%s', and '%s' property is not defined." % (repr_self, attr, attr))
    for domain in Prop.domain:
      if not domain._satisfied_by(self):
        try:    repr_self = repr(self)
        except: repr_self = "<instance of %s>" % self.__class__
        raise AttributeError("%s has no attribute '%s', and '%s' property has incompatible domain." % (repr_self, attr, attr))
        
    if Prop.is_functional_for(self): value = Prop.get_default_value(self)
    else:                            value = []
    setattr(self, attr, value)
    return getattr(self, attr) # __setattr__ may change the value, so we need to get it again
  
  def __setattr__(self, attr, value):
    if attr in _SPECIAL_ATTRS:
      if attr == "is_a":
        self.is_a.reinit(value)
      else:
        object.__setattr__(self, attr, value)
    else:
      Prop = PROPS.get(attr)
      if Prop:
        old_value = self.__dict__.get(attr, None)
        if Prop.is_functional_for(self):
          if Prop.inverse_property:
            if not old_value is None: del_relation(old_value, Prop.inverse_property, self)
          object.__setattr__(self, attr, value)
          if Prop.inverse_property and (not value is None):
            add_relation(value, Prop.inverse_property, self)
        else:
          if isinstance(value, list):
            if Prop.inverse_property:
              value = _CallbackList(value, self, "_prop_with_inverse_changed", Prop)
            object.__setattr__(self, attr, value)
            if Prop.inverse_property:
              for i in value: add_relation(i, Prop.inverse_property, self)
          else: raise ValueError("Property '%s' is not functional, cannot assign directly (use .append() or assign a list)." % attr)
        if Prop.indexes:
          for Class in Prop.indexes:
            if isinstance(self, Class):
              try: del Prop.indexes[Class][old_value]
              except: pass
              Prop.indexes[Class][value] = self
      else:
        object.__setattr__(self, attr, value)
        
  def _prop_with_inverse_changed(self, new, Prop, old):
    old = set(old)
    new = set(new)
    for removed in old - new:
      del_relation(removed, Prop.inverse_property, self)
    for added   in new - old:
      add_relation(added, Prop.inverse_property, self)
      
  def closed_world(self, Properties = None): close_world(self, Properties) # For backward compatibility



        
def has_relation(subject, Prop, object):
  if Prop.is_functional_for(subject): return getattr(subject, Prop.python_name) == object
  else:                               return object in getattr(subject, Prop.python_name)
  
def _ancestor_property_value_restrictions(clazz, Prop):
  #DW
  return None
  for restrict in (clazz.is_a + clazz.equivalent_to ):
    x = isinstance(restrict, PropertyValueRestriction)      
    if x:
        y = restrict.Prop is Prop
        if y:
            yield restrict
    if isinstance(restrict, AndRestriction):
      for clazz2 in restrict.Classes: yield from _ancestor_property_value_restrictions(clazz2, Prop)
    #TODO Check this without this restriction i fet an infinit loop - after running hermit
   
    elif isinstance(restrict, EntityClass): 
            
        yield from _ancestor_property_value_restrictions(restrict, Prop)
    
def get_relations(subject, Prop):
  Props = set(Prop.descendant_subclasses())
  values = set()
  for sub_Prop in Props:
    if sub_Prop.is_functional_for(subject):
      values.add(getattr(subject, sub_Prop.python_name))
    else:
      values.update(getattr(subject, sub_Prop.python_name))
  values.discard(None)
  return list(values)

def add_relation(subject, Prop, object):
  if has_relation(subject, Prop, object): return
  if Prop.is_functional_for(subject):
    setattr(subject, Prop.python_name, object)
  else:
    values = getattr(subject, Prop.python_name)
    if not object in values: values.append(object)
    
def del_relation(subject, Prop, object):
  if Prop.is_functional_for(subject):
    value = getattr(subject, Prop.python_name)
    if value is object: setattr(subject, Prop.python_name, None)
  else:
    values = getattr(subject, Prop.python_name)
    if object in values: values.remove(object)
    
    
class Property(metaclass = PropertyClass):
  owl_separator = "#"
  ontology      = owl
  name          = _NameDescriptor()
  
  @classmethod
  def get_default_value(Prop, instance):
    if Prop.range:
      if   (str   in Prop.range) or (normstr in Prop.range): return ""
      elif (int   in Prop.range): return 0
      elif (float in Prop.range): return 0.0
      elif (bool  in Prop.range): return False
    for restrict in _ancestor_property_value_restrictions(instance, Prop):
      if restrict.type == ONLY:
        if   (str   is restrict.Class) or (normstr is restrict.Class): return ""
        elif (int   is restrict.Class): return 0
        elif (float is restrict.Class): return 0.0
        elif (bool  is restrict.Class): return False
    return None
    
  @classmethod
  def is_functional_for(Prop, o): # o can be a Class or an Instance
    # XXX cache the results
    ranges  = set(Prop.range)
    singles = set()
    for restrict in _ancestor_property_value_restrictions(o, Prop):
      if     restrict.type == ONLY:
        ranges.add(restrict.Class)
      elif ((restrict.type == EXACTLY) or (restrict.type == MAX)) and (restrict.cardinality == 1):
        singles.add(restrict.Class)
    return not ranges.isdisjoint(singles)
    
class FunctionalProperty(Property):
  @classmethod
  def is_functional_for(Prop, o): return True

class InverseFunctionalProperty(Property): pass
class TransitiveProperty       (Property): pass
class SymmetricProperty        (Property): pass
class AsymmetricProperty       (Property): pass
class ReflexiveProperty        (Property): pass
class IrreflexiveProperty      (Property): pass


class AnnotationProperty(metaclass = AnnotationPropertyClass):
  owl_separator = "#"
  ontology      = owl
  name          = _NameDescriptor()
  
  @classmethod
  def is_functional_for(Prop, o): return False

def _create_base_properties(): # In a func to avoid polluting the module with global names like "label"
  class backwardCompatibleWith(AnnotationProperty): ontology = owl
  class comment               (AnnotationProperty): ontology = rdfs
  class deprecated            (AnnotationProperty): ontology = owl
  class incompatibleWith      (AnnotationProperty): ontology = owl
  class isDefinedBy           (AnnotationProperty): ontology = rdfs
  class label                 (AnnotationProperty): ontology = rdfs
  class priorVersion          (AnnotationProperty): ontology = owl
  class seeAlso               (AnnotationProperty): ontology = rdfs
  class versionInfo           (AnnotationProperty): ontology = owl
  
  class is_a                  (Property):           ontology = owl
  class equivalent_to         (Property):           ontology = owl
  class range                 (Property):           ontology = owl; domain = [Property]
  class domain                (Property):           ontology = owl; domain = [Property]
_create_base_properties()

class Nothing(Thing): pass

_IGNORED_ISA = { Thing, Property }
_TYPES = { FunctionalProperty, InverseFunctionalProperty, TransitiveProperty, SymmetricProperty, AsymmetricProperty, ReflexiveProperty, IrreflexiveProperty }
_HIDDEN_PROPS = { owl.is_a, owl.equivalent_to } | _TYPES

_PYTHON_2_DATATYPES = {
  int                : "http://www.w3.org/2001/XMLSchema#integer",
  bool               : "http://www.w3.org/2001/XMLSchema#boolean",
  float              : "http://www.w3.org/2001/XMLSchema#decimal",
  str                : "http://www.w3.org/2001/XMLSchema#string",
  normstr            : "http://www.w3.org/2001/XMLSchema#normalizedString",
  datetime.datetime  : "http://www.w3.org/2001/XMLSchema#dateTime",
  datetime.date      : "http://www.w3.org/2001/XMLSchema#date",
  datetime.time      : "http://www.w3.org/2001/XMLSchema#time",
  datetime.timedelta : "http://www.w3.org/2001/XMLSchema#duration",
  }

_DATATYPES_2_PYTHON = { val : key for (key, val) in _PYTHON_2_DATATYPES.items() }
_DATATYPES_2_PYTHON["http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral"] = str
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#byte"]                   = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#short"]                  = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#int"]                    = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#long"]                   = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#unsignedByte"]           = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#unsignedShort"]          = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#unsignedInt"]            = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#unsignedLong"]           = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#negativeInteger"]        = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#nonNegativeInteger"]     = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#nonPositiveInteger"]     = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#positiveInteger"]        = int
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#double"]                 = float
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#float"]                  = float
_DATATYPES_2_PYTHON["http://www.w3.org/2002/07/owl#real"]                      = float
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#anyURI"]                 = normstr
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#Name"]                   = normstr
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#date"]                   = datetime.date
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#time"]                   = datetime.time
_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#dateTime"]               = datetime.datetime
#_DATATYPES_2_PYTHON["http://www.w3.org/2001/XMLSchema#duration"]               = datetime.timedelta

if pyxb:
  for datatype in pyxb.binding.datatypes._PrimitiveDatatypes + pyxb.binding.datatypes._DerivedDatatypes:
    datatype_name = "http://www.w3.org/2001/XMLSchema#%s" % datatype.__name__
    if datatype_name in _DATATYPES_2_PYTHON: continue # Builtin / hardcoded datatype
    _PYTHON_2_DATATYPES[datatype]      = datatype_name
    _DATATYPES_2_PYTHON[datatype_name] = datatype
    

_OWL_NAME = {clazz : '''<Datatype IRI="%s"/>''' % iri for (clazz, iri) in _PYTHON_2_DATATYPES.items() }

_N3_NAME = {
  int     : "xsd:integer",
  bool    : "xsd:boolean",
  float   : "xsd:decimal",
  str     : "xsd:string",
  normstr : "xsd:normalizedString",
}

def _owl_object_type(self):
  if   (self is int) or (self is bool) or (self is float) or (self is str): return "Data"
  elif isinstance(self, int) or isinstance(self, bool) or isinstance(self, float) or isinstance(self, str): return "Data"
  elif isinstance(self, ThingClass) or isinstance(self, Thing): return "Object"
  elif isinstance(self, Restriction): return self._owl_object_type()
  elif isinstance(self, PropertyClass):
    if self._is_data_property(): return "Data"
    else:                        return "Object"
  raise ValueError
  

def _owl_type(self):
  if   isinstance(self, ThingClass):              return """Class"""
  elif isinstance(self, PropertyClass):
    if self._is_data_property():                  return """DataProperty"""
    else:                                         return """ObjectProperty"""
  elif isinstance(self, AnnotationPropertyClass): return """AnnotationProperty"""
  elif isinstance(self, Thing):                   return """NamedIndividual"""
  raise ValueError
  
def _owl_type_plural(self):
  if   isinstance(self, ThingClass):              return """Classes"""
  elif isinstance(self, PropertyClass):
    if self._is_data_property():                  return """DataProperties"""
    else:                                         return """ObjectProperties"""
  elif isinstance(self, AnnotationPropertyClass): return """AnnotationProperties"""
  elif isinstance(self, Thing):                   return """NamedIndividuals"""
  raise ValueError
  
def _owl_name(self, lang = ""):
  if   self in _OWL_NAME: return _OWL_NAME[self]
  elif(isinstance(self, EntityClass) or
       isinstance(self, Thing) or isinstance(self, rdflib.URIRef)):      return """<%s IRI="%s%s%s"/>""" % (_owl_type(self), self.ontology.base_iri, self.owl_separator, escape(self.name))
  elif isinstance(self, Restriction): return self._restriction_to_owl()
  elif isinstance(self, bool):        return """<Literal datatypeIRI="&xsd;boolean">%s</Literal>""" % self
  elif isinstance(self, int):         return """<Literal datatypeIRI="&xsd;integer">%s</Literal>"""     % self
  elif isinstance(self, float):       return """<Literal datatypeIRI="&xsd;decimal">%s</Literal>"""   % self
  elif isinstance(self, normstr):     return """<Literal datatypeIRI="&xsd;normalizedString"%s>%s</Literal>"""  % ((' xml:lang="%s"' % lang) if lang else "", escape(self))
  elif isinstance(self, str):         return """<Literal datatypeIRI="&xsd;string"%s>%s</Literal>"""            % ((' xml:lang="%s"' % lang) if lang else "", escape(self))
  elif isinstance(self, datetime.date):        return """<Literal datatypeIRI="&xsd;date">%s</Literal>"""  % self.isoformat()
  elif isinstance(self, datetime.time):        return """<Literal datatypeIRI="&xsd;time">%s</Literal>"""  % self.isoformat()
  elif isinstance(self, datetime.datetime):    return """<Literal datatypeIRI="&xsd;dateTime">%s</Literal>"""  % self.isoformat()
  elif isinstance(self, datetime.timedelta):   return """<Literal datatypeIRI="&xsd;duration">P%sDT%sS</Literal>"""  % (self.days, self.seconds)
  raise ValueError(self)
  
def _n3_name(self, lang = ""):
  if   self in _N3_NAME: return _N3_NAME[self]
  elif(isinstance(self, EntityClass) or
       isinstance(self, Thing)):      return """<%s%s%s>""" % (self.ontology.base_iri, self.owl_separator, escape(self.name))
  elif isinstance(self, Restriction): return self._restriction_to_n3()
  elif isinstance(self,rdflib.URIRef): return self
  elif isinstance(self, bool):        return str(self).lower()
  elif isinstance(self, int):         return  "%s"  % self
  elif isinstance(self, float):       return  "%s"  % self
  elif isinstance(self, normstr):     return '"%s"' % escape(self)
  elif isinstance(self, str):         return '"%s"' % escape(self)
  raise ValueError(self)

def _owl_prop_name(self):
  return "%s:%s" % (self.ontology.name, self.name)

_PYTHON_NAME = {
  int     : "int",
  bool    : "bool",
  float   : "float",
  str     : "str",
  normstr : "NormalizedString",
  }
def _python_name(x):
  if isinstance(x, list): return "[%s]" % ", ".join(_python_name(i) for i in x)
  if isinstance(x, Restriction): return repr(x)
  return _PYTHON_NAME.get(x) or repr(x)

def _instance_relation_2_owl(obj, Prop, value, f):
  if (value is None) or (value == ""): return
  if isinstance(value, list):
    for val in value: _instance_relation_2_owl(obj, Prop, val, f)
  else:
    prop_type = _owl_type(Prop)
    f.write("<%sAssertion>" % prop_type)
    for AProp, annot_value, lang in ANNOTATIONS[obj, Prop, value].items():
      f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
    f.write("%s%s%s</%sAssertion>\n" % (_owl_name(Prop), _owl_name(obj), _owl_name(value), prop_type))
  
def _instance_relation_2_rdflib(obj, Prop, value, g):
  if (value is None) or (value == ""): return
  if isinstance(value, list):
    for val in value: _instance_relation_2_rdflib(obj, Prop, val, g)
  else:
    
    if len(Prop.range)==0:
        g.add((URIref2("%s"%_n3_name(obj)),URIref2("%s"%_n3_name(Prop)),URIref2("%s"%_n3_name(value))))
    else:
        for rangeCls in Prop.range: #gehe durch die Klassen im Range und Teste zu welcer value gehört  
            if isinstance(rangeCls, ThingClass):
                g.add((URIref2("%s"%_n3_name(obj)),URIref2("%s"%_n3_name(Prop)),URIref2("%s"%_n3_name(value))))
            else: #assume is literal
                g.add((URIref2("%s"%_n3_name(obj)),URIref2("%s"%_n3_name(Prop)),rdflib.Literal(rangeCls(value))))
                
     
    #for AProp, annot_value, lang in ANNOTATIONS[obj, Prop, value].items():
    #  f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
    

def _instance_relation_2_n3(obj, Prop, value, f):
  if (value is None) or (value == ""): return
  if isinstance(value, list):
    for val in value: _instance_relation_2_n3(obj, Prop, val, f)
  else:
    f.write("%s %s %s.\n" % (_n3_name(obj), _n3_name(Prop), _n3_name(value)))
    #for AProp, annot_value, lang in ANNOTATIONS[obj, Prop, value].items():
    #  f.write('''\n<Annotation>%s%s</Annotation>\n''' % (_owl_name(AProp), _owl_name(annot_value, lang)))
    
def NOT(x): return ~ x

class Restriction(object):
  def __and__ (a, b): return AndRestriction(a, b)
  def __or__  (a, b): return OrRestriction (a, b)
  def __invert__ (a): return NotRestriction(a)
  def _class_to_python(self, s): s.class_content.write(repr(self))
  def _referenced(self, s): pass
  
class OneOfRestriction(Restriction):
  def __init__(self, *instances):
    super().__init__()
    self.instances = instances
    
  def _owl_object_type(self): return _owl_object_type(self.instances[0])
  
  def _satisfied_by(self, x):
    return x in self.instances
  
  def _refered_object(self, l):
    for instance in self.instances: instance._instance_refered_object(l)
    
  def _restriction_to_owl(self):
    return """\n<ObjectOneOf>%s</ObjectOneOf>""" % "".join(_owl_name(instance) for instance in self.instances)

 #todo restrictions in rdflib
  def _restriction_to_rdflib(self):
     return
 
  def _restriction_to_n3(self):
    return """[ owl:oneOf (%s) ]""" % " ".join(_n3_name(instance) for instance in self.instances)
    
  def __repr__(self): return "one_of(%s)" % ", ".join(_python_name(instance) for instance in self.instances)
one_of = OneOfRestriction

class OperatorRestriction(Restriction):
  def __init__(self, *Classes):
    super().__init__()
    new_Classes = list(Classes)
    for Class in Classes:
      if isinstance(Class, self.__class__):
        index = new_Classes.index(Class)
        new_Classes[index : index + 1] = Class.Classes
    self.Classes = new_Classes
    
  def _owl_object_type(self): return _owl_object_type(self.Classes[0])
  
  def _refered_object(self, l):
    for Class in self.Classes: Class._refered_object(l)

  #todo restrictions in rdflib
  def _restriction_to_rdflib(self):
      return

  def _restriction_to_owl(self):
    type = self._owl_object_type()
    return "\n<%s%s>%s</%s%s>" % (type, self._OWL_TAG, "".join(_owl_name(Class) for Class in self.Classes), type, self._OWL_TAG)
    
  def _restriction_to_n3(self):
    return "[ %s (%s) ]" % (self._N3_TAG, " ".join(_n3_name(Class) for Class in self.Classes))
  
  def _referenced(self, s):
    for Class in self.Classes: s.referenced(Class)
  def __repr__(self): return "(%s)" % self._PYTHON_OP.join(_python_name(c) for c in self.Classes)

class OrRestriction(OperatorRestriction):
  _PYTHON_OP       = " | "
  _OWL_TAG         = "UnionOf"
  _N3_TAG          = "owl:unionOf"
  
  def __init__(self, *Classes):
    if len(Classes) < 2: raise ValueError("Need at least 2 elements for OR!")
    super().__init__(*Classes)
    
  def _satisfied_by(self, x):
    for Class in self.Classes:
      if Class._satisfied_by(x): return 1
    return 0

class AndRestriction(OperatorRestriction):
  _PYTHON_OP       = " & "
  _OWL_TAG         = "IntersectionOf"
  _N3_TAG          = "owl:intersectionOf"
  
  def __init__(self, *Classes):
    if len(Classes) < 2: raise ValueError("Need at least 2 elements for AND!")
    super().__init__(*Classes)
    
  def _satisfied_by(self, x):
    for Class in self.Classes:
      if not Class._satisfied_by(x): return 0
    return 1
  
class NotRestriction(OperatorRestriction):
  def __init__(self, Class):
    super().__init__()
    self.Class = Class
  
  def _owl_object_type(self): return _owl_object_type(self.Class)
  
  def _satisfied_by(self, x):
    return not self.Class._satisfied_by(x)
  
  def _restriction_to_owl(self):
    return "\n<ObjectComplementOf>%s</ObjectComplementOf>" % _owl_name(self.Class)

  #todo restrictions in rdflib
  def _restriction_to_rdflib(self):
      return
    
  def _restriction_to_n3(self):
    return "[ owl:complementOf %s ]" % _n3_name(self.Class)
    
  def _referenced(self, s): s.referenced(self.Class)
  
  def __repr__(self): return "NOT(%s)" % (self.Class)
  
SOME    = "SOME"
ONLY    = "ONLY"
#EVERY   = "EVERY"
EXACTLY = "EXACTLY"
MIN     = "MIN"
MAX     = "MAX"
VALUE   = "VALUE"
class PropertyValueRestriction(Restriction):
  def __init__(self, Prop, type, Class, c = None):
    super().__init__()
    if not c is None:
      self.cardinality = Class
      self.Class       = c
    else:
      self.Class = Class
      
    if isinstance(Prop, str): Prop = PROPS[Prop]
    
    self.Prop  = Prop
    self.type  = type
    
    if type == VALUE:
      if isinstance(self.Class, Restriction) or isinstance(self.Class, ThingClass): raise ValueError("VALUE restriction expects an instance!")
    else:
      if isinstance(self.Class, Thing): raise ValueError("%s restriction expects an ontology class!" % type)
      
  def _owl_object_type(self): return _owl_object_type(self.Prop)
  
  def _satisfied_by(self, x):
    if isinstance(x, EntityClass): return 1 # XXX not doable on classes
    
    if   self.type == "SOME":
      for obj in get_relations(x, self.Prop):
        if isinstance(obj, self.Class): return 1
      return 0
    
    elif self.type == "ONLY":
      for obj in get_relations(x, self.Prop):
        if not isinstance(obj, self.Class): return 0
      return 1
    
    elif self.type == "VALUE":
      for obj in get_relations(x, self.Prop):
        if obj is self.Class: return 1
      return 0
    
    else:
      nb = 0
      for obj in get_relations(x, self.Prop):
        if isinstance(obj, self.Class): nb += 1
      if   self.type == "MIN":     return nb >= self.cardinality
      elif self.type == "MAX":     return nb <= self.cardinality
      elif self.type == "EXACTLY": return nb == self.cardinality
      
  def _refered_object(self, l):
    if self.type == "VALUE": self.Class._instance_refered_object(l)
    else:                    self.Class._refered_object(l)
    
  def _restriction_to_owl(self):
    if self.Prop._is_data_property(): prop_type = "Data"
    else:                             prop_type = "Object"
    if (self.type == SOME) or (self.type == ONLY) or (self.type == VALUE):
      s = """\n<%s%s>""" % (prop_type, _TYPE_2_TAG[self.type])
    else:
      s = """\n<%s%s cardinality="%s">""" % (prop_type, _TYPE_2_TAG[self.type], self.cardinality)
    s += _owl_name(self.Prop)
    s += _owl_name(self.Class)
    s += """</%s%s>""" % (prop_type, _TYPE_2_TAG[self.type])
    return s
    
#todo restrictions in rdflib
  def _restriction_to_rdflib(self):
      return

  def _restriction_to_n3(self):
    if (self.type == SOME) or (self.type == ONLY) or (self.type == VALUE):
      return """[ owl:onProperty %s; %s %s ]""" % (_n3_name(self.Prop), _TYPE_2_N3_TAG[self.type], _n3_name(self.Class))
    else:
      return """[ owl:onProperty %s; owl:onClass %s; %s %s ]""" % (_n3_name(self.Prop), _n3_name(self.Class), _TYPE_2_N3_TAG[self.type], self.cardinality)
    
  def _referenced(self, s):
    s.referenced(self.Class)
    s.referenced(self.Prop)
    
  def __repr__(self):
    if (self.type == "SOME") or (self.type == "ONLY") or (self.type == "VALUE"):
      return """%s(%s, %s)""" % (self.Prop, self.type, _python_name(self.Class))
    else:
      return """%s(%s, %s, %s)""" % (self.Prop, self.type, self.cardinality, _python_name(self.Class))
      
restriction = PropertyValueRestriction

_TYPE_2_TAG = {
  SOME    : "SomeValuesFrom",
  ONLY    : "AllValuesFrom",
  EXACTLY : "ExactCardinality",
  MIN     : "MinCardinality",
  MAX     : "MaxCardinality",
  VALUE   : "HasValue",
  }
_TYPE_2_N3_TAG = {
  SOME    : "owl:someValuesFrom",
  ONLY    : "owl:allValuesFrom",
  EXACTLY : "owl:cardinality",
  MIN     : "owl:minCardinality",
  MAX     : "owl:maxCardinality",
  VALUE   : "owl:hasValue",
  }


def _keep_most_specific(s, consider_equivalence = True):
  if consider_equivalence:
    testsubclass = issubclass
  else:
    testsubclass = lambda parent, child: type.__subclasscheck__(child, parent)
  r = set()
  for i in s:
    for j in s:
      if i is j: continue
      if testsubclass(j, i): break
    else:
      r.add(i)
  return r


_RULE_REGEXP = re.compile("<DLSafeRule>.*?</DLSafeRule>", re.MULTILINE | re.DOTALL)
class Rules(object):
  def __init__(self, base_iri):
    #self.filename = filename
    #if not os.path.isabs(self.filename):
    #  for dir in onto_path:
    #    filename = os.path.join(dir, self.filename)
    #    if os.path.exists(filename):
    #      self.filename = filename
    #      break
    self.base_iri = base_iri
    self.name     = base_iri.rsplit("/", 1)[-1]
    if self.name.endswith(".owl"): self.name = self.name[:-4]
        
  def __repr__(self): return 'Rules("%s")' % self.base_iri

  def get_rules(self):
    s = _open_onto_file(self.base_iri, self.name).read()
    return "\n".join(_RULE_REGEXP.findall(s))


class _HashableTriple(list):
  def __hash__(self): return hash(tuple(self))

class Annotationss():
  def __init__(self):
    self.dict = weakref.WeakKeyDictionary()
  
  def __len__(self):
    l = 0
    for annotations in self.dict.values(): l += len(annotations)
    return l
    
  def keys    (self): return self.dict.keys()
  def values  (self): return self.dict.values()
  def items   (self): return self.dict.items()
  def __iter__(self): return self.dict.__iter__()
  
  def __getitem__(self, key):
    if isinstance(key, tuple) : key = _HashableTriple(key)
    if not key in self.dict: self.dict[key] = Annotations(key)
    return self.dict[key]
    
  def get(self, key):
    if key in self.dict: return self[key]
    return None    
    

class Annotations(object):
  def __init__(self, obj):
    self.obj    = obj
    self.values = {}
    self.langs  = {}
    
  def __len__(self):
    l = 0
    for values in self.values.values(): l += len(values)
    return l
    
  def keys  (self): return self.values.keys()
  def values(self):
    l = []
    for values in  self.values.values(): l += values
    return l
  def items(self):
    for prop in self.values:
      values = self.values[prop]
      langs  = self.langs [prop]
      for i in range(len(values)): yield prop, values[i], langs[i]
  def __iter__(self): return self.values.__iter__()
      
  def langs_for_prop(self): return set(self.langs[key])
  
  def _split_key_lang(self, key):
    if isinstance(key, tuple): key, lang = key
    else:                      lang = ""
    if isinstance(key, str): key = ANNOT_PROPS[key]
    
    if not key in self.values:
      self.values[key] = []
      self.langs [key] = []
      
    return key, lang
    
  def get_first(self, key, default = ""):
    annots = self[key]
    if annots: return annots[0]
    return default
  
  def __getitem__(self, key):
    key, lang = self._split_key_lang(key)
    aprops    = list(key.descendant_subclasses())
    
    if len(aprops) == 1:
      if not lang: return self.values[key]
      values = self.values[key]
      langs  = self.langs [key]
      return [values[i] for i in range(len(values)) if langs[i] == lang]
    else:
      r = []
      if not lang: 
        for key in aprops:
          if key in self.values: r += self.values[key]
      else:
        for key in aprops:
          if key in self.values:
            values = self.values[key]
            langs  = self.langs [key]
            r += [values[i] for i in range(len(values)) if langs[i] == lang]
      return r
      
  def __delitem__(self, key):
    key, lang = self._split_key_lang(key)
    aprops    = list(key.descendant_subclasses())
    
    if not lang:
      for key in aprops:
        if key in self.values:
          del self.values[key]
          del self.langs [key]
    else:
      for key in aprops:
        if key in self.values:
          values = self.values[key]
          langs  = self.langs [key]
          self.values[key] = [values[i] for i in range(len(values)) if langs[i] != lang]
          self.langs [key] = [langs [i] for i in range(len(langs )) if langs[i] != lang]
          
  def __setitem__(self, key, value):
    key, lang = self._split_key_lang(key)
    if key is owlready_ontology.python_name: old_python_name = self.obj.python_name
    
    values = self.values[key]
    langs  = self.langs [key]
    for i in range(len(values)):
      if langs[i] == lang:
        values[i] = value
        break
    else:
      values.append(value)
      langs .append(lang)
      
    if key is owlready_ontology.python_name:
      if   isinstance(self.obj, PropertyClass):
        del PROPS[old_python_name]
        if value in PROPS: warnings.warn("Dupplicated Property name '%s'!" % value, OwlReadyDupplicatedNameWarning, 2)
        PROPS[value] = self.obj
      elif isinstance(self.obj, AnnotationPropertyClass):
        del ANNOT_PROPS[old_python_name]
        if value in PROPS: warnings.warn("Dupplicated AnnotationProperty name '%s'!" % value, OwlReadyDupplicatedNameWarning, 2)
        ANNOT_PROPS[value] = self.obj
      
  def add_annotation(self, key, value):
    if value is None:
        raise ValueError("Value is None")  
      
    key, lang = self._split_key_lang(key)
    if key is owlready_ontology.python_name: old_python_name = self.obj.python_name
    
    values = self.values[key]
    langs  = self.langs [key]
    values.append(value)
    langs .append(lang)
    
    if key is owlready_ontology.python_name:
      if   isinstance(self.obj, PropertyClass):           del       PROPS[old_python_name]; PROPS      [value] = self.obj
      elif isinstance(self.obj, AnnotationPropertyClass): del ANNOT_PROPS[old_python_name]; ANNOT_PROPS[value] = self.obj
      
  def del_annotation(self, key, value):
    key, lang = self._split_key_lang(key)
    
    values = self.values[key]
    langs  = self.langs [key]
    for i in range(len(values)):
      if (values[i] == value) and (langs[i] == lang):
        if key is owlready_ontology.python_name:
          if   isinstance(self.obj, PropertyClass):           del PROPS      [values[i]]
          elif isinstance(self.obj, AnnotationPropertyClass): del ANNOT_PROPS[values[i]]
        del values[i]
        del langs [i]
        break

  def __repr__(self):
    s = "<Annotations for %s:\n" % self.obj
    for aprop, value, lang in self.items():
      s += "  %s: %s%s\n" % (aprop, value, (" (%s)" % lang) if lang else "")
    s += ">"
    return s
    
ANNOTATIONS = Annotationss()


class _FusionClass(ThingClass):
  ontology = anonymous
  
  def _class_to_owl(Class, definition, content): pass
  
  _FUSION_CLASSES = {}
  
  @staticmethod
  def _get_fusion_class(*Classes):
    if len(set(Classes)) == 1: return Classes[0]
    Classes = tuple(sorted(Classes, key = lambda Class: Class.__name__))
    if Classes in _FusionClass._FUSION_CLASSES: return _FusionClass._FUSION_CLASSES[Classes]
#    d = {}
#    exec("""
#class Fusion(%s):
#  pass
#    """ % (", ".join(Class.__name__ for Class in Classes)))
    name = " & ".join(Class.__name__ for Class in Classes) 
    #fusion_class = _FusionClass._FUSION_CLASSES[Classes] = type.__new__(ThingClass, name, Classes, {})
    fusion_class = _FusionClass._FUSION_CLASSES[Classes] = _FusionClass(name, Classes, { "ontology" : anonymous })
    return fusion_class


def close_world(self, Properties = None, close_instance_list = True, recursive = True):
  if isinstance(self, Thing): # An instance
    if Properties is None:
      Properties2 = (Prop for Prop in self._get_instance_possible_relations() if (not Prop._is_data_property()) and (not Prop in _HIDDEN_PROPS))
    else:
      Properties2 = Properties
      
    for Prop in Properties2:
      range_instances = get_relations(self, Prop)
      range_classes = []
      for r in _ancestor_property_value_restrictions(self, Prop):
        if (r.type == SOME): range_classes.append(r.Class)
      if range_instances: range_classes.append(one_of(*range_instances))
      
      if not range_classes:                      self.is_a.append(NOT(restriction(Prop, SOME, Thing)))
      elif issubclass(Prop, FunctionalProperty): pass
      elif len(range_classes) == 1:              self.is_a.append(restriction(Prop, ONLY, range_classes[0]))
      else:                                      self.is_a.append(restriction(Prop, ONLY, OrRestriction(*range_classes)))
      
  else: # A class
    if close_instance_list:
      instances = list(self.instances())
      if instances: self.is_a.append(one_of(*instances))
      
    if Properties is None:
      Properties2 = (Prop for Prop in self._get_class_possible_relations() if (not Prop._is_data_property()) and (not Prop in _HIDDEN_PROPS))
    else:
      Properties2 = Properties
      
    instances  = set(self.instances())
    subclasses = set(self.descendant_subclasses())
    
    for Prop in Properties2:
      range_instances = []
      range_classes = []
      for subclass in subclasses: # subclasses includes self
        for r in _ancestor_property_value_restrictions(subclass, Prop):
          if   r.type is VALUE:
            range_instances.append(r.Class)
          elif (r.type is SOME) or ((r.type is EXACTLY) and r.cardinality >= 1) or ((r.type is MIN) and r.cardinality >= 1):
            if isinstance(r.Class, OneOfRestriction): range_instances.extend(r.Class.instances)
            else: range_classes.append(r.Class)

      for instance in instances:
        range_instances += get_relations(instance, Prop)
        for r in _ancestor_property_value_restrictions(instance, Prop):
          if (r.type == SOME): range_classes.append(r.Class)
          
        
      if range_instances: range_classes.append(one_of(*range_instances))
      if   len(range_classes) == 1: self.is_a.append(restriction(Prop, ONLY, range_classes[0]))
      elif range_classes:           self.is_a.append(restriction(Prop, ONLY, OrRestriction(*range_classes)))
      else:                         self.is_a.append(NOT(restriction(Prop, SOME, Thing)))
      
    if recursive:
      subclasses.discard(self)
      for subclass in subclasses: close_world(subclass, Properties, close_instance_list, False)
      for instance in instances:  close_world(instance, Properties, close_instance_list, False)
        
def partition(mother, *children):
  mother.is_a.append(OrRestriction(*children))
  AllDisjoint(*children)
  
OWLREADY_ONTOLOGY_IRI = "http://www.lesfleursdunormal.fr/static/_downloads/owlready_ontology.owl"

onto_path.insert(0, os.path.dirname(__file__))
owlready_ontology = get_ontology(base_iri=OWLREADY_ONTOLOGY_IRI).load()
del onto_path[0]



class sameAs(Property):
    ontology = owl