#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Database v 1.0

#Copyright Philipp Scior philipp.scior@drk-forum.de

#contains the SQLite databases where the history and the current
#staging area are stored. contains all the python wrapper methods
#to access the databases.


import sqlite3
import time

from pdf import PDFgenerator

#import datetime

class Database_error(Exception):
    pass


class Database:

# Constructor
    def __init__(self,new):

        self.connection = sqlite3.connect("ELW_Backend/bereitstellungsraum.db")
        self.connection.text_factory=str


        self.cursor = self.connection.cursor()

        if new == 1:
            self.cursor.execute("DROP TABLE bereitstellung")
            self.cursor.execute("DROP TABLE name")
        

        self.sql_make_name= """
        CREATE TABLE IF NOT EXISTS name (
        name VARCHAR(50) PRIMARY KEY
        );
        """
        

        self.sql_make_br= """
        CREATE TABLE IF NOT EXISTS bereitstellung (
        id INTEGER PRIMARY KEY, 
        f_name VARCHAR(50) UNIQUE,
        organisation VARCHAR(20),
        f_typ VARCHAR(20),
        zf INT,
        gf INT,
        helfer INT,
        fuehrung BOOLEAN,
        ankunft TIMESTAMP,
        bemerkung VARCHAR(200),
        sonderbeladung VARCHAR(200),
        notarzt INT,
        arzt INT,
        notsan INT,
        rs INT,
        liegend INT,
        tragestuhl INT,
        sitzend INT,
        atemschutz INT,
        csa INT,
        sanitaeter INT,
        loeschwasser INT,
        schaummittel INT,
        tel VARCHAR(20),
        fax VARCHAR(20),
        email VARCHAR(50),
        mrt INT,
        hrt INT,
        auftrag BOOLEAN
        );
        """
        
        self.sql_make_history = """
        CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY, 
        f_name VARCHAR(50),
        organisation VARCHAR(20),
        f_typ VARCHAR(20),
        zf INT,
        gf INT,
        helfer INT,
        fuehrung BOOLEAN,
        ankunft TIMESTAMP,
        abfahrt TIMESTAMP,
        ziel VARCHAR(100),
        bemerkung VARCHAR(200)
        );        
        """

        self.sql_make_double_tr = """
        CREATE TRIGGER IF NOT EXISTS double
        AFTER INSERT ON bereitstellung
        BEGIN
        SELECT "FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im BR vorhanden!"
        WHERE
        f_name=NEW.f_name;
        END;
        """

        self.cursor.execute(self.sql_make_br)
        self.cursor.execute(self.sql_make_history)
        self.cursor.execute(self.sql_make_name)
        #self.cursor.execute(self.sql_make_double_tr)



        self.connection.commit()

        try:
            self.br_name=self.name_querry()[0]
        except TypeError as e:
            self.br_name=""
  
        


        #print(self.br_name)


#wrapper to add a database entry, expects tupel with 27 entries as input        

    def add(self, tupel):
        
        try:
            self.cursor.execute("INSERT INTO bereitstellung VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 0)", tupel)
        except sqlite3.IntegrityError as e:
            raise Database_error("FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im BR vorhanden \n Kontaktieren Sie die EAL!")   
        self.connection.commit()

#wrapper to read the complete history of the staging area
    def read_history(self):
        self.cursor.execute("SELECT * FROM history")
        print("History:")
        self.result=self.cursor.fetchall()
        #for r in self.result:
        #    print(r)
        return self.result


#wrapper to remove an entry from the database, expects a tupel with 4 entries as input
    def remove(self,tupel2):
        name=(tupel2[0],)
        rest=(tupel2[1], tupel2[2], tupel2[3], tupel2[0])
        self.cursor.execute("INSERT INTO history(id,f_name, organisation, f_typ, zf, gf, helfer, fuehrung, ankunft, abfahrt, ziel, bemerkung) SELECT NULL, f_name, organisation, f_typ, zf, gf, helfer, fuehrung, ankunft, ?, ?, ? FROM bereitstellung WHERE f_name=?", rest)
        self.cursor.execute("DELETE FROM bereitstellung WHERE f_name=?", name)
        self.connection.commit()


#wrapper to read all current entries in the database, if start=True: sets assignment for all units to 0 <- true only at upstart
    def read_current(self, start):
        #print("in read current")
        print(start)
        if start==True:
            #print("in if case")

            self.cursor.execute("SELECT count(*) FROM bereitstellung")
            exists=self.cursor.fetchone()[0]
            #print(exists)
            #self.cursor.rollback()
            if not (exists == 0):
                #print("before try")
                try:
                    #print("before shizzle")
                    self.cursor.execute("UPDATE bereitstellung SET auftrag=?", (0,))
                    #print("shizzle")
                    self.cursor.commit()                
                except Exception as e:
                    pass
            self.cursor.execute("SELECT * FROM bereitstellung")
            print("after start thingy")
        else:
            self.cursor.execute("SELECT * FROM bereitstellung WHERE auftrag=0")
            print("Derzeit Vorhandene Fahrzeuge in Bereitstellung:")

            
        self.result=self.cursor.fetchall()
        return self.result
        #for r in self.result:
           # print(r)

#wrapper to update one entry in the database, expects a tupel with 27 entries and one tupel with one entry as input
    def update(self, tupel, name):
        tupell=tupel+name
        print(tupell)
        try:
            self.cursor.execute("UPDATE bereitstellung SET f_name=?, organisation=?, f_typ=?, zf=?, gf=?, helfer=?, fuehrung=?, ankunft=?, bemerkung=?, sonderbeladung=?, notarzt=?, arzt=?, notsan=?, rs=?, liegend=?, sitzend=?, tragestuhl=?, atemschutz=?, csa=?, sanitaeter=?, loeschwasser=?, schaummittel=?, tel=?, fax=?, email=?, mrt=?, hrt=?, auftrag=0 WHERE f_name=?",(tupell))
        except sqlite3.IntegrityError as e:
            raise Database_error("FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im BR vorhanden \n Kontaktieren Sie die EAL!")
        self.connection.commit()

#wrapper set the set "auftrag" to true, showing that the unit has a assignment, espects only the callsign as input
    def set_assignment(self, name):
        tupel=(name,)
        try:
            self.cursor.execute("UPDATE bereitstellung SET auftrag=1 WHERE f_name=?", tupel)
        except Exception as e:
            raise Database_error("FEHLER: Fahrzeug nicht vorhanden?")
        self.connection.commit()

#wrapper make a querry for one single entry in the database, expects a tupel with one entry (callsign) as input
    def single(self, tupel):
        self.cursor.execute("SELECT * FROM bereitstellung WHERE f_name=?", tupel)
        self.result=self.cursor.fetchone()
        return self.result


#wrapper to get the number of all current personal in the staging area
    def get_persons(self):
        
        self.cursor.execute("SELECT SUM(zf) FROM bereitstellung")
        zf=self.cursor.fetchone()

        self.cursor.execute("SELECT SUM(gf) FROM bereitstellung")
        gf=self.cursor.fetchone()

        self.cursor.execute("SELECT SUM(helfer) FROM bereitstellung")
        helfer=self.cursor.fetchone()

        try:
            persons=zf[0]+gf[0]+helfer[0]
        except TypeError as e:
            persons=0
        return int(persons)

# wrapper for the agt querry
    def get_agt(self):
        self.cursor.execute("SELECT SUM(atemschutz) FROM bereitstellung")

        try:
            return int(self.cursor.fetchone()[0])
        except TypeError as e:
            return 0


        

#method to print the current content of the staging area to .csv file
    def print_to_file(self):
        #name=time.strftime("%Y-%b-%d-%H-%M", time.localtime())
        name=time.strftime("%d%H%M%b%Y", time.localtime())
        name=name+self.br_name+".csv"
        content=self.read_current(False)


        cont_sort=sorted(content, key= lambda eintrag: eintrag[1])
        final_sort=sorted(cont_sort, key= lambda eintrag: eintrag[2])

 
        with open(name, "w") as file:
            file.write("Rufname\t Organisation\t Typ\t Besatzung\n")
            for x in content:
                file.write("{}\t{}\t{}\t{}/{}/{}\n".format(x[1],x[2],x[3],x[4],x[5],x[6]))
        with open("sorted.csv", "w") as file2:
            file2.write("Rufname\t Organisation\t Typ\t Besatzung\n")
            for x in final_sort:
                file2.write("{}\t{}\t{}\t{}/{}/{}\n".format(x[1],x[2],x[3],x[4],x[5],x[6]))

        pdf_out=PDFgenerator(final_sort, self.br_name, time.strftime("%d%H%M%b%Y", time.localtime()))
        pdf_out.generate()


#method to print the complete history of the staging area to .csv file
    def print_history(self):
        name="Bereitstellungsraum_historie.csv"
        content=self.read_history();

        print(content)
        with open(name, "w") as file:
            file.write("Rufname\t Organisation\t Typ\t Fuehrung\t Ankunft\t Abfahrt\t Ziel\t Bemerkung\t Besatzung\n")
            for x in content:
                file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}/{}/{}\n".format(x[1],x[2],x[3],x[7],x[8],x[9],x[10],x[11],x[4],x[5],x[6]))


#python wrapper for name querry:
    def name_querry(self):
        self.cursor.execute("SELECT name FROM name")
        return self.cursor.fetchone()

#python wrapper to set the name
    def set_name(self,the_name):
        self.cursor.execute("INSERT INTO name VALUES(?)", (the_name,))
        self.connection.commit()


#python wrapper for the type querry:
    def type_querry(self):
        print("inside the type_querry")
        self.cursor.execute("SELECT f_typ FROM bereitstellung")
        return self.cursor.fetchall()

#python warpper for count querry:
    def count(self):
        self.cursor.execute("SELECT count(*) FROM bereitstellung")
        return self.cursor.fetchone()[0]