from sqlalchemy import Column, Integer, String, Float, PickleType, Boolean, JSON, ForeignKey, LargeBinary
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
import os

db_url = os.getenv("DB_URL")

Base = declarative_base()

# Disabling same thread checking for different users being able to watch all products
# engine = create_engine('sqlite:///db.sqlite?check_same_thread=False',echo=False)

engine = create_engine(db_url,echo=False,pool_pre_ping=True)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer)
    carrito = relationship('Deseo')
    nombre = Column(String)
    alias = Column(String)
    baneado = Column(Boolean)
    admin = Column(Boolean)

    def __repr__(self):
        return f'''```
Usuario -> {self.nombre}
Alias -> @{self.alias}
T_id -> {self.tg_id}
Ban -> {self.baneado}
Admin -> {self.admin}
        ```'''

    @classmethod
    def limpiar_carrito(self):
        self.carrito = []

class Producto(Base):
    __tablename__ = 'producto'

    id = Column(Integer, unique=True ,primary_key=True)
    nombre = Column(String)
    detalles = Column(String)
    precio = Column(Integer)
    categoria = Column(String)
    imagen = Column(String)
    deseado = relationship("Deseo",back_populates="producto",cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Producto: {self.nombre} , {self.detalles} , {self.precio}, {self.categoria}>'


class Deseo(Base):
    __tablename__ = 'deseo'

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('user.id'))
    id_producto = Column(Integer,ForeignKey('producto.id'))
    producto = relationship("Producto",back_populates="deseado")
    cantidad = Column(Integer)

    def __repr__(self):
        return f'<Deseo: {self.id} , {self.user_id} , {self.cantidad}>'

class Utils(Base):
    __tablename__ = 'utils'

    id = Column(Integer,primary_key = True)
    categorias=Column(String)
    dev = Column(Integer)
    p_mostrados = Column(Integer)
    owner = Column(Integer)
    image_secs = Column(String)
    response_waiting = Column(Integer)

    def __repr__(self):
        return f'<Utils: {self.id} , {self.categorias} , {self.dev} , {self.p_mostrados} , {self.owner}>'

Session = scoped_session(sessionmaker(bind=engine))

Base.metadata.create_all(engine)

session = Session()

session.close()
