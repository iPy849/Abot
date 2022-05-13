import os
from sys import argv
from time import sleep
from abot import app


def create_db():
    """
    Crea una base de datos SQLite y la llena con los datos necesarios
    """
    open("abot.db", "w+").close()
    from abot import db
    from sqlalchemy import text

    db.create_all()
    for statement in open("insert_verbs.sql", "r").read().rstrip().split(";"):
        db.engine.execute(text(statement))


if __name__ == "__main__":

    if "--reset-db" in argv:
        from abot import db

        db.drop_all()
        create_db()

    # Create database if not exits
    if not os.path.exists("abot.db"):
        print("No se encontró la vase de datos.")
        print("Creando base de datos...")
        create_db()
        print("Base de datos creada con éxito!!!")

    app.run()
