from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import database
import models

app = FastAPI(title="DVD Rental System - PostgreSQL")

# Configurar CORS para el frontend web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas Pydantic
class CustomerResponse(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: Optional[str]
    
    class Config:
        from_attributes = True

class FilmResponse(BaseModel):
    film_id: int
    title: str
    description: Optional[str]
    release_year: Optional[int]
    rental_rate: float
    rental_duration: int
    
    class Config:
        from_attributes = True

class StaffResponse(BaseModel):
    staff_id: int
    first_name: str
    last_name: str
    email: Optional[str]
    
    class Config:
        from_attributes = True

class RentalCreate(BaseModel):
    customer_id: int
    film_id: int
    staff_id: int
    days: int = 3

class RentalResponse(BaseModel):
    rental_id: int
    rental_date: datetime
    customer_id: int
    staff_id: int
    return_date: Optional[datetime]
    
    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health Check
@app.get("/")
def root():
    return {"message": "DVD Rental System API - PostgreSQL", "status": "running", "database": "dvdrental"}

# === ENDPOINTS DE CLIENTES ===
@app.get("/customers", response_model=List[CustomerResponse])
def get_customers(limit: int = 50, db: Session = Depends(get_db)):
    """Obtiene la lista de clientes"""
    customers = db.query(models.Customer).filter(
        models.Customer.active == 1
    ).limit(limit).all()
    return customers

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Obtiene un cliente específico"""
    customer = db.query(models.Customer).filter(
        models.Customer.customer_id == customer_id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer

# === ENDPOINTS DE PELÍCULAS (DVDs) ===
@app.get("/films", response_model=List[FilmResponse])
def get_films(limit: int = 50, db: Session = Depends(get_db)):
    """Obtiene el catálogo de películas"""
    films = db.query(models.Film).limit(limit).all()
    return films

@app.get("/films/{film_id}", response_model=FilmResponse)
def get_film(film_id: int, db: Session = Depends(get_db)):
    """Obtiene una película específica"""
    film = db.query(models.Film).filter(models.Film.film_id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return film

@app.get("/films/{film_id}/availability")
def get_film_availability(film_id: int, db: Session = Depends(get_db)):
    """Verifica disponibilidad de copias de una película"""
    # Total de copias en inventario
    total_copies = db.query(func.count(models.Inventory.inventory_id)).filter(
        models.Inventory.film_id == film_id
    ).scalar()
    
    # Copias actualmente rentadas (no devueltas)
    rented_copies = db.query(func.count(models.Rental.rental_id)).join(
        models.Inventory
    ).filter(
        and_(
            models.Inventory.film_id == film_id,
            models.Rental.return_date.is_(None)
        )
    ).scalar()
    
    available = total_copies - rented_copies
    
    return {
        "film_id": film_id,
        "total_copies": total_copies,
        "rented_copies": rented_copies,
        "available_copies": available
    }

# === ENDPOINTS DE STAFF ===
@app.get("/staff", response_model=List[StaffResponse])
def get_staff(db: Session = Depends(get_db)):
    """Obtiene la lista de personal"""
    staff = db.query(models.Staff).filter(models.Staff.active == True).all()
    return staff

# === ENDPOINT PRINCIPAL: RENTAR DVD ===
@app.post("/rentals", response_model=RentalResponse)
def create_rental(rental: RentalCreate, db: Session = Depends(get_db)):
    """Crea una nueva renta de DVD"""
    
    # Verificar que el cliente exista y esté activo
    customer = db.query(models.Customer).filter(
        models.Customer.customer_id == rental.customer_id,
        models.Customer.active == 1
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o inactivo")
    
    # Verificar que el staff exista
    staff = db.query(models.Staff).filter(
        models.Staff.staff_id == rental.staff_id
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Personal no encontrado")
    
    # Verificar que la película exista
    film = db.query(models.Film).filter(
        models.Film.film_id == rental.film_id
    ).first()
    if not film:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    # Buscar una copia disponible en inventario
    available_inventory = db.query(models.Inventory).filter(
        models.Inventory.film_id == rental.film_id
    ).outerjoin(
        models.Rental,
        and_(
            models.Rental.inventory_id == models.Inventory.inventory_id,
            models.Rental.return_date.is_(None)
        )
    ).filter(
        models.Rental.rental_id.is_(None)
    ).first()
    
    if not available_inventory:
        raise HTTPException(status_code=400, detail="No hay copias disponibles de esta película")
    
    # Crear la renta
    new_rental = models.Rental(
        rental_date=datetime.now(),
        inventory_id=available_inventory.inventory_id,
        customer_id=rental.customer_id,
        staff_id=rental.staff_id,
        return_date=None
    )
    
    db.add(new_rental)
    db.flush()  # Para obtener el rental_id
    
    # Crear el pago
    payment = models.Payment(
        customer_id=rental.customer_id,
        staff_id=rental.staff_id,
        rental_id=new_rental.rental_id,
        amount=film.rental_rate,
        payment_date=datetime.now()
    )
    
    db.add(payment)
    db.commit()
    db.refresh(new_rental)
    
    return new_rental

# === ENDPOINT: DEVOLVER DVD ===
@app.put("/rentals/{rental_id}/return", response_model=RentalResponse)
def return_rental(rental_id: int, db: Session = Depends(get_db)):
    """Marca una renta como devuelta"""
    
    rental = db.query(models.Rental).filter(
        models.Rental.rental_id == rental_id
    ).first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="Renta no encontrada")
    
    if rental.return_date is not None:
        raise HTTPException(status_code=400, detail="Esta renta ya fue devuelta")
    
    # Actualizar fecha de devolución
    rental.return_date = datetime.now()
    rental.last_update = datetime.now()
    
    db.commit()
    db.refresh(rental)
    
    return rental

# === ENDPOINT: CANCELAR RENTA ===
@app.delete("/rentals/{rental_id}")
def cancel_rental(rental_id: int, db: Session = Depends(get_db)):
    """Cancela una renta (solo si no ha sido devuelta)"""
    
    rental = db.query(models.Rental).filter(
        models.Rental.rental_id == rental_id
    ).first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="Renta no encontrada")
    
    if rental.return_date is not None:
        raise HTTPException(status_code=400, detail="No se puede cancelar una renta ya devuelta")
    
    # Eliminar el pago asociado si existe
    payment = db.query(models.Payment).filter(
        models.Payment.rental_id == rental_id
    ).first()
    if payment:
        db.delete(payment)
    
    # Eliminar la renta
    db.delete(rental)
    db.commit()
    
    return {"message": "Renta cancelada exitosamente", "rental_id": rental_id}

# === REPORTE 1: Rentas de un cliente ===
@app.get("/reports/customer/{customer_id}")
def get_customer_rentals(customer_id: int, db: Session = Depends(get_db)):
    """Obtiene todas las rentas de un cliente específico"""
    
    customer = db.query(models.Customer).filter(
        models.Customer.customer_id == customer_id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    rentals = db.query(models.Rental).filter(
        models.Rental.customer_id == customer_id
    ).all()
    
    result = []
    for rental in rentals:
        inventory = db.query(models.Inventory).filter(
            models.Inventory.inventory_id == rental.inventory_id
        ).first()
        film = db.query(models.Film).filter(
            models.Film.film_id == inventory.film_id
        ).first()
        payment = db.query(models.Payment).filter(
            models.Payment.rental_id == rental.rental_id
        ).first()
        
        result.append({
            "rental_id": rental.rental_id,
            "film_title": film.title,
            "rental_date": rental.rental_date,
            "return_date": rental.return_date,
            "status": "DEVUELTO" if rental.return_date else "ACTIVO",
            "amount": float(payment.amount) if payment else 0.0
        })
    
    return {
        "customer_name": f"{customer.first_name} {customer.last_name}",
        "customer_email": customer.email,
        "total_rentals": len(result),
        "rentals": result
    }

# === REPORTE 2: DVDs no devueltos ===
@app.get("/reports/unreturned")
def get_unreturned_dvds(db: Session = Depends(get_db)):
    """Obtiene todas las rentas activas (no devueltas)"""
    
    unreturned = db.query(models.Rental).filter(
        models.Rental.return_date.is_(None)
    ).all()
    
    result = []
    for rental in unreturned:
        customer = db.query(models.Customer).filter(
            models.Customer.customer_id == rental.customer_id
        ).first()
        inventory = db.query(models.Inventory).filter(
            models.Inventory.inventory_id == rental.inventory_id
        ).first()
        film = db.query(models.Film).filter(
            models.Film.film_id == inventory.film_id
        ).first()
        
        days_rented = (datetime.now() - rental.rental_date).days
        expected_return = rental.rental_date + timedelta(days=film.rental_duration)
        days_late = max(0, (datetime.now() - expected_return).days)
        
        result.append({
            "rental_id": rental.rental_id,
            "film_title": film.title,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "rental_date": rental.rental_date,
            "expected_return_date": expected_return,
            "days_rented": days_rented,
            "days_late": days_late
        })
    
    return {
        "total_unreturned": len(result),
        "rentals": result
    }

# === REPORTE 3: DVDs más rentados ===
@app.get("/reports/most-rented")
def get_most_rented_films(limit: int = 10, db: Session = Depends(get_db)):
    """Obtiene las películas más rentadas"""
    
    most_rented = db.query(
        models.Film.film_id,
        models.Film.title,
        models.Film.release_year,
        func.count(models.Rental.rental_id).label("rental_count")
    ).join(
        models.Inventory, models.Inventory.film_id == models.Film.film_id
    ).join(
        models.Rental, models.Rental.inventory_id == models.Inventory.inventory_id
    ).group_by(
        models.Film.film_id
    ).order_by(
        func.count(models.Rental.rental_id).desc()
    ).limit(limit).all()
    
    result = []
    for film_id, title, year, count in most_rented:
        result.append({
            "film_id": film_id,
            "title": title,
            "release_year": year,
            "rental_count": count
        })
    
    return {
        "total_films": len(result),
        "films": result
    }

# === REPORTE 4: Ganancias por staff ===
@app.get("/reports/staff-earnings")
def get_staff_earnings(db: Session = Depends(get_db)):
    """Obtiene las ganancias generadas por cada miembro del staff"""
    
    earnings = db.query(
        models.Staff.staff_id,
        models.Staff.first_name,
        models.Staff.last_name,
        func.count(models.Payment.payment_id).label("total_transactions"),
        func.sum(models.Payment.amount).label("total_earnings")
    ).join(
        models.Payment, models.Payment.staff_id == models.Staff.staff_id
    ).group_by(
        models.Staff.staff_id
    ).all()
    
    result = []
    for staff_id, first_name, last_name, transactions, total in earnings:
        result.append({
            "staff_id": staff_id,
            "staff_name": f"{first_name} {last_name}",
            "total_transactions": transactions,
            "total_earnings": float(total) if total else 0.0
        })
    
    return {
        "total_staff": len(result),
        "staff": result
    }

# === ENDPOINT ADICIONAL: Obtener todas las rentas ===
@app.get("/rentals")
def get_rentals(limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene lista de rentas recientes"""
    rentals = db.query(models.Rental).order_by(
        models.Rental.rental_date.desc()
    ).limit(limit).all()
    
    result = []
    for rental in rentals:
        customer = db.query(models.Customer).filter(
            models.Customer.customer_id == rental.customer_id
        ).first()
        inventory = db.query(models.Inventory).filter(
            models.Inventory.inventory_id == rental.inventory_id
        ).first()
        film = db.query(models.Film).filter(
            models.Film.film_id == inventory.film_id
        ).first()
        
        result.append({
            "rental_id": rental.rental_id,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "film_title": film.title,
            "rental_date": rental.rental_date,
            "return_date": rental.return_date,
            "status": "DEVUELTO" if rental.return_date else "ACTIVO"
        })
    
    return result