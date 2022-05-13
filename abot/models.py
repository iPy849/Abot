from abot import db


class SpanishVerbs(db.Model):
    conjugated_verb = db.Column(
        db.String(length=30), nullable=False, unique=True, primary_key=True
    )
    infinitive_verb = db.Column(db.String(length=30), nullable=False)


# TODO: Para más adelante hay que meter los json en una base de datos
