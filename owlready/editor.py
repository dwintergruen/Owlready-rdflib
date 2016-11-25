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

from collections import defaultdict

import editobj3, editobj3.introsp as introsp, editobj3.field as field, editobj3.editor as editor

import owlready
from owlready import *
from owlready import _PYTHON_2_DATATYPES

IGNORE_DOMAINLESS_PROPERTY = False

introsp.def_attr("topObjectProperty"  , field.HiddenField)

descr = introsp.description(Ontology)
descr.def_attr("loaded"             , field.HiddenField)
descr.def_attr("name"               , field.HiddenField)
descr.def_attr("base_iri"           , field.StringField)
descr.def_attr("python_module"      , field.StringField)
descr.def_attr("classes"            , add_method = "add", label = "class")
descr.def_attr("imported_ontologies", add_method = "add", label = "imported_ontology")
descr.def_attr("properties"         , add_method = "add", label = "property")
descr.def_attr("instances"          , add_method = "add")
descr.def_attr("all_disjoints"      , add_method = "add")
descr.set_icon_filename(os.path.join(os.path.dirname(__file__), "icons", "owl_instance.svg"))

def _keep_most_generic(s):
  r = set()
  for i in s:
    for parent in i.is_a:
      if parent in s: break
    else: r.add(i)
  return r

def _available_ontologies(o):
  return sorted(o.ontology.indirectly_imported_ontologies(), key = lambda x: x.name)

def _available_classes(o):
  r = set()
  for ontology in o.ontology.indirectly_imported_ontologies():
    r.update(ontology.classes)
  return sorted(_keep_most_generic(r), key = lambda x: str(x))

def _available_properties(o):
  r = set()
  for ontology in o.ontology.indirectly_imported_ontologies():
    r.update(ontology.properties)
  return sorted(_keep_most_generic(r), key = lambda x: str(x))

def _available_properties_and_types(o):
  return [FunctionalProperty, InverseFunctionalProperty, TransitiveProperty, SymmetricProperty, AsymmetricProperty, ReflexiveProperty, IrreflexiveProperty] + _available_properties(o)

def _available_classes_and_datatypes(o):
  r = set()
  for ontology in o.ontology.indirectly_imported_ontologies():
    r.update(ontology.classes)
  r = _keep_most_generic(r)
  r.update(owlready._PYTHON_2_DATATYPES.keys())
  return sorted(r, key = lambda x: str(x))

def _get_label(o):
  return str(o).replace("_", " ")

#descr = introsp.description(EntityClass)
#descr.def_attr("ontology"   , field.HiddenField)

descr = introsp.description_for_type(Thing)
descr.def_attr("ontology"     , field.ObjectSelectorField, addable_values = _available_ontologies)
descr.def_attr("name"         , field.StringField)
descr.def_attr("python_name"  , field.StringField)
descr.def_attr("is_a"         , field.HierarchyAndObjectListField, addable_values = _available_classes)
descr.def_attr("equivalent_to", field.HierarchyAndObjectListField, addable_values = _available_classes)
descr.set_label(_get_label)
descr.set_icon_filename(os.path.join(os.path.dirname(__file__), "icons", "owl_class.svg"))

descr = introsp.description_for_type(Property)
descr.def_attr("ontology"        , field.ObjectSelectorField, addable_values = _available_ontologies)
descr.def_attr("name"            , field.StringField)
descr.def_attr("python_name"     , field.StringField)
descr.def_attr("is_a"            , field.HierarchyAndObjectListField, addable_values = _available_properties_and_types)
descr.def_attr("domain"          , field.HierarchyAndObjectListField, addable_values = _available_classes              , reorder_method = None)
descr.def_attr("range"           , field.HierarchyAndObjectListField, addable_values = _available_classes_and_datatypes, reorder_method = None)
descr.def_attr("inverse_property", field.ObjectSelectorField        , addable_values = lambda o: [None] + _available_properties(o))
descr.def_attr("equivalent_to"   , field.HierarchyAndObjectListField, addable_values = _available_properties_and_types)
descr.set_label(_get_label)
descr.set_icon_filename(os.path.join(os.path.dirname(__file__), "icons", "owl_property.svg"))

descr = introsp.description(Thing)
descr.def_attr("ontology", field.HiddenField)
descr.def_attr("name"    , field.StringField)
descr.def_attr("is_a"    , field.HiddenField)
descr.set_label(_get_label)
descr.set_icon_filename(os.path.join(os.path.dirname(__file__), "icons", "owl_instance.svg"))
descr.set_constructor(introsp.Constructor(lambda Class, parent: Class(ontology = parent.ontology)))

descr = introsp.description(GeneratedName)
descr.def_attr("name", field.HiddenField)


introsp.MAX_NUMBER_OF_ATTRIBUTE_FOR_EMBEDDING = 0

def _get_priority(Prop):
  priority = ANNOTATIONS[Prop]["editobj_priority"]
  if priority: return priority[0]
  else:        return None

def _get_class_one_of(Class):
  if isinstance(Class, OneOfRestriction): return Class.instances
  if isinstance(Class, ThingClass):
    for superclass in Class.is_a + Class.equivalent_to:
      if isinstance(superclass, OneOfRestriction): return superclass.instances
      
def _prop_use_children_group(Prop, domain):
  for superprop in Prop.mro():
    if (superprop is Property) or (superprop in owlready._TYPES): continue
    if isinstance(superprop, PropertyClass) and not superprop.is_functional_for(domain): return 1
  for range in Prop.range:
    if   isinstance(range, ThingClass):
      if _has_object_property(range): return 1
    elif isinstance(range, OrRestriction):
      for or_range in range.Classes:
        if _has_object_property(or_range): return 1
  return 0

def _has_object_property(Class):
  for Prop in Class._get_class_possible_relations():
    if not Prop._is_data_property(): return 1
  return 0

def _is_abstract_class(Class):
  for superclass in Class.is_a + Class.equivalent_to:
    if isinstance(superclass, OrRestriction):
      for or_class in superclass.Classes:
        if not isinstance(or_class, ThingClass): break
      else: return 1

def _simplified_domains(Prop):
  if Prop.domain: yield from _simplified_domains_iteration(Prop.domain)
  else:           yield Thing

def _simplified_domains_iteration(domains):
  for domain in domains:
    if   isinstance(domain, ThingClass): yield domain
    elif isinstance(domain, OrRestriction): yield from _simplified_domains_iteration(domain.Classes)
    
def configure_editobj_from_ontology(onto):
  for Prop in onto.properties:
    ranges = None
    if len(Prop.range) == 1:
      if   isinstance(Prop.range[0], ThingClass):       ranges = [Prop.range[0]]
      elif isinstance(Prop.range[0], OrRestriction) :   ranges =  Prop.range[0].Classes
      elif Prop.range[0] in owlready._PYTHON_2_DATATYPES: ranges = [Prop.range[0]]
    if not ranges: continue
    
    priority = _get_priority(Prop)
    for domain in _simplified_domains(Prop):
      if isinstance(domain, ThingClass):
        if len(ranges) == 1: one_of = _get_class_one_of(ranges[0])
        else:                one_of = None
        if one_of: RangeInstanceOnly(Prop, domain, one_of)
        else:      RangeClassOnly   (Prop, domain, ranges)
        #if one_of: 
        #  if isinstance(domain, ThingClass):
        #    RangeInstanceOnly(Prop, domain, one_of)
        #else:
        #  if isinstance(domain, ThingClass):
        #    RangeClassOnly   (Prop, domain, ranges)
          
  for Class in onto.classes:
    for superclass in Class.is_a:          _configure_class_restriction(Class, superclass)
    for superclass in Class.equivalent_to: _configure_class_restriction(Class, superclass)
    
  #for Prop, group in PROP_CHILDREN_GROUPS.items(): print(group.range_restrictions)
  
  for prop_children_group in PROP_CHILDREN_GROUPS.values():
    if prop_children_group.changed: prop_children_group.define_children_groups()
  
    
def _configure_class_restriction(Class, restriction):
  if   isinstance(restriction, AndRestriction):
    for sub_restriction in restriction.Classes:
      _configure_class_restriction(Class, sub_restriction)
      
  elif isinstance(restriction, OneOfRestriction):pass
    
  elif isinstance(restriction, PropertyValueRestriction):
    if   restriction.type == "VALUE":
      introsp.description(Class).def_attr(restriction.Prop.python_name, field.LabelField, priority = _get_priority(restriction.Prop))
      
    elif restriction.type == "ONLY":
      if not restriction.Prop._is_data_property():
        if   isinstance(restriction.Class, ThingClass): ranges = [restriction.Class]
        else:
          if not hasattr(restriction.Class, "Classes"): return
          ranges =  restriction.Class.Classes
        if len(ranges) == 1: one_of = _get_class_one_of(ranges[0])
        else:                one_of = None
        if one_of: RangeInstanceOnly(restriction.Prop, Class, one_of)
        else:      RangeClassOnly   (restriction.Prop, Class, ranges)
        
    elif (restriction.type == "EXACTLY") or (restriction.type == "MAX"):
      # These restrictions can make the Property functional for the given Class
      # => Force the redefinition of the field type by creating an empty range restriction list
      for subprop in restriction.Prop.descendant_subclasses():
        prop_children_group = get_prop_children_group(subprop)
        prop_children_group.range_restrictions[Class] # Create the list if not already existent
        prop_children_group.changed = 1
        
      
  elif isinstance(restriction, NotRestriction):
    if isinstance(restriction.Class, Restriction):
      _configure_class_negative_restriction(Class, restriction.Class)
      
def _configure_class_negative_restriction(Class, restriction):
  if   isinstance(restriction, OrRestriction):
    for sub_restriction in restriction.Classes:
      _configure_class_negative_restriction(Class, sub_restriction)
      
  elif isinstance(restriction, PropertyValueRestriction):
    if restriction.type == "SOME":
      if not restriction.Prop._is_data_property():
        if isinstance(restriction.Class, ThingClass): ranges = [restriction.Class]
        else:                                         ranges =  restriction.Class.Classes
        if len(ranges) == 1: one_of = _get_class_one_of(ranges[0])
        else:                one_of = None
        if one_of: RangeInstanceExclusion(restriction.Prop, Class, one_of)
        else:      RangeClassExclusion   (restriction.Prop, Class, ranges)
          

PROP_CHILDREN_GROUPS = {}
def get_prop_children_group(Prop): return PROP_CHILDREN_GROUPS.get(Prop) or PropChildrenGroup(Prop)


class PropChildrenGroup(object):
  def __init__(self, Prop):
    self.Prop = Prop
    self.range_restrictions = defaultdict(list)
    self.changed = 0
    PROP_CHILDREN_GROUPS[Prop] = self
    
    
  def define_children_groups(self):
    self.changed = 0
    
    priority = _get_priority(self.Prop)
    
    for domain in set(self.range_restrictions):
      descr      = introsp.description(domain)
      functional = self.Prop.is_functional_for(domain)
      range_restrictions = set()
      for superclass in domain.mro():
        s = self.range_restrictions.get(superclass)
        if s: range_restrictions.update(s)
        
      range_instance_onlys = { range_restriction for range_restriction in range_restrictions if isinstance(range_restriction, RangeInstanceOnly) }
      if range_instance_onlys:
        instances = None
        for range_restriction in range_instance_onlys:
          if instances is None: instances = set(range_restriction.ranges)
          else:                 instances.intersection_update(set(range_restriction.ranges))
          
        d = { instance.name : instance for instance in instances }
        if functional:
          d["None"] = None
          descr.def_attr(self.Prop.python_name, field.EnumField(d), priority = priority)
        else:
          descr.def_attr(self.Prop.python_name, field.EnumListField(d), priority = priority)
          
      else:
        datatype = None
        for range_restriction in range_restrictions:
          if isinstance(range_restriction, RangeClassOnly):
            for range in range_restriction.ranges:
              if range in _PYTHON_2_DATATYPES:
                datatype = range
                break
                
        if datatype:
          if   datatype == int:
            if functional: descr.def_attr(self.Prop.python_name, field.IntField       , priority = priority)
            else:          descr.def_attr(self.Prop.python_name, field.IntListField   , priority = priority)
          elif datatype == float:
            if functional: descr.def_attr(self.Prop.python_name, field.FloatField     , priority = priority)
            else:          descr.def_attr(self.Prop.python_name, field.FloatListField , priority = priority)
          elif datatype == normstr:
            if functional: descr.def_attr(self.Prop.python_name, field.StringField    , priority = priority)
            else:          descr.def_attr(self.Prop.python_name, field.StringListField, priority = priority)
          elif datatype == str:
            if functional: descr.def_attr(self.Prop.python_name, field.TextField      , priority = priority)
            else:          descr.def_attr(self.Prop.python_name, field.StringListField, priority = priority)
          elif datatype == bool:
            if functional: descr.def_attr(self.Prop.python_name, field.BoolField      , priority = priority)
          else:
            if functional: descr.def_attr(self.Prop.python_name, field.EntryField     , priority = priority)
            else:          descr.def_attr(self.Prop.python_name, field.EntryListField , priority = priority)
            
        else:
          values_lister = ValuesLister(self.Prop, domain, range_restrictions)
          if _prop_use_children_group(self.Prop, domain) or values_lister.values_have_children():
            if self.Prop.inverse_property: inverse_attr = self.Prop.inverse_property.python_name
            else:                          inverse_attr = ""
            if functional: field_class = field.HierarchyOrObjectSelectorField
            else:          field_class = field.HierarchyOrObjectListField
            descr.def_attr(self.Prop.python_name,
                           field_class,
                           addable_values = values_lister.available_values,
                           inverse_attr = inverse_attr,
                           priority = priority)
          else:
            descr.def_attr(self.Prop.python_name,
                           field.ObjectSelectorField, addable_values = values_lister.available_values,
                           priority = priority)
          
class RangeRestriction(object):
  def __init__(self, Prop, domain, ranges):
    self.domain = domain
    self.ranges = ranges
    
    for subprop in Prop.descendant_subclasses():
      prop_children_group = get_prop_children_group(subprop)
      prop_children_group.range_restrictions[domain].append(self)
      prop_children_group.changed = 1
      
  def __repr__(self): return "<%s %s %s>" % (self.__class__.__name__, self.domain, self.ranges)
  
  def get_classes(self):
    available_classes = set()
    for range in self.ranges:
      for subrange in range.descendant_subclasses(): available_classes.add(subrange)
    return available_classes
  
class RangeClassOnly(RangeRestriction): pass

class RangeClassExclusion(RangeRestriction): pass

class RangeInstanceOnly(RangeRestriction): pass

class RangeInstanceExclusion(RangeRestriction): pass

VALUES_LISTERS = {}

class ValuesLister(object):
  def __init__(self, Prop, domain, range_restrictions):
    self.Prop               = Prop
    self.domain             = domain
    self.range_restrictions = range_restrictions
    VALUES_LISTERS[Prop, domain] = self
    
  def values_have_children(self):
    for range_restriction in self.range_restrictions:
      if isinstance(range_restriction, RangeClassOnly):
        for range in range_restriction.ranges:
          for subrange in range.descendant_subclasses():
            #if introsp.description(subrange).children_getters: return 1
            for attribute in introsp.description(subrange).attributes.values():
              #if _is_field_subclass(attribute.field_class, FieldInHierarchyPane): return 1
              #if is_displayed_in_hierarchy_pane(self.Prop, ): return 1
              try:    return issubclass(attribute.field_class, FieldInHierarchyPane)
              except: return False # attribute.field_class if a func and not a class

  def available_values(self, subject):
    available_classes = None
    excluded_classes  = set()
    for range_restriction in self.range_restrictions:
      if   isinstance(range_restriction, RangeClassOnly):
        range_restriction_available_classes = range_restriction.get_classes()
        if available_classes is None: available_classes = range_restriction_available_classes
        else: available_classes &= range_restriction_available_classes
      elif isinstance(range_restriction, RangeClassExclusion):
        excluded_classes.update(range_restriction.get_classes())
        
    if not available_classes: available_classes = set()
    available_classes.difference_update(excluded_classes)
    available_classes = sorted(available_classes, key = lambda Class: Class.name)
    new_instances_of = [introsp.NewInstanceOf(Class) for Class in available_classes if (not _get_class_one_of(Class)) and (not _is_abstract_class(Class))]
    #new_instances_of = [introsp.NewInstanceOf(Class, lambda subject, Class = Class: Class(ontology = subject.ontology)) for Class in available_classes if (not _get_class_one_of(Class)) and (not _is_abstract_class(Class))]
    existent_values = set()
    for Class in available_classes:
      existent_values.update(Class._direct_instances)
    if excluded_classes:
      excluded_classes = tuple(excluded_classes)
      existent_values = [o for o in existent_values if not isinstance(o, excluded_classes)]
      
    # For InverseFounctional props, remove values already used.
    if issubclass(self.Prop, InverseFunctionalProperty) and self.Prop.inverse_property:
      existent_values = { value for value in existent_values if not getattr(value, self.Prop.inverse_property.python_name) }
      
    existent_values = sorted(existent_values, key = lambda obj: obj.name)
      
    return new_instances_of + existent_values

  def range_match_classes(self, classes):
    classes = tuple(classes)
    for range_restriction in self.range_restrictions:
      if isinstance(range_restriction, RangeClassOnly):
        for range in range_restriction.ranges:
          if issubclass(range, classes): return True
          
