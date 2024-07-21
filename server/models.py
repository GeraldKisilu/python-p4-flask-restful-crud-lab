from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user')

    @hybrid_property
    def password(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50', name='check_instructions_length'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Recipe {self.id}: {self.title}>'

class Plant(db.Model, SerializerMixin):
    __tablename__ = 'plants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_in_stock = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Plant {self.id}: {self.name}>'
