from sqlalchemy import Column, Integer, String, Numeric, SmallInteger, Date, Text, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Modelos basados en la base de datos dvdrental de PostgreSQL

class Customer(Base):
    __tablename__ = "customer"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(SmallInteger, nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    email = Column(String(50))
    address_id = Column(SmallInteger, nullable=False)
    activebool = Column(Boolean, default=True)
    create_date = Column(Date, default=datetime.now)
    last_update = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    active = Column(Integer)
    
    rentals = relationship("Rental", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")

class Film(Base):
    __tablename__ = "film"
    
    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    release_year = Column(Integer)
    language_id = Column(SmallInteger, nullable=False)
    rental_duration = Column(SmallInteger, default=3)
    rental_rate = Column(Numeric(4, 2), default=4.99)
    length = Column(SmallInteger)
    replacement_cost = Column(Numeric(5, 2), default=19.99)
    rating = Column(String(10))
    last_update = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    special_features = Column(Text)
    fulltext = Column(Text)  # Campo tsvector en PostgreSQL
    
    inventory = relationship("Inventory", back_populates="film")

class Staff(Base):
    __tablename__ = "staff"
    
    staff_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    address_id = Column(SmallInteger, nullable=False)
    email = Column(String(50))
    store_id = Column(SmallInteger, nullable=False)
    active = Column(Boolean, default=True)
    username = Column(String(16), nullable=False)
    password = Column(String(40))
    last_update = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    picture = Column(Text)  # bytea en PostgreSQL
    
    rentals = relationship("Rental", back_populates="staff")
    payments = relationship("Payment", back_populates="staff")

class Inventory(Base):
    __tablename__ = "inventory"
    
    inventory_id = Column(Integer, primary_key=True, index=True)
    film_id = Column(Integer, ForeignKey("film.film_id"), nullable=False)
    store_id = Column(SmallInteger, nullable=False)
    last_update = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    film = relationship("Film", back_populates="inventory")
    rentals = relationship("Rental", back_populates="inventory")

class Rental(Base):
    __tablename__ = "rental"
    
    rental_id = Column(Integer, primary_key=True, index=True)
    rental_date = Column(TIMESTAMP, nullable=False, default=datetime.now)
    inventory_id = Column(Integer, ForeignKey("inventory.inventory_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    return_date = Column(TIMESTAMP)
    staff_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)
    last_update = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    
    customer = relationship("Customer", back_populates="rentals")
    staff = relationship("Staff", back_populates="rentals")
    inventory = relationship("Inventory", back_populates="rentals")
    payment = relationship("Payment", back_populates="rental", uselist=False)

class Payment(Base):
    __tablename__ = "payment"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)
    rental_id = Column(Integer, ForeignKey("rental.rental_id"))
    amount = Column(Numeric(5, 2), nullable=False)
    payment_date = Column(TIMESTAMP, nullable=False)
    
    customer = relationship("Customer", back_populates="payments")
    staff = relationship("Staff", back_populates="payments")
    rental = relationship("Rental", back_populates="payment")