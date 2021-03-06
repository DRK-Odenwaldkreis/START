#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup script to generate a portable Windows version from
#the Python program

# usage: 
# 1) run python setup.py py2exe in PowerShell/CMD
# 2) copy the folders "ELW_Frontend" and "ELW_Backend" in the
# "dist" folder created by step 1)
# 3) now execute main.exe 

from distutils.core import setup
import py2exe

setup(windows=[
		{"script":"main.pyw",
 		 "icon_resources": [(0,"ELW_Frontend/images/Logo.ico")]
		}
	]
)
