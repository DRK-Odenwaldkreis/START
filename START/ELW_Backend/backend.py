#!/usr/bin/env python

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Middelware v 1.0

#Copyright Philipp Scior philipp.scior@drk-forum.de

#contains the middelware class that manages the webserver and comunications beteween
# webserver and the gui
# the webserver also creates an html page that can be used to add units via a webbrowser
# this is mainly for debugging

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
from ELW_Frontend.gui import GUI
import datetime
import Queue


html = """
<html>
<!DOCTYPE html>
<html lang="de"> 
<head>
<meta charset="utf-8"/>

<body>
   <form method="post" action="">
        <p>
            <b>Browser-Testimplementierung des Staging.py Clients </b>
        </p>
        <p>
          Funkrufname: <input type="text" name="f_name" value="%(funkrufname)s"> 
        </p>
        <p>
          Organisation: <input type="text" name="orga" value="%(organisation)s"> 
        </p>
        <p>
          Fahrzeugtyp: <input type="text" name="typ" value="%(fahrzeugtyp)s"> 
        </p>
        <p>
          Besatzung: <input type="text" name="zf" value="%(zf)s">  <input type="text" name="gf" value="%(gf)s"> <input type="text" name="helfer" value="%(helfer)s">
        </p>
        <p>
          Bemerkungen: <input type="text" name="bemerkung" value="%(bemerkung)s"> 
        </p>
        <p>
          Sonderbeladung: <input type"text" name="sonderbeladung" value="%(sonderbeladung)s">
        </p>
        <p>
          Notarzt: <input type"text" name="notarzt" value="%(notarzt)s">
        </p>
        <p>
          Arzt: <input type"text" name="arzt" value="%(arzt)s">
        </p>
        <p>
          NotSan / RettAss: <input type"text" name="notsan" value="%(notsan)s">
        </p>
        <p>
          RS: <input type"text" name="rs" value="%(rs)s">
        </p>
        <p>
          liegend: <input type"text" name="liegend" value="%(liegend)s">
        </p>
        <p>
          Tragestuhl: <input type"text" name="tragestuhl" value="%(tragestuhl)s">
        </p>
        <p>
          sitzend: <input type"text" name="sitzend" value="%(sitzend)s">
        </p>
        <p>
          Atemschutz: <input type"text" name="atemschutz" value="%(atemschutz)s">
        </p>
        <p>
          CSA: <input type"text" name="csa" value="%(csa)s">
        </p>
        <p>
          Sanitäter: <input type"text" name="sanitaeter" value="%(sanitaeter)s">
        </p>
        <p>
          Löschwasser: <input type"text" name="loeschwasser" value="%(loeschwasser)s">
        </p>
        <p>
          Schaummittel: <input type"text" name="schaummittel" value="%(schaummittel)s">
        </p>
        <p>
          Telefon: <input type"text" name="telefon" value="%(telefon)s">
        </p>
        <p>
          Fax: <input type"text" name="fax" value="%(fax)s">
        </p>
        <p>
          Email: <input type"text" name="email" value="%(email)s">
        </p>
        <p>
          ISSI MRT: <input type"text" name="mrt" value="%(mrt)s">
        </p>
        <p>
          ISSI HRT: <input type"text" name="hrt" value="%(hrt)s">
        </p>
        <p>
            Führung:
            <input
                name="führung" type="checkbox" value="führung"
                %(checked-führung)s
            > Führung
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>
    <p>
        <b>Status der Übertragung:</b> %(error_code)s<br>
        <br>
        Funkrufname: %(funkrufname)s<br>
        Organisation: %(organisation)s<br>
        Fahrzeugtyp: %(fahrzeugtyp)s<br>
        Besatzung: %(zf)s / %(gf)s / %(helfer)s <br>
        Bemerkungen: %(bemerkung)s<br>
        Sonderbeladung: %(sonderbeladung)s<br>
        Notarzt: %(notarzt)s<br>
        Arzt: %(arzt)s<br>
        NotSan / RettAss: %(notsan)s<br>
        RS: %(rs)s<br>
        liegend: %(liegend)s<br>
        Tragestuhl: %(tragestuhl)s<br>
        sitzend: %(sitzend)s<br>
        Atemschutz: %(atemschutz)s<br>
        CSA: %(csa)s<br>
        Sanitäter: %(sanitaeter)s<br>
        Löschwasser: %(loeschwasser)s<br>
        Schaummittel: %(schaummittel)s<br>
        Führung: %(führung)s<br>
        Telefon: %(telefon)s<br>
        Fax: %(fax)s<br>
        Email: %(email)s<br>
        ISSI MRT: %(mrt)s<br>
        ISSI HRT: %(hrt)s<br>
    </p>
</body>
</html>
"""
#class needs the gui instance as input
class Middleware():

    def __init__(self, gui, queue, r_queue):
        self.gui = gui
        self.queue = queue
        self.r_queue = r_queue
        self.status=False

    def run(self, environ, start_response):
    
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
        request_body = environ['wsgi.input'].read(request_body_size)
        d = parse_qs(request_body)
        err=''
        funkrufname = d.get('f_name', [''])[0] # Returns the funkrufname value.
        organisation= d.get('orga', [''])[0]
        fuehrung = d.get('führung', []) # Returns a list.
        fahrzeugtyp = d.get('typ', [''])[0]
        zf = d.get('zf', [''])[0]
        gf = d.get('gf', [''])[0]
        helfer = d.get('helfer', [''])[0]
        bemerkung = d.get('bemerkung', [''])[0]
        sonderbeladung =d.get('sonderbeladung',[''])[0]
        notarzt =d.get('notarzt',[''])[0]
        arzt =d.get('arzt',[''])[0]
        notsan =d.get('notsan',[''])[0]
        rs =d.get('rs',[''])[0]
        liegend =d.get('liegend',[''])[0]
        tragestuhl =d.get('tragestuhl',[''])[0]
        sitzend =d.get('sitzend',[''])[0]
        atemschutz =d.get('atemschutz',[''])[0]
        csa =d.get('csa',[''])[0]
        sanitaeter =d.get('sanitaeter',[''])[0]
        loeschwasser =d.get('loeschwasser',[''])[0]
        schaummittel =d.get('schaummittel',[''])[0]
        telefon=d.get('telefon',[''])[0]
        fax=d.get('fax',[''])[0]
        email=d.get('email',[''])[0]
        mrt=d.get('mrt',[''])[0]
        hrt=d.get('hrt',[''])[0]
    # Always escape user input to avoid script injection
        funkrufname = escape(funkrufname)
        organisation=escape(organisation)
        fahrzeugtyp=escape(fahrzeugtyp)
        zf= escape(zf)
        gf=escape(gf)
        helfer=escape(helfer)
        bemerkung=escape(bemerkung)
        sonderbeladung=escape(sonderbeladung)
        fuehrung = [escape(f) for f in fuehrung]
        notarzt=escape(notarzt)
        arzt=escape(arzt)
        notsan=escape(notsan)
        rs=escape(rs)
        liegend=escape(liegend)
        tragestuhl=escape(tragestuhl)
        sitzend=escape(sitzend)
        atemschutz=escape(atemschutz)
        csa=escape(csa)
        sanitaeter=escape(sanitaeter)
        loeschwasser=escape(loeschwasser)
        schaummittel=escape(schaummittel)
        telefon=escape(telefon)
        fax=escape(fax)
        email=escape(email)
        mrt=escape(mrt)
        hrt=escape(hrt)
        #try:
        if environ['REQUEST_METHOD'] == 'POST':
            print(fuehrung)
            try:
                if fuehrung[0]=="1" or fuehrung[0]=="f\xc3\xbchrung":
                    var=1
                else:
                    var=0
            except IndexError as e:
                var=0
            

            if bemerkung=="Bemerkung":
                bemerkung=""    

            tupel=(funkrufname, organisation, fahrzeugtyp, zf, gf, helfer, var, bemerkung, sonderbeladung, notarzt, arzt, notsan, rs, liegend, tragestuhl, sitzend, atemschutz, csa, sanitaeter, loeschwasser, schaummittel, telefon, fax, email, mrt, hrt)

            print("putting tupel:")
            self.queue.put_nowait(tupel)
            print("\t CCOMPLETE")
            wait= True
            while wait:
                if self.r_queue.full():
                    err=self.r_queue.get_nowait()
                    print(err)
                    wait= False

        

        response_body = html % { # Fill the above html template in
            'checked-führung': ('', 'checked')['führung' in fuehrung],
            'funkrufname': funkrufname or '',
            'organisation': organisation or '',
            'fahrzeugtyp': fahrzeugtyp or '',
            'zf': zf or '0',
            'gf': gf or '0',
            'helfer': helfer or '0',
            'bemerkung': bemerkung or '',
            'führung': ', '.join(fuehrung or ['']),
            'error_code': err or '',
            'sonderbeladung': sonderbeladung or '',
            'notarzt': notarzt or '',
            'arzt': arzt or '',
            'notsan': notsan or '',
            'rs': rs or '',
            'liegend': liegend or '',
            'tragestuhl': tragestuhl or '',
            'sitzend': sitzend or '',
            'atemschutz': atemschutz or '',
            'csa': csa or '',
            'sanitaeter': sanitaeter or '',
            'loeschwasser': loeschwasser or '',
            'schaummittel': schaummittel or '',
            'telefon': telefon or '',
            'fax': fax or '',
            'email': email or '',
            'mrt': mrt or '',
            'hrt': hrt or ''
        }

        if err=='Error1':
            html_status='201 OK'
        elif err=='Error2':
            html_status='202 OK'
        else:
            html_status = '200 OK'

        response_headers = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(response_body)))
        ]
    
        start_response(html_status, response_headers)
        self.status=False

        return [response_body]
        #except:
         #   print("Unexpected error in webserver!")

#httpd = make_server('localhost', 8051, application)
#httpd.serve_forever()
