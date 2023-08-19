import os 
import requests
from flask import Flask, render_template, redirect, session, request, flash, jsonify
from helps import login_required
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

engine = create_engine(os.getenv("DATABASE_URL"))
# Crea la conexion
db = scoped_session(sessionmaker(bind=engine))



app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/', methods=["GET", "POST"])
@login_required
def index():
        return render_template("index.html")

@app.route("/search", methods=["GET","POST"])
@login_required
def result():
    # Variables
    busq = request.form.get("Search")
    option = request.form.get("option")

    if request.method == "POST":

        consult = ('%' + busq + '%').title()
        foo = consult.title()
        print(foo)
    
        if not busq:
            flash("Write a search")
            return render_template("search.html")
        if not option:
            flash("Choose a option")
            return render_template("search.html")
        else: 
            if option == "Title":
                query = db.execute(text("SELECT Isbn , title, Author, Year From Book WHERE title LIKE :title"), 
                                {"title":foo})
                row = query.fetchall()
                print(row)

                if len(row) == 0:
                    flash("There is no recorded data that matches the given parameter")
                    return render_template("search.html")
                else: 
                    flash("Successful Search") 
                return render_template("result.html", busq = row)

            elif option == "Isbn":
                query = db.execute(text("SELECT Isbn , title, Author, Year From Book WHERE isbn LIKE :isbn"), 
                                {"isbn":foo})
                row = query.fetchall()
                if len(row) == 0:
                    flash("There is no recorded data that matches the given parameter")
                    return render_template("search.html")

                else: 
                    flash("Successful Search") 
                    return render_template("result.html", busq = row)
                

            elif option == "Year":
                query = db.execute(text("SELECT Isbn , title, Author, Year From Book WHERE year LIKE :year LIMIT 10"), 
                                {"year":foo})
                row = query.fetchall()
                if len(row) == 0:
                    flash("There is no recorded data that matches the given parameter")
                    return render_template("search.html")
                else:
                    flash("Successful Search") 
                    return render_template("result.html", busq = row)
    else:    
        return render_template("search.html")

        
@app.route ("/api",methods=["GET"])
def api():

    isbn = request.args.get("isbn")
    rques = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
    if rques.status_code != 200:
        return jsonify({'error': 'book not found'}),404
    else:
    #variables a retornar
        book_info = rques.json()
        print(book_info)
        books = db.execute(text("SELECT *FROM Book  WHERE isbn = :isbn"),{"isbn":isbn}).fetchall()
        #Para leer un arreglo recorrerlo con for xd 
        for books in books:
            Isbn = books[0]
            title = books[1] 
            author = books[2]
            year = books[3]

        if books is None:
            return jsonify({
            'Error': 'Libro no encontrado' 
        }
        )
        else:
            for book in book_info["items"]:
                puntuacion = book['volumeInfo']['averageRating']
                vistas =  book["volumeInfo"]["ratingsCount"]
            return jsonify({'title': title,
                    'author': author,
                    'year':year,
                    'isbn':Isbn,
                    'review_count':vistas,
                    'average_score':puntuacion
                    })


@app.route("/books/<isbn>" ,methods=["GET" ,"POST"])
@login_required
def book(isbn):   
            #Se Muestra el resultado del libro buscado 
    query_books = db.execute(text("SELECT *FROM Book WHERE isbn = :isbn"),{"isbn":isbn}).fetchone()
            #Se Muestran los comentarios a ese libro tomando como parametro el id del libro
    query_coment = db.execute(text("SELECT *FROM reviews JOIN Book ON books_Id = Isbn WHERE Isbn = :Isbn"),{"Isbn" :isbn})
    rows = query_coment.fetchall()
    verificar = db.execute(text("SELECT stars FROM reviews WHERE username =:username AND books_Id = :book_Id"),{"username":session["username"], "book_Id":isbn}).fetchall()
            
            #API de google books
    reques = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
    if reques.status_code != 200:
        return jsonify({'error': 'book not found'}),404
    book_info = reques.json()
    if book_info["totalItems"] == 0:
        flash("Libro no encontrado")  
        return render_template("result.html")
    print(book_info)
    print(reques.status_code)

            #Estrellas de usuarios
    y = 1
    coment_stars = []
    for row in verificar:
        while(y <= row[0]):
            y+=1  
            coment_stars.append(y)

    puntuacion = None
    if rows == None:
        flash("Isbn no encontrado")
        return render_template("result.html")

    dato = []
    for book in book_info["items"]:
        if 'averageRating' in book['volumeInfo'] or 'raitingsCount' in book['volumeInfo'] and 'imageLinks' in book['volumeInfo']:
            puntuacion = book['volumeInfo']['averageRating']
            vistas =  book["volumeInfo"]["ratingsCount"]
            img = book["volumeInfo"]["imageLinks"]["thumbnail"]
            des = book["volumeInfo"]["description"]
            user = session["username"]
            print(puntuacion)
            dato.append(puntuacion)
            dato.append(vistas)
            dato.append(des)
            dato.append(img)
            dato.append(user)

        
        #variables de la APi se agregan a un arreglo

        #Parte de los comentarios
    if request.method == 'POST':
        coment = request.form.get("comentario")    
        user = session["username"]
        stars = request.form.get("stars")

        verificar = db.execute(text("SELECT *From reviews WHERE username =:username"),{"username":session["username"]}).fetchone()
        print(verificar)
            
            #estrellas 
            #stars = []
        if not coment:
                flash("write a comment")
                return render_template("books.html", rows = rows, query_books = query_books, dato = dato, puntuacion = puntuacion, star=star,coment_stars= coment_stars)

        elif not stars:
                flash("Give a Score")
                return render_template("books.html", rows = rows, query_books = query_books, dato = dato, puntuacion = puntuacion, star=star,coment_stars= coment_stars)

        elif not stars and coment:    
                flash("Provide a comment and puntuation")
                return render_template("books.html", rows = rows, query_books = query_books, dato = dato, puntuacion = puntuacion, star=star,coment_stars= coment_stars)
            
        elif verificar != None and not stars:
                    flash("you have already commented")
                    return render_template("books.html", rows=rows, query_books=query_books, dato=dato, puntuacion=puntuacion, star=star, coment_stars=coment_stars)
        else:
            public_coment = db.execute(text("INSERT INTO reviews (username,comments, stars,books_id) VALUES(:username,:comments,:stars,:book_id)"),
                                                {"username": user, "comments": coment, "stars": stars, "book_id": isbn})
            db.commit()
            flash("Comment Posted Successfully")
            return redirect('/books/' + isbn)        
        
    star = []
    x = 1.0    
    if puntuacion is not None:
        while(x <= puntuacion):
                    estrellass = []
                    estrellass.append(x)
                    star.append(estrellass)
                    x+=1                   
                    return render_template("books.html", rows = rows, query_books = query_books, dato = dato, puntuacion = puntuacion, star=star,coment_stars= coment_stars)#Se muestra el resultado del libro buscado
    else: 
        puntuacion = 0.0
        while(x <= puntuacion):
                    estrellass = []
                    estrellass.append(x)
                    star.append(estrellass)
                    x+=1                   
                    return render_template("books.html", rows = rows, query_books = query_books, dato = dato, puntuacion = puntuacion, star=star,coment_stars= coment_stars)#Se muestra el resultado del libro buscad
    if len(dato) == 0: 
        print(dato)
        puntuacion = 'No rating available'
        vistas = "No ratings"
        flash("Book information is not accessible")
        return render_template("books.html", rows=rows,query_books = query_books, dato = dato,coment_stars = "None", star= star)

@app.route('/register', methods=["GET", "POST"])
def register():

    user = request.form.get("Username")
    passw = request.form.get("Password")
    confirm = request.form.get("PasswordConfirm")

    if request.method == "POST":
        if not user:
            flash("Provide a usser")
            return redirect("/register")
        if not passw:
            flash("Provide a Password")
            return redirect("/register")
        if passw != confirm:
            flash("Password do not much")
            return redirect("/register")
        
        query = db.execute(text("SELECT *FROM usser WHERE username = :username"),{"username" :user}).fetchone()
        if query == None:
            hash = generate_password_hash(passw)
            db.execute(text("INSERT INTO usser (username, password) VALUES(:username, :password)"), 
                    {"username" :user, "password":hash})
            db.commit()
            db.close()
            flash("Successful registration")
            return render_template("login.html")
        else:
            flash("El usuario ya esta registrado")
            return render_template("register.html")
    else:
        return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():

    session.clear()
    user = request.form.get("Username")
    passw = request.form.get("Password")

    if request.method == "POST":
        if not user:
            flash("Provide a User")
            return render_template("login.html")
        if not passw:
            flash("Provide a Password")
            return render_template("login.html")

    
        verificar = db.execute(text("SELECT *FROM usser WHERE  username = :username")
                            ,{"username":user})
            
        row = verificar.fetchone()
        if verificar == None:
            flash("User was not exist")
            return render_template("login.html")
        
        if row == None or not check_password_hash(row[2], passw):
            flash("User Or Password Invalid")
            return render_template("login.html")

        session["user_id"] = row[0]
        session["username"] = row[1]
        if row:
            flash("Login successful")
            return render_template("index.html", user = user)
        else:
            flash("User or Password Invalid")
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/logout")
def logiout():
    session.clear()
    flash("Session Cerrada")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
