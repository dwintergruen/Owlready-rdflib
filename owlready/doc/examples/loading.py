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


# This short example shows how to load an OWL ontology from an OWL/XML file
# and to run the reasoner.

import sys, os

from owlready import *

onto_path.append(os.path.dirname(__file__))

onto_test = Ontology("http://test.org/onto_test.owl")
onto_test.load()

onto_test.sync_reasoner(debug = 1)
