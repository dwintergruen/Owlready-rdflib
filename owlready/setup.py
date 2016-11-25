#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Owlready
# Copyright (C) 2013-2014 Jean-Baptiste LAMY

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


import os, os.path, sys, glob

HERE = os.path.dirname(sys.argv[0]) or "."

if len(sys.argv) <= 1: sys.argv.append("install")


import distutils.core, distutils.sysconfig
if ("upload_docs" in sys.argv) or ("build_sphinx" in sys.argv): import setuptools


distutils.core.setup(
  name         = "Owlready",
  version      = "0.3",
  license      = "LGPLv3+",
  description  = "A module for ontology-oriented programming in Python: load OWL 2.0 ontologies as Python objects, modify them, save to OWL XML, and perform reasoning via HermiT. It can also generate dialog boxes for editing instances.",
  long_description = open(os.path.join(HERE, "README.rst")).read(),
  
  author       = "Lamy Jean-Baptiste (Jiba)",
  author_email = "jibalamy@free.fr",
  url          = "https://bitbucket.org/jibalamy/owlready",
  classifiers  = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: User Interfaces",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
  
  package_dir  = {"owlready" : "."},
  packages     = ["owlready"],
  package_data = {"owlready" : ["owlready_ontology.owl", "hermit/*.*", "hermit/org/semanticweb/HermiT/cli/*", "icons/*", "locale/fr/LC_MESSAGES/*", "locale/en/LC_MESSAGES/*"]}
  )
