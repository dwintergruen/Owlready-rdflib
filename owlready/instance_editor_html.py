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

import owlready, owlready.editor
from owlready import *
from owlready.instance_editor import *

import editobj3, editobj3.undoredo as undoredo, editobj3.introsp as introsp, editobj3.field as field, editobj3.editor as editor, editobj3.editor_html as editor_html

  
class HTMLOntologyInstanceEditor(OntologyInstanceEditor, editor_html.HTMLEditorTabbedDialog):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    self.add_to_menu(self.file_menu, 0, u"Save"      , self.on_save, accel = u"C-S", pos = 0)    
    
  



