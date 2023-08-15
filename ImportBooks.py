import csv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
load_dotenv()
# Pide la cadena de conexion
engine = create_engine(os.getenv("DATABASE_URL"))
# Crea la conexion
db = scoped_session(sessionmaker(bind=engine))

# Abre el archivo y lo recorre
with open('books.csv', 'r') as csvfile:
    # El lector omitira las , y las sustituira por el ""
    lector = csv.reader(csvfile)
    next(lector)

    print('iniciando')
    cont = 0
    # recorre con el ciclo form los elementos del lector
    for isbn, title, author, year in lector:
        # los inserta en la tabla
            db.execute(text("INSERT INTO Book (Isbn, title,author,year) VALUES (:Isbn,:Title,:Author,:Year)"), {
                        "Isbn": isbn, "Title": title, "Author": author, "Year": year})
            print(title)
    # Se envia a la BD
            db.commit()
            cont+=1
    print("Tarea Completada Exitosamente")        
    db.close()
