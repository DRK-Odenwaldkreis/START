#!python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright Philipp Scior philipp.scior@drk-forum.de

import sys
import os
import Tkinter


umlaute=['odiaeresis', 'adiaeresis', 'udiaeresis', 'Odiaeresis', 'Adiaeresis', 'Udiaeresis', 'ssharp']

class Autocomplete(Tkinter.Entry):
	"""
	Subclass of Tkinter.Entry that features autocompletion.
	
	To enable autocompletion use set_verv_liste(list) to define 
        a list of possible strings to hit.
	To cycle through treffer use down and up arrow keys.
	"""

	def set_verv_liste(self, verv_liste):
		self._verv_liste = verv_liste
		self._treffer = []
		self._index = 0
		self.position = 0
		self.bind('<KeyRelease>', self.handle_keyrelease)		

	def autocomplete(self, delta=0):
		"""autocomplete the Entry, delta may be 0/1/-1 to cycle through possible treffer"""
		if delta: # need to delete selection otherwise we would fix the current position
			self.delete(self.position, Tkinter.END)
		else: # set position to end so selection starts where textentry ended
			self.position = len(self.get())
		# collect treffer
		_treffer = []
		for element in self._verv_liste:
			if element.startswith(self.get()):
				_treffer.append(element)
		# if we have a new hit list, keep this in mind
		if _treffer != self._treffer:
			self._index = 0
			self._treffer=_treffer
		# only allow cycling if we are in a known hit list
		if _treffer == self._treffer and self._treffer:
			self._index = (self._index + delta) % len(self._treffer)
		# now finally perform the auto completion
		if self._treffer:
			self.delete(0,Tkinter.END)
			self.insert(0,self._treffer[self._index])
			self.select_range(self.position,Tkinter.END)
			
	def handle_keyrelease(self, event):
		"""event handler for the keyrelease event on this widget"""
		if event.keysym == "BackSpace":
			self.delete(self.index(Tkinter.INSERT), Tkinter.END) 
			self.position = self.index(Tkinter.END)
		if event.keysym == "Left":
			if self.position < self.index(Tkinter.END): # delete the selection
				self.delete(self.position, Tkinter.END)
			else:
				self.position = self.position-1 # delete one character
				self.delete(self.position, Tkinter.END)
		if event.keysym == "Right":
			self.position = self.index(Tkinter.END) # go to end (no selection)
		if event.keysym == "Down":
			self.autocomplete(1) # cycle to next hit
		if event.keysym == "Up":
			self.autocomplete(-1) # cycle to previous hit
		# perform normal autocomplete if event is a single key or an umlaut
		if len(event.keysym) == 1 or event.keysym in umlaute:
			self.autocomplete()

