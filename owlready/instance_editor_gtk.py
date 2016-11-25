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

import editobj3, editobj3.undoredo as undoredo, editobj3.introsp as introsp, editobj3.field as field, editobj3.editor as editor, editobj3.editor_gtk as editor_gtk

import gi
from gi.repository import GObject as gobject, Gdk as gdk, Gtk as gtk, GtkSource as gtksource, GdkPixbuf as gdkpixbuf


class GtkOntologyInstanceEditor(OntologyInstanceEditor, editor_gtk.GtkEditorTabbedDialog):
  def check_save(self):
    if self.undo_stack.undoables != self.last_undoables:
      dialog = gtk.MessageDialog(self.window, gtk.DialogFlags.MODAL, gtk.MessageType.WARNING, message_format = editobj3.TRANSLATOR(u"Save modifications before closing?"))
      dialog.add_buttons(
        editobj3.TRANSLATOR(u"Close without saving"), gtk.ResponseType.CLOSE,
        gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
        gtk.STOCK_SAVE, gtk.ResponseType.OK,
        )
      dialog.set_default_response(1)
      response = dialog.run()
      dialog.destroy()
      if   response == gtk.ResponseType.CLOSE : return 0
      if   response == gtk.ResponseType.CANCEL: return 1
      elif response == gtk.ResponseType.OK:
        self.on_save()
        return self.check_save() # The user may have canceled a "save as" dialog box !
        
    else: return 0
    
  def prompt_save_filename(self):
    filter = gtk.FileFilter()
    filter.set_name("OWL/XML")
    filter.add_pattern("*.owl")
    
    dialog = gtk.FileChooserDialog(editobj3.TRANSLATOR(u"Save as..."), self.window, gtk.FileChooserAction.SAVE, (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, gtk.STOCK_SAVE, gtk.ResponseType.OK))
    dialog.set_property("do-overwrite-confirmation", 1)
    dialog.set_default_response(gtk.ResponseType.OK)
    dialog.add_filter(filter)
    dialog.set_current_folder(onto_path[0])
    dialog.set_current_name  (self.ontology.name)
    response = dialog.run()
    filename = dialog.get_filename()
    dialog.destroy()
    if response != gtk.RESPONSE_OK: return
    return filename
  



