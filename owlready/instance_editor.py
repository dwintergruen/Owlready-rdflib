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

__all__ = ["EditedInstances", "OntologyInstanceEditor"]
import locale

import owlready, owlready.editor
from owlready import *
from owlready.editor import _get_class_one_of, _is_abstract_class, VALUES_LISTERS

import editobj3, editobj3.undoredo as undoredo, editobj3.introsp as introsp, editobj3.field as field, editobj3.editor as editor
from editobj3.observe import *


class EditedInstances(object):
  def __init__(self, ontology, Class):
    self.ontology  = ontology
    self.Class     = Class
    self.name      = editobj3.TRANSLATOR(Class.name.replace("_", " "))
    #self.compute_instances()
    #for Class in self.class_and_descendant_classes():
    #  observe(Class._direct_instances, self._listener)
    
  #def _listener(self, o, type, new, old):
  #  self.compute_instances()
  #  
  #def compute_instances(self):
  #  self.instances = sorted(self.Class.instances(), key = lambda instance: locale.strxfrm(instance.name))
    
  def get_instances(self):
    #return sorted(self.Class.instances(), key = lambda instance: locale.strxfrm(instance.name))
    return sorted((instance for instance in self.ontology.instances if isinstance(instance, self.Class)), key = lambda instance: locale.strxfrm(instance.name))
  instances = property(get_instances)
  
  def remove_instance(self, instance):
    self.ontology.instances.remove(instance)
    
  def __str__(self): return self.name
  
  def details(self): return "%s (%s)" % (self.name, len(self.instances))
  
  def class_and_descendant_classes(self):
    return list(set(self.Class.descendant_subclasses()))
  
  def addable_values(self):
#    return [introsp.Constructor(Class, lambda subject, Class = Class: Class(ontology = subject.ontology))
#            for Class in self.class_and_descendant_classes()
#            if (not _get_class_one_of(Class)) and (not _is_abstract_class(Class))]
    return [introsp.NewInstanceOf(Class)
            for Class in self.class_and_descendant_classes()
            if (not _get_class_one_of(Class)) and (not _is_abstract_class(Class))]
  
descr = introsp.description(EditedInstances)
descr.set_details(EditedInstances.details)
descr.def_attr("instances", label = "", reorder_method = None, addable_values = "addable_values")
descr.def_attr("ontology" , field.HiddenField)
descr.def_attr("Class"    , field.HiddenField)
descr.def_attr("name"     , field.HiddenField)

class TabPaneRepartitor(editor.PaneRepartitor):
  def __init__(self, instance_editor, tab_edited_class):
    self.instance_editor  = instance_editor
    self.tab_edited_class = tab_edited_class
    self._cache           = {}
    
  def is_displayed_in_other_tab(self, attribute, o_Class):
    Prop = PROPS.get(attribute.name)
    if Prop: 
      for Class in o_Class.mro():
        values_lister = VALUES_LISTERS.get((Prop, Class))
        if values_lister:
          other_tab_classes = list(self.instance_editor.edited_classes)
          other_tab_classes.remove(self.tab_edited_class)
          #if attribute.name == "population": print("=> ", values_lister.range_match_classes(other_tab_classes))
          return values_lister.range_match_classes(other_tab_classes)
    #if attribute.name == "population": print("=> False (pas trouvé)")
    return False
  
  def _compute(self, o, attribute, field_class = None):
    o_Class = o.__class__
    if field_class is None: field_class = attribute.field_class_for(o)
    
    displayed_in_another_tab = False
    Prop = PROPS.get(attribute.name)
    if Prop:
      if isinstance(o, type): mro = o.mro()
      else:                   mro = o_Class.mro()
      for Class in mro:
        values_lister = VALUES_LISTERS.get((Prop, Class))
        if values_lister:
          other_tab_classes = list(self.instance_editor.edited_classes)
          other_tab_classes.remove(self.tab_edited_class)
          #if attribute.name == "population": print("=> ", values_lister.range_match_classes(other_tab_classes))
          displayed_in_another_tab = values_lister.range_match_classes(other_tab_classes)
          break
          
    displayed_in_hierarchy_pane = field_class.display_in_hierarchy_pane and not(displayed_in_another_tab)
    displayed_in_attribute_pane = field_class.display_in_attribute_pane or      displayed_in_another_tab
    self._cache[o_Class, attribute.name] = displayed_in_hierarchy_pane, displayed_in_attribute_pane
    
  def is_displayed_in_hierarchy_pane(self, attribute, o, field_class = None):
    if not (o.__class__, attribute.name) in self._cache: self._compute(o, attribute, field_class)
    return self._cache[o.__class__, attribute.name][0]
    
  def is_displayed_in_attribute_pane(self, attribute, o, field_class = None):
    if not (o.__class__, attribute.name) in self._cache: self._compute(o, attribute, field_class)
    return self._cache[o.__class__, attribute.name][1]


  
class OntologyInstanceEditor(editor.EditorTabbedDialog):
  _Qt_MODULE     = "owlready.instance_editor_qt"
  _Gtk_MODULE    = "owlready.instance_editor_gtk"
  _HTML_MODULE   = "owlready.instance_editor_html"
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    self.set_default_size(1024, 752)
    self.add_to_menu(self.file_menu, 0, u"Save"      , self.on_save, accel = u"C-S", pos = 0)
    self.add_to_menu(self.file_menu, 0, u"Save as...", self.on_save_as, accel = u"C-S-S", pos = 1)
    self.add_separator_to_menu(self.file_menu, pos = 2)
    
    self.ontology          = None
    self.edited_classes    = []
    self.last_undoables    = []
    self.edited_instancess = {}
    
  def on_dialog_closed(self, *args):
    super().on_dialog_closed(*args)
    if not self.check_save(): return True
    return False
    
  def set_ontology(self, ontology, edited_classes = None):
    if not edited_classes: edited_classes = [Class for Class in ontology.classes if not [parent for parent in Class.is_a if parent.ontology is ontology]]
    self.ontology          = ontology
    self.edited_classes    = []
    self.last_undoables    = []
    self.edited_instancess = {}
    # edit() must be called AFTER setting the pane repartitor, thus cannot be done by add_tab(),
    # and AFTER creating all tabs (since the pane repartitor needs the entire list of tabs)
    for edited_class in edited_classes: self.add_tab_for_class(edited_class)
    for edited_class in edited_classes: self.editor_panes[edited_class].edit(self.edited_instancess[edited_class])
    scan()
    
  def add_tab_for_class(self, Class):
    self.edited_classes.append(Class)
    edited_instance = self.edited_instancess[Class] = EditedInstances(self.ontology, Class)
    editor_pane = self.add_tab(Class, str(edited_instance))
    editor_pane.set_pane_repartitor(TabPaneRepartitor(self, Class))
    return editor_pane
    
  # def set_field_class_for_class(self, Class, hierarchy):
  #   for ontology in self.ontology.indirectly_imported_ontologies():
  #     for Prop in ontology.properties:
  #       for range in Prop.range:
  #         if isinstance(range, ThingClass) and issubclass(range, Class):
  #           if hierarchy:
  #             if issubclass(Prop, FunctionalProperty): field_class = field.HierarchyOrObjectSelectorField
  #             else:                                    field_class = field.HierarchyOrObjectListField
  #           else:
  #             if issubclass(Prop, FunctionalProperty): field_class = field.ObjectSelectorField
  #             else:                                    field_class = field.ObjectListField
  #           for descr in introsp._CLASS_DESCRS.values(): # Hack, optimizable
  #             if hasattr(descr, "attributes") and Prop.python_name in descr.attributes:
  #               attribute = descr.attributes[Prop.python_name]
  #               if not attribute.field_class is field.HiddenField: # Else, the attribute has been hidden by a manual call to def_attr()
  #                 attribute.field_class = field_class
  #           break
    
  def on_save(self, *args):
    self.ontology.save()
    self.last_undoables = self.undo_stack.undoables[:]
    
  def on_save_as(self, *args):
    filename = self.prompt_save_filename()
    if not filename: return
    dirname, filename = os.path.split(filename)
    self.ontology.name = filename
    if onto_path[0] != dirname: onto_path.insert(0, dirname)
    self.on_save()

    



