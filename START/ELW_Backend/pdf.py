from fpdf import FPDF


class MyPDF(FPDF):

    #it sucks that these members do not belong to specific object instances, but I can use __init__
    #since it overwrites the FPDF contructor and then shit does not work...
    # on the other hand this shouldnt be to bad for my case as the PDF generator only generates one
    # pdf at the time and time and name are set within the contructor for the PDF generator
	time='zeit'
	name='name'


	def header(self):
		self.set_font('Arial', '', 11)
		self.cell(40, 10, 'Bereitstellungsraum:', ln=0)
		self.cell(10, 10, self.name, ln=0)
		self.cell(0,10, self.time, align='R', ln=1)
		self.ln(10)


	def footer(self):
		self.set_y(-15)
		self.set_font('Arial', '', 11)
		self.cell(40,10, 'generiert durch START:QR', ln=0)

		page= 'Seite %s/ {nb}' % self.page_no()

		self.cell(0, 10, page, align='R')


class PDFgenerator:

	def __init__(self, content, name, time):
		self.content=content
		self.name=name
		self.time=time

	def generate(self):

		pdf=MyPDF()
		pdf.time=self.time
		pdf.name=self.name
		pdf.alias_nb_pages()
		pdf.add_page()


		pdf.set_font('Arial', '', 14)

		header_name='Bereitstellungsraum '+self.name

		pdf.cell(20, 10, 'von:', 0, 0)
		pdf.cell(20, 10, header_name, ln=1)
		pdf.cell(20, 10, 'Zeit:', 0, 0)
		pdf.cell(20, 10, self.time, 0, 1)

		pdf.set_font('Arial', 'B' , 14)
		pdf.ln(10)
		pdf.cell(20, 10, 'Einheiten in Bereitstellung:', 0, 1)

		pdf.cell(70, 10, 'Funkrufname', 0, 0)
		pdf.cell(50, 10, 'Organisation', 0, 0)
		pdf.cell(40, 10, 'Typ', 0, 0)
		pdf.cell(0, 10, 'Besatzung', 0 ,1)

		current_x =pdf.get_x()
		current_y =pdf.get_y()

		pdf.line(current_x, current_y, current_x+190, current_y)

		pdf.set_font('Arial', '', 14)


		for i in self.content:
			if pdf.y + 10 > pdf.page_break_trigger:
				pdf.set_font('Arial', 'B' , 14)

				pdf.cell(70, 10, 'Funkrufname', 0, 0)
				pdf.cell(50, 10, 'Organisation', 0, 0)
				pdf.cell(40, 10, 'Typ', 0, 0)
				pdf.cell(0, 10, 'Besatzung', 0 ,1)

				current_x =pdf.get_x()
				current_y =pdf.get_y()

				pdf.line(current_x, current_y, current_x+190, current_y)

				pdf.set_font('Arial', '', 14)
			else:		
				pdf.cell(70, 10, i[1], 0, 0)
				pdf.cell(50, 10, i[2], 0, 0)
				pdf.cell(40, 10, i[3], 0, 0)
				pdf.cell(0, 10, '{}/{}/{}'.format(i[4],i[5],i[6]), 0, 1)

		pdf.output(self.time+self.name+".pdf")	

