from flask import Flask, render_template, url_for, request, redirect, session 
from flask import Response
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import ast
import os
import io
import csv
from flask_mail import Mail, Message


# GLOBALNA funkcija, za proveru da li je korisnik ulogovan
def ulogovan():
	if 'ulogovani_korisnik' in session:
		return True
	else:
		return False



# GLOBALNA funkcija, za proveru koja je rola korisnika, koji je ulogovan
def rola():
   if ulogovan():
       return ast.literal_eval(session["ulogovani_korisnik"]).pop("rola")


# GLOBALNA funkcija, za dobijanje id-a prijavljenog studenta
def getStudentId():

	# Vracanje id-a od ulogovanog studenta da bi mogao kasnije da pristupi svojoj stranici

	# Upit ka bazi
	upit = 	""" 
			SELECT id FROM studenti
			WHERE email = %s
			"""
	# Izvršavanje upita i cuvanje dobijene vrednosti 
	kursor.execute(upit,(ast.literal_eval(session['ulogovani_korisnik']).pop('email'),) )
	# Cuvanje dobijene vrednosti
	id = kursor.fetchone()
	# Vracanje dobijenog id studenta
	return id['id']






#Konekcija sa bazom:
konekcija = mysql.connector.connect(
    passwd="", # lozinka za bazu 
    user="root", # korisničko ime
    database="evidencija_studenata", # ime baze
    port=3306, # port na kojem je mysql server
    auth_plugin='mysql_native_password' # ako se koristi mysql 8.x 
)

#Kreiranje kursora za izvršenje upita:
kursor = konekcija.cursor(dictionary = True,buffered = True)




# deklaracija Flask aplikacije ispod “import-a”
app = Flask(__name__)

# Tajni kljuc za Flask sesiju :
app.secret_key = "tajni_kljuc_aplikacije"



# Konfiguracija za cuvanje slika na serveru : 
UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Konfiguracija za slanje mejla novokreiranom korisniku:
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "evidencija.atvss@gmail.com"
app.config["MAIL_PASSWORD"] = "atvss123loz"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

# GLOBALNA funkcija za slanje mejla, novokreiranom korisniku
def send_email(ime,prezime,email,lozinka):
	msg = Message(
					subject = 'Korisnički nalog',
					sender = 'ATVSS Evidencija studenata',
					recipients=[email],
				)
	msg.html = render_template("email.html", ime=ime, prezime=prezime, lozinka=lozinka)
	mail.send(msg)
	return "Sent"





#DEFINICIJA RUTA :

# Pocetna ruta
@app.route('/', methods = ['GET'])
def start():
    	if ulogovan():
    			return redirect(url_for('studenti'))
	
    	return redirect(url_for('login'))



#Definisanje rute "login"
@app.route('/login', methods=['GET','POST'])
def login():
	if(request.method == 'GET'):
		return render_template('login.html')

	#Post
	elif(request.method == 'POST'):
		forma = request.form
		upit = "SELECT * FROM korisnici WHERE email=%s"
		vrednosti = (forma['email'],)
		kursor.execute(upit,vrednosti)
		
		# Parsiranje emaila
		korisnik = kursor.fetchone()

		# Parsiranje lozinke
		if (check_password_hash(korisnik['lozinka'] , forma['lozinka'])):
			session['ulogovani_korisnik'] = str(korisnik)
			return redirect(url_for('studenti'))
		else:
			return render_template('login.html')





#Definisanje rute "logout"
@app.route('/logout', methods=['GET'])
def logout():
	session.pop('ulogovani_korisnik',None)
	return redirect(url_for('login'))







#Definisanje rute "korisnici"
@app.route('/korisnici', methods=['GET'])
def korisnici():
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():

		# Paginacija

		prethodna_strana = ""
		strana = request.args.get('page', '1')
		sledeca_strana = "2"
		if "page=" in request.full_path:
			split_path = request.full_path.split("page=")
			del split_path[-1]
			sledeca_strana 	 =  str(int(strana) + 1)
			prethodna_strana =  str(int(strana) - 1)


		# SORTIRANJE :

		# Pormenljive sa default vrednostima za sortiranje.
		# Sortiranje po defaultu se vrsi po:
		order_by = 'id'  # id kolone
		order_type = 'asc' # ulazni poredak


		# Pretvaranje atgumenata poslatih metodom GET u tip recnik (radi lakseg baratanja) 
		args = request.args.to_dict()

		# U slucaju da je "zahtev" za sortiranje poslat putem GET
		if ('order_by' in args and args['order_by'] != ''):
			order_by = args['order_by'].lower() # Vrednost (kolonu po kojoj ce se sortirati) sacuvamo.

			# U slucaju da je prethodno sortiranje poslato GET-om i da imam istu vrednost kao
			# sadašnju (znači zahteva se sortiranje po istoj koloni uzastopno) 
			if ('prethodni_order_by' in args and args['prethodni_order_by'] == args['order_by']):
				# Vrši se promena poretka sortiranja
				if (args['order_type'] == 'asc'):
					order_type = 'desc'
					



		# PPRETRAŽIVANJE I FILTRIRANJE :

		# Postavljanje inicijalnih vrednosti i izmena onih koje su poslate kroz forme GET metodom:
		s_ime =  "%" +args['ime']+ "%" if 'ime' in args else "%%"
		s_prezime =  "%" +args['prezime']+ "%" if 'prezime' in args else "%%"
		s_email =  "%" +args['email']+ "%" if 'email' in args else "%%"
		s_rola =  "%" +args['rola']+ "%" if 'rola' in args else "%%"
		 

		# Upit ka bazi (sadrži podatke za : Paginaciju, Sortiranje i Filtriranje)

		upit = 	""" SELECT * FROM korisnici
					WHERE 
					ime 	LIKE %s AND
					prezime LIKE %s AND
					email 	LIKE %s AND
					rola 	LIKE %s 
					ORDER BY {0} {1}
					LIMIT 10 offset %s
					""".format(order_by,order_type,)


		# Paginacija : računanje od kog zapisa se počinje
		offset = int(strana) * 10 - 10

		# Vrednost potrebne za upit:
		vrednosti = (	s_ime,
						s_prezime,
						s_email,
						s_rola,
						offset
					)

		# Izvršavanje upita :
		kursor.execute(upit, vrednosti)

		# Čuvanje isčitanih podataka, radi prosleđivanja stranici
		korisnici = kursor.fetchall()
		

		

		# Vračanje kreirane stranice u kojoj ce postojati obj korisnici
		return render_template('korisnici.html',
							    korisnici = korisnici, 
							    strana = strana,
							    prethodna_strana = prethodna_strana,
							    sledeca_strana = sledeca_strana,
							    order_type = order_type,
							    args = args
							   )
	
	else:
		return redirect(url_for('login'))






#Definisanje korisniknik_novi"
@app.route('/korisnik_novi', methods=['GET','POST'])
def korisnik_novi():
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))


	if ulogovan():
		# U slucaju da je korisnik pristupipo strani pomocu URL-a
		if(request.method == 'GET'):
			return render_template('korisnik_novi.html')
	
		# U slucaju da je korisnik pristupio stranicni, pomocu forme 
		elif(request.method == 'POST'):
			forma = request.form
			hesovana_lozinka = generate_password_hash(forma['lozinka'])
			
			vrednosti =(
				forma['ime'],
				forma['prezime'],
				forma['email'],
				hesovana_lozinka,
				forma['rola']
				)
	
			# Dodavanje korisnika u bazi(tabela : korisnici)
			upit = """ 	INSERT INTO 
						korisnici (ime,prezime,email,lozinka,rola)
						VALUES (%s, %s,%s,%s,%s)
					"""
			# Korisnik kreiran
			kursor.execute(upit,vrednosti)
			konekcija.commit()

			# Obaveštenje korisnika, putem maila, da je za njega kreiran korisnički nalog
			# GRESKA :  send_email(forma['ime'],forma['prezime'],forma['email'],forma['lozinka'])
		

			return redirect(url_for('korisnici'))
	else :
		return redirect(url_for('login'))




#Definisanje rute "korisnik_izmena/<id>"
@app.route('/korisnik_izmena/<id>', methods=['GET','POST'])
def korisnik_izmena(id):
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		if(request.method == 'GET'):
			
			upit = "SELECT * FROM korisnici WHERE id = %s"
			vrednost = (id,)
			kursor.execute(upit,vrednost)
			korisnik = kursor.fetchone()
	
			return render_template('korisnik_izmena.html',korisnik = korisnik)
	
	
		elif(request.method == 'POST'):
			upit = """ UPDATE korisnici SET
						ime = %s,
						prezime = %s,
						email = %s,
						lozinka = %s,
						rola = %s
						WHERE id = %s
					"""
			
			forma = request.form
			hesovana_lozinka = generate_password_hash(forma['lozinka'])
			vrednosti = (	
					forma['ime'],
					forma['prezime'],
					forma['email'],
					hesovana_lozinka,
					forma['rola'],
					id
						)
			kursor.execute(upit,vrednosti)
			konekcija.commit()
			return redirect(url_for('korisnici'))

	else:
		return redirect(url_for('login'))



#Definisanje rute "korisnik_brisanje/<id>"
@app.route('/korisnik_brisanje/<id>', methods=['GET'])
def korisnik_brisanje(id):
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		upit = 'DELETE FROM korisnici WHERE id = %s'
		vrednosti = (id,)
		kursor.execute(upit,vrednosti)
		konekcija.commit()
	
		return redirect(url_for('korisnici'))
	
	else:
		return redirect(url_for('login'))








# S T U D E N T I:

#Definisanje rute "studenti"
@app.route('/studenti', methods=['GET'])
def studenti():
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if ulogovan():

		# PAGINACIJA: 
		prethodna_strana = ""
		strana = request.args.get('page', '1') 
		sledeca_strana = "2"
		if "page=" in request.full_path:	
			split_path = request.full_path.split("page=")
			del split_path[-1]
			sledeca_strana = str(int(strana) + 1)
			prethodna_strana = str(int(strana) - 1)     


		# SORTIRANJE :

		# Pormenljive sa default vrednostima za sortiranje.
		# Sortiranje po defaultu se vrsi po:
		order_by = 'id'  # id kolone
		order_type = 'asc' # ulazni poredak


		# Pretvaranje atgumenata poslatih metodom GET u tip recnik (radi lakseg baratanja) 
		args = request.args.to_dict()

		# U slucaju da je "zahtev" za sortiranje poslat putem GET
		if ('order_by' in args and args['order_by'] != ''): 
			order_by = args['order_by'].lower() # Vrednost (kolonu po kojoj ce se sortirati) sacuvamo.

			# U slucaju da je prethodno sortiranje poslato GET-om i da imam istu vrednost kao
			# sadašnju (znači zahteva se sortiranje po istoj koloni uzastopno) 
			if ('prethodni_order_by' in args and args['prethodni_order_by'] == args['order_by']):
				# Vrši se promena poretka sortiranja
				if (args['order_type'] == 'asc'):
					order_type = 'desc'

		# PPRETRAŽIVANJE I FILTRIRANJE :

		# Postavljanje inicijalnih vrednosti i izmena onih koje su poslate kroz forme GET metodom:
		s_broj_indeksa =  "%" +args['broj_indeksa']+ "%" if 'broj_indeksa' in args else "%%"
		s_ime =  "%" +args['ime']+ "%" if 'ime' in args else "%%"
		s_prezime =  "%" +args['prezime']+ "%" if 'prezime' in args else "%%"
		s_godina_studija =  "%" +args['godina_studija']+ "%" if 'godina_studija' in args else "%%"
		s_espb_od =  args['espb_od'] if 'espb_od' in args else 0
		s_espb_do =  args['espb_do'] if 'espb_do' in args and args['espb_do'] != '' else 270
		s_prosek_od = args['prosek_od'] if 'prosek_od' in args  else 0
		s_prosek_do = args['prosek_do'] if 'prosek_do' in args and args['prosek_do'] != '' else 10



		# Upit ka bazi (sadrži podatke za : Paginaciju, Sortiranje i Filtriranje)
	
		upit = 	""" SELECT * FROM studenti
					WHERE 
					broj_indeksa 	LIKE %s AND
					ime   		   	LIKE %s AND
					prezime 	   	LIKE %s AND
					godina_studija 	LIKE %s AND
					espb >= %s AND espb <= %s AND
					prosek_ocena >= %s AND prosek_ocena <= %s
					ORDER BY {0} {1}
					LIMIT 10 offset %s
					""".format(order_by,order_type,)

		
		# Paginacija : računanje od kog zapisa se počinje
		offset = int(strana) * 10 - 10

		# Vrednosti za izvršenje upita
		vrednosti = (	s_broj_indeksa,
						s_ime,
						s_prezime,
						s_godina_studija,
						s_espb_od,
						s_espb_do,
						s_prosek_od,
						s_prosek_do,
						offset,
					)

		# Izvršavanje upita gde prosleđujemo, od kog zapisa se počinje, kolonu i način sortiranja
		kursor.execute(upit,vrednosti)
	
		# Cuvanje iscitanih podataka, radi prosleđivanja stranici
		studenti = kursor.fetchall()


		# Renderovanje stranice, sa zadatim parametrima
		return render_template('studenti.html', 
								studenti = studenti,
								rola = rola(),
								strana = strana,
								prethodna_strana = prethodna_strana,
								sledeca_strana = sledeca_strana,
								order_type = order_type,
								args = args
								)
	
	else:
		return redirect(url_for('login'))




#Definisanje rute "student/<id>"
@app.route('/student/<id>', methods=['GET'])
def student(id):
	if ulogovan():
    	# Pretvaranje atgumenata poslatih metodom GET u tip recnik (radi lakseg baratanja) 
		args = request.args.to_dict()	

		if (rola() == 'student' and int(id) != int(getStudentId()) ):
    			return redirect(url_for('student', id = getStudentId()))
    			
    	# PAGINACIJA
		prethodna_strana = ""
		strana = request.args.get('page', '1') 
		sledeca_strana = "2"
		if "page=" in request.full_path:	
			split_path = request.full_path.split("page=")
			del split_path[-1]
			sledeca_strana = str(int(strana) + 1)
			prethodna_strana = str(int(strana) - 1)   


		# Selektovanje odredjenog studenta iz baze
		upit = 'SELECT * FROM studenti WHERE id = %s'
		vrednosti = (id,)
		kursor.execute(upit,vrednosti)

		# Čuvanje vrednosti tog studenta, radi prosledjivanja stranici
		student = kursor.fetchone()


		# Upit za selektovanje svih predmeta iz baze(tebela : predmeti) 
		# iz kojih student nema upisanu ocenu, da bi se mogli prikazati, u <select> tagu.
		upit = 	""" SELECT * From Predmeti 
					WHERE id NOT IN ( SELECT ocene.predmet_id FROM ocene WHERE ocene.student_id = %s) 
				"""
		kursor.execute(upit, vrednosti)
		predmeti = kursor.fetchall() 



		# SORTIRANJE :

		# Promenljive sa default vrednostima za sortiranje.
		# Sortiranje po defaultu se vrsi po:
		order_by = 'oid'  # id kolone
		order_type = 'asc' # ulazni poredak


		

		# U slucaju da je "zahtev" za sortiranje poslat putem GET
		if ('order_by' in args and args['order_by'] != ''):
			order_by = args['order_by'].lower() # Vrednost (kolonu po kojoj ce se sortirati) sacuvamo.

			# U slucaju da je prethodno sortiranje poslato GET-om i da imam istu vrednost kao
			# sadašnju (znači zahteva se sortiranje po istoj koloni uzastopno) 
			if ('prethodni_order_by' in args and args['prethodni_order_by'] == args['order_by']):
				# Vrši se promena poretka sortiranja
				if (args['order_type'] == 'asc'):
					order_type = 'desc'

		# PPRETRAŽIVANJE I FILTRIRANJE :

		# Postavljanje inicijalnih vrednosti i izmena onih koje su poslate kroz forme GET metodom:
		s_sifra =  "%" +args['sifra']+ "%" if 'sifra' in args else "%%"
		s_naziv =  "%" +args['naziv']+ "%" if 'naziv' in args else "%%"
		s_godina_studija =  "%" +args['godina_studija']+ "%" if 'godina_studija' in args else "%%"
		s_espb_od =  args['espb_od'] if 'espb_od' in args else 0
		s_espb_do =  args['espb_do'] if 'espb_do' in args and args['espb_do'] != '' else 240
		s_obavezni_izborni =  "%" +args['obavezni_izborni']+ "%" if 'obavezni_izborni' in args else "%%"
		s_ocena =  "%" +args['ocena']+ "%" if 'ocena' in args else "%%"	









		# Upit ka bazi (Sadrzi podatke za : Sortiranje , Filtriranje ) 
		# Koji će iscitava sve predmete za datog studenta(id), kao i ocenu iz datog predmeta(oid)
		
		upit =	""" SELECT ocene.id as oid,
					predmeti.sifra, 
					predmeti.naziv, 
					predmeti.godina_studija, 
					predmeti.espb, 
					predmeti.obavezni_izborni,
					ocene.ocena 
					FROM predmeti 
					INNER JOIN ocene
					ON predmeti.id = ocene.predmet_id
					WHERE 
					predmeti.sifra 	LIKE %s AND 
					predmeti.naziv 	LIKE %s AND
					predmeti.godina_studija LIKE %s AND
					predmeti.espb >= %s  AND predmeti.espb <= %s AND
					predmeti.obavezni_izborni LIKE %s AND
					ocene.ocena 	LIKE %s AND
					ocene.student_id = %s
					ORDER BY {0} {1}
					LIMIT 10 offset %s
				""".format(order_by,order_type)
		offset =  int(strana) * 10 - 10
		
		# Definisanje vrednosti za upit 
		vrednosti = ( s_sifra,
					  s_naziv,
					  s_godina_studija,
					  s_espb_od,
					  s_espb_do,
					  s_obavezni_izborni,
					  s_ocena,
					  id,
					  offset
					  )
		# Izvrsavanje upita
		kursor.execute(upit,vrednosti)
		# Čuvanje vrednosti svih predmeta i ocena iz predmeta
		predmeti_ocene = kursor.fetchall()



		
		return render_template('student.html', 
								student = student, 
								predmeti = predmeti, 
								predmeti_ocene = predmeti_ocene, 
								rola = rola(),
								order_type = order_type,
								args = args,
								strana = strana,
								prethodna_strana = prethodna_strana,
								sledeca_strana = sledeca_strana,
								)



	else:
		return redirect(url_for('login'))






#Definisanje rute "student_novi"
@app.route('/student_novi', methods=['GET','POST'])
def student_novi():

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		if(request.method == 'GET'):
			return render_template('student_novi.html')
	
		elif(request.method == 'POST'):
			forma = request.form

			naziv_slike = ""
			if "slika" in request.files:
				file = request.files["slika"]
				if file.filename:	
					naziv_slike = forma["jmbg"] + file.filename              
					file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))




			upit = """ 	INSERT INTO 
						studenti(broj_indeksa , ime, ime_roditelja, prezime, email, broj_telefona, godina_studija, datum_rodjenja, jmbg, slika)
						VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
					"""

			



			
			vrednosti = (
						forma['broj_indeksa'],
						forma['ime'],
						forma['ime_roditelja'],
						forma['prezime'],
						forma['email'],
						forma['broj_telefona'],
						forma['godina_studija'],
						forma['datum_rodjenja'],
						forma['jmbg'],
						naziv_slike
						)		
	
			kursor.execute(upit,vrednosti)
			konekcija.commit()
	
			return redirect(url_for('studenti'))

	else:
		return redirect(url_for('login'))




#Definisanje rute "student_izmena/<id>"
@app.route('/student_izmena/<id>', methods=['GET','POST'])
def student_izmena(id):
	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		if(request.method == 'GET'):
			upit = "SELECT * FROM studenti WHERE id = %s"
			vrednost = (id,)
			kursor.execute(upit,vrednost)
			student = kursor.fetchone()
	
			return render_template('student_izmena.html',student = student, rola = rola())



		elif(request.method == 'POST'):	
			# Upit ka bazi, za isčitavanje trenutne slke
			upit = ' SELECT slika FROM studenti WHERE id = %s'
			# Izvršavanje upita 
			kursor.execute(upit,(id,))
			# Cuvanje slike
			trenutna_slika = kursor.fetchone()
			trenutna_slika = trenutna_slika['slika']


			# Prikupljanje podataka koji su postali POST metodom pomoću forme
			forma = request.form
			
			naziv_slike = trenutna_slika
			if "slika" in request.files:
				file = request.files["slika"]
				if file.filename:
					naziv_slike = forma["jmbg"] + file.filename
					file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))
					if(trenutna_slika):
						os.remove(os.path.join(app.config["UPLOAD_FOLDER"],trenutna_slika))
					


			upit = """ UPDATE studenti SET
						broj_indeksa = %s,
						ime = %s,
						ime_roditelja = %s,
						prezime = %s,
						email = %s,
						broj_telefona = %s,
						godina_studija = %s,
						datum_rodjenja = %s,
						jmbg = %s,
						slika = %s

						WHERE id = %s
					"""
			

			vrednosti = (	
					forma['broj_indeksa'],
					forma['ime'],
					forma['ime_roditelja'],
					forma['prezime'],
					forma['email'],
					forma['broj_telefona'],
					forma['godina_studija'],
					forma['datum_rodjenja'],
					forma['jmbg'],
					naziv_slike,
					id
					)


			kursor.execute(upit,vrednosti)
			konekcija.commit()
			return redirect(url_for('studenti'))
	
	else:
		return redirect(url_for('login'))




#Definisanje rute "student_brisanje/<id>"
@app.route('/student_brisanje/<id>', methods=['GET'])
def student_brisanje(id):

	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))
	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		vrednosti = (id,)

		# Upit za selektovanje slike iz tabele student:
		upit = 'SELECT slika FROM studenti WHERE id = %s'
		kursor.execute(upit,vrednosti)
		student_slika = kursor.fetchone()
		# Funkcija za brisanje slike sa servera
		if ('' != student_slika['slika']) :
			os.remove(os.path.join(app.config['UPLOAD_FOLDER'], student_slika['slika']))

		# Upit za brisanje studenta zajedno sa njihovim ocenama iz baze :
		upit = 	"""
				DELETE  studenti,ocene FROM studenti 
				LEFT JOIN ocene  ON studenti.id = ocene.student_id 
				WHERE studenti.id = %s
				"""
		kursor.execute(upit,vrednosti)
		konekcija.commit()

		return redirect(url_for('studenti'))

	else:
		return redirect(url_for('login'))







# Predmeti:

#Definisanje rute "predmeti"
@app.route('/predmeti', methods=['GET'])
def predmeti():
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		
		# PAGINACIJA: 
		prethodna_strana = ""
		strana = request.args.get('page', '1') 
		sledeca_strana = "2"
		if "page=" in request.full_path:	
			split_path = request.full_path.split("page=")
			del split_path[-1]
			sledeca_strana = str(int(strana) + 1)
			prethodna_strana = str(int(strana) - 1)   
			

		







		# SORTIRANJE :

		# Pormenljive sa default vrednostima za sortiranje.
		# Sortiranje po defaultu se vrsi po:
		order_by = 'id'  # id kolone
		order_type = 'asc' # ulazni poredak


		# Pretvaranje atgumenata poslatih metodom GET u tip recnik (radi lakseg baratanja) 
		args = request.args.to_dict()

		# U slucaju da je "zahtev" za sortiranje poslat putem GET
		if ('order_by' in args and args['order_by'] != ''): 
			order_by = args['order_by'].lower() # Vrednost (kolonu po kojoj ce se sortirati) sacuvamo.

			# U slucaju da je prethodno sortiranje poslato GET-om i da imam istu vrednost kao
			# sadašnju (znači zahteva se sortiranje po istoj koloni uzastopno) 
			if ('prethodni_order_by' in args and args['prethodni_order_by'] == args['order_by']):
				# Vrši se promena poretka sortiranja
				if (args['order_type'] == 'asc'):
					order_type = 'desc'
				
				




		# PPRETRAŽIVANJE I FILTRIRANJE :

		# Postavljanje inicijalnih vrednosti i izmena onih koje su poslate kroz forme GET metodom:
		s_sifra =  "%" +args['sifra']+ "%" if 'sifra' in args else "%%"
		s_naziv =  "%" +args['naziv']+ "%" if 'naziv' in args else "%%"
		s_godina_studija =  "%" +args['godina_studija']+ "%" if 'godina_studija' in args else "%%"
		s_espb_od =  args['espb_od'] if 'espb_od' in args else 0
		s_espb_do =  args['espb_do'] if 'espb_do' in args and args['espb_do'] != '' else 240	
		s_obavezni_izborni =  "%" +args['obavezni_izborni']+ "%" if 'obavezni_izborni' in args else "%%"


		# Upit ka bazi (sadrži podatke za : Paginaciju, Sortiranje i Filtriranje)
	
		upit = 	""" SELECT * FROM predmeti
					WHERE 
					sifra LIKE %s AND
					naziv LIKE %s AND
					godina_studija LIKE %s AND
					espb >= %s AND espb <= %s
					AND
					obavezni_izborni LIKE %s 
					ORDER BY {0} {1}
					LIMIT 10 offset %s
					""".format(order_by,order_type,)

		# Paginacija : računanje od kog zapisa se počinje
		offset = int(strana) * 10 - 10
		
		# Vrednosti potrebne za upit
		vrednosti = (	s_sifra, 
						s_naziv, 
						s_godina_studija,
						s_espb_od,
						s_espb_do,
						s_obavezni_izborni,
						offset,)

		# Izvršavanje upita :
		kursor.execute(upit,vrednosti)

		# Čuvanje isčitanih podataka, radi prosleđivanja stranici
		predmeti = kursor.fetchall()
		

	
		# Vracanje stranice predmeti.html, u kojoj postoji obj predmeti
		return render_template('predmeti.html',
							    predmeti = predmeti,
							    strana = strana,
							    sledeca_strana = sledeca_strana,
							    prethodna_strana = prethodna_strana,
							    test = strana,
							    order_type = order_type,
								args = args
							    )

	else:
		return redirect(url_for('login'))









#Definisanje rute "predmet_novi"
@app.route('/predmet_novi', methods=['GET','POST'])
def predmet_novi():
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		if(request.method == 'GET'):
			return render_template('predmet_novi.html')
	
		elif(request.method == 'POST'):
			upit =   """ INSERT INTO 
						predmeti (sifra,naziv,godina_studija,espb,obavezni_izborni)
						VALUES (%s, %s,%s,%s,%s)
					"""
	
			forma = request.form
			vrednoti = (
						forma['sifra'],
						forma['naziv'],
						forma['godina_studija'],
						forma['espb'],
						forma['obavezni_izborni']
						)

	
			kursor.execute(upit,vrednoti)
			konekcija.commit()
	
			return redirect(url_for('predmeti'))

	else:
		return redirect(url_for('login'))



#Definisanje rute "predmet_izmena/<id>"
@app.route('/predmet_izmena/<id>', methods=['GET','POST'])
def predmet_izmena(id):
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		if(request.method == 'GET'):
			upit = 'SELECT * FROM predmeti WHERE id = %s'
			vrednosti = (id,)
			kursor.execute(upit,vrednosti)
			predmet = kursor.fetchone()
	
			return render_template('predmet_izmena.html', predmet = predmet)
	
	
		elif(request.method == 'POST'):
			upit = """ UPDATE predmeti SET
						sifra = %s,
						naziv = %s,
						godina_studija = %s,
						espb = %s,
						obavezni_izborni = %s
						WHERE id = %s
					"""
			forma = request.form
			vrednosti = (	
					forma['sifra'],
					forma['naziv'],
					forma['godina_studija'],
					forma['espb'],
					forma['obavezni_izborni'],
					id
						)
			kursor.execute(upit,vrednosti)
			konekcija.commit()
			return redirect(url_for('predmeti'))

	else:
		return redirect(url_for('login'))



#Definisanje rute "predmet_brisanje/<id>"
@app.route('/predmet_brisanje/<id>', methods=['GET'])
def predmet_brisanje(id):
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if rola() == 'profesor':
		return redirect(url_for('studenti'))

	if ulogovan():
		upit = 'DELETE FROM predmeti WHERE id = %s'
		vrednosti = (id,)
		kursor.execute(upit,vrednosti)
		konekcija.commit()
	
		return redirect(url_for('predmeti'))

	else:
		return redirect(url_for('login'))

# krajPredmeti






#Definisanje rute "ocena_nova/<id>"
@app.route('/ocena_nova/<id>', methods=['POST'])
def ocena_nova(id):
	if ulogovan():
	
		# UPITI ka bazi:

		# Dodavanje nove ocene u tabeli ocene:
		upit = 	""" INSERT INTO ocene(student_id, predmet_id, ocena, datum)
    	        VALUES(%s, %s, %s, %s)
				"""
	
		forma = request.form
		vrednosti = (
					id,
					forma['predmet'],
					forma['ocena'],
					forma['datum']
					)
	
		kursor.execute(upit,vrednosti)
		konekcija.commit()


		# Racunanje proseka ocena :
		upit = 'SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s'
		vrednoti = (id,)
		kursor.execute(upit,vrednoti)
		prosek_ocena = kursor.fetchone()


		# Racunanje ukupno espb :
		upit = """SELECT SUM(espb) AS rezultat FROM predmeti 
		WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"""

		vrednoti = (id,)
		kursor.execute(upit,vrednoti)
		espb = kursor.fetchone()


		# Izmena tabele student :
		upit = 'UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s' 
		vrednoti = (
					espb['rezultat'],
					prosek_ocena['rezultat'],
					id
					)
		kursor.execute(upit,vrednoti)
		konekcija.commit()

		return redirect(url_for('student',id = id))

	else:
		return redirect(url_for('login'))


#Definisanje rute "ocena_brisanje/<id>/<oid>"
@app.route('/ocena_brisanje/<id>/<oid>', methods=['GET'])
def ocena_brisanje(id, oid):
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if ulogovan():

		upit = 'DELETE FROM ocene WHERE id = %s'
		vrednoti = (oid,)
		kursor.execute(upit,vrednoti)
		konekcija.commit()
		
		# Racunanje proseka ocena :
		upit = 'SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s'
		vrednoti = (id,)
		kursor.execute(upit,vrednoti)
		prosek_ocena = kursor.fetchone()


		# Racunanje ukupno espb :
		upit = """SELECT SUM(espb) AS rezultat FROM predmeti 
		WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"""

		vrednoti = (id,)
		kursor.execute(upit,vrednoti)
		espb = kursor.fetchone()


		# Izmena tabele student :
		upit = 'UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s' 
		vrednoti = (
					espb['rezultat'],
					prosek_ocena['rezultat'],
					id
					)
		kursor.execute(upit,vrednoti)
		konekcija.commit()


		return redirect(url_for('student',id = id))

	else:
		return redirect(url_for('login'))




#Definisanje rute "ocena_izmena/<id>"
@app.route('/ocena_izmena/<id>/<oid>', methods=['GET','POST'])
def ocena_izmena(id, oid):
	if rola() == 'student':
		return redirect(url_for('student',id = getStudentId()))

	if ulogovan():
		if(request.method == 'GET'):

			# Upit za selektovanje potrebnih zapisa za promenu ocene, koji ce se proslediti stranici za promenu ocene:
			upit = 	""" SELECT ocene.id as oid, ocene.student_id as sid,
					predmeti.naziv, ocene.ocena, ocene.datum 
					FROM predmeti 
					INNER JOIN ocene
					ON predmeti.id = ocene.predmet_id
					WHERE ocene.student_id = %s and ocene.id = %s
					"""

			# Prosledjivanje vrednosti
			vrednoti = (id,oid)

			# Izvrsavanje upita
			kursor.execute(upit,vrednoti)

			# Cuvanej dobijenih rezultata, radi prosleđivanja na stranici
			predmet_ocena = kursor.fetchone()


			# Iscrtavanje odgovarajuce teplejta
			return render_template('ocena_izmena.html', predmet_ocena = predmet_ocena)

		# Prosledjivanje podataka pomocu forme
		elif (request.method == 'POST'):

				# Ažuriranje ocna, po izmenu ocene
				upit = 	""" UPDATE ocene 
							SET 
							ocena = %s,
							datum = %s
							where student_id = %s AND ocene.id = %s
						"""

				# Prikupljanje podataka iz forme		
				forma = request.form
				vrednoti = (forma['ocena'],forma['datum'], id,oid)
				# Izvršenje upita
				kursor.execute(upit,vrednoti)
				konekcija.commit()

				# Ažuriranje proseka ocene studenta

				# Računanje novog proseka 
				upit = 'SELECT AVG(ocena) as prosek FROM ocene WHERE student_id = %s'
				# Izvršenje upita
				kursor.execute(upit,(id,))
				# Čuvanje novodobijenog proseka:
				prosek = kursor.fetchone()
				prosek = prosek['prosek']

				# Ažuriranje proseka u tabeli student:

				# Upit za ažuriranje
				upit = 'UPDATE studenti set prosek_ocena = %s WHERE id = %s'
				# Izvršavanje upita
				kursor.execute(upit,(prosek,id))


				return redirect(url_for('student', id = id))




	else:
		return redirect(url_for('login'))


# Definisanje rute "export/<tip>"
@app.route("/export/<tip>" , methods = ['GET'])
@app.route("/export/<tip>/<studentId>" , methods = ['GET'])
def export(tip, studentId = -1):
	# Kreiranje rečnika koji kao ključeve sadrži tip koji je odabran za exportovanje
	switch = {
		"studenti" : "SELECT * FROM studenti",
		"korisnici" : "SELECT * FROM korisnici",
		"predmeti" : "SELECT * FROM predmeti",
		"ocene"   :  """ SELECT
					predmeti.sifra, predmeti.naziv, predmeti.godina_studija, predmeti.espb, predmeti.obavezni_izborni,ocene.ocena 
					FROM predmeti 
					INNER JOIN ocene
					ON predmeti.id = ocene.predmet_id
					WHERE ocene.student_id = {0} 
					 """.format(studentId)
				}

	# Selektovanje tipa i ujedno kreiranje upita ka bazi :
	upit = switch.get(tip)
	# Izvršenje upita :
	kursor.execute(upit)
	# Čuvanje rezultata dobijenih iz baze:
	rezultati = kursor.fetchall()

	# Definisanje izlazne putanje za export
	output = io.StringIO()
	# Defisanje writera za exportuje na definisanoj putanju
	writer = csv.writer(output)

	# Zapisivanje isčitanih podataka u csv fajl 
	for row in rezultati:
		red = []
		for value in row.values():
			red.append(str(value))
		writer.writerow(red)

	output.seek(0)

	# Vracanje fajla (Exportovanje)
	return Response(
			output,
			mimetype = 'text/csv',
			headers = {'Content-Disposition' : 'attachment;filename=' + tip + ".csv"}
			)



	











# pokretanje aplikacije na dnu fajla
app.run(debug=True)
