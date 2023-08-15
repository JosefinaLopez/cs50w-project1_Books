-- Zona de Eliminacion--
DROP TABLE Book
DROP TABLE reviews
DROP TABLE Usser

--Zona de Creacion -- 
CREATE TABLE Book
(
    Isbn VARCHAR(30) PRIMARY KEY NOT NULL,
    title VARCHAR(100) NOT NULL,
    Author VARCHAR(70) NOT NULL,
    Year VARCHAR(4) NOT NULL
)

CREATE TABLE reviews
(
    Id SERIAL PRIMARY KEY NOT NULL,
    stars INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    books_Id VARCHAR(30) NOT NULL REFERENCES Book(Isbn)
)

CREATE TABLE usser
(
    Id SERIAL PRIMARY KEY NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR NOT NULL
)

--Zona de Vistas--
SELECT *FROM Book
SELECT *FROM reviews
SELECT *FROM usser
