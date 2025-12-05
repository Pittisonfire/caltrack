from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta

from app.core.database import get_db
from app.models.models import User, FoodEntry, WeightEntry, FavoriteFood
from app.services import openfoodfacts

router = APIRouter()


# ============ Pydantic Models ============

class UserCreate(BaseModel):
    name: str
    calorie_goal: int = 2000
    protein_goal: int = 150
    carb_goal: int = 200
    fat_goal: int = 65


class UserUpdate(BaseModel):
    calorie_goal: Optional[int] = None
    protein_goal: Optional[int] = None
    carb_goal: Optional[int] = None
    fat_goal: Optional[int] = None


class FoodEntryCreate(BaseModel):
    user_id: int
    date: date
    meal_type: str  # breakfast, lunch, dinner, snack
    name: str
    brand: Optional[str] = None
    barcode: Optional[str] = None
    serving_size: float = 100
    servings: float = 1
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    fiber: float = 0
    sugar: float = 0
    source: str = "manual"
    external_id: Optional[str] = None
    image_url: Optional[str] = None


class WeightEntryCreate(BaseModel):
    user_id: int
    date: date
    weight: float
    note: Optional[str] = None


class FavoriteFoodCreate(BaseModel):
    user_id: int
    name: str
    brand: Optional[str] = None
    barcode: Optional[str] = None
    calories_per_100g: float = 0
    protein_per_100g: float = 0
    carbs_per_100g: float = 0
    fat_per_100g: float = 0
    source: str = "openfoodfacts"
    external_id: Optional[str] = None
    image_url: Optional[str] = None


# ============ User Endpoints ============

@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).order_by(User.name).all()
    return users


@router.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user exists
    existing = db.query(User).filter(User.name == user.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user goals"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


# ============ Food Search Endpoints ============

@router.get("/food/search")
async def search_food(query: str, page: int = 1):
    """Search for food in Open Food Facts"""
    results = await openfoodfacts.search_food(query, page)
    return results


@router.get("/food/barcode/{barcode}")
async def get_food_by_barcode(barcode: str):
    """Get food by barcode"""
    product = await openfoodfacts.get_product_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ============ Food Entry Endpoints ============

@router.get("/entries/{user_id}")
async def get_food_entries(
    user_id: int, 
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get food entries for a user, optionally filtered by date range"""
    query = db.query(FoodEntry).filter(FoodEntry.user_id == user_id)
    
    if date_from:
        query = query.filter(FoodEntry.date >= date_from)
    if date_to:
        query = query.filter(FoodEntry.date <= date_to)
    
    entries = query.order_by(FoodEntry.date.desc(), FoodEntry.created_at.desc()).all()
    return entries


@router.get("/entries/{user_id}/day/{entry_date}")
async def get_daily_entries(user_id: int, entry_date: date, db: Session = Depends(get_db)):
    """Get all food entries for a specific day"""
    entries = db.query(FoodEntry).filter(
        FoodEntry.user_id == user_id,
        FoodEntry.date == entry_date
    ).order_by(FoodEntry.meal_type, FoodEntry.created_at).all()
    
    # Group by meal type
    grouped = {
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snack": []
    }
    
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    
    for entry in entries:
        meal_calories = entry.calories * entry.servings
        meal_protein = entry.protein * entry.servings
        meal_carbs = entry.carbs * entry.servings
        meal_fat = entry.fat * entry.servings
        
        grouped[entry.meal_type].append({
            **entry.__dict__,
            "total_calories": meal_calories,
            "total_protein": meal_protein,
            "total_carbs": meal_carbs,
            "total_fat": meal_fat
        })
        
        totals["calories"] += meal_calories
        totals["protein"] += meal_protein
        totals["carbs"] += meal_carbs
        totals["fat"] += meal_fat
    
    return {
        "date": entry_date,
        "meals": grouped,
        "totals": totals
    }


@router.post("/entries")
async def create_food_entry(entry: FoodEntryCreate, db: Session = Depends(get_db)):
    """Create a new food entry"""
    db_entry = FoodEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.put("/entries/{entry_id}")
async def update_food_entry(entry_id: int, servings: float, db: Session = Depends(get_db)):
    """Update food entry servings"""
    entry = db.query(FoodEntry).filter(FoodEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    entry.servings = servings
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/entries/{entry_id}")
async def delete_food_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a food entry"""
    entry = db.query(FoodEntry).filter(FoodEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db.delete(entry)
    db.commit()
    return {"status": "deleted"}


# ============ Statistics Endpoints ============

@router.get("/stats/{user_id}/week")
async def get_weekly_stats(user_id: int, start_date: Optional[date] = None, db: Session = Depends(get_db)):
    """Get weekly statistics"""
    if not start_date:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # Monday
    
    end_date = start_date + timedelta(days=6)
    
    entries = db.query(FoodEntry).filter(
        FoodEntry.user_id == user_id,
        FoodEntry.date >= start_date,
        FoodEntry.date <= end_date
    ).all()
    
    # Group by date
    daily_stats = {}
    for i in range(7):
        day = start_date + timedelta(days=i)
        daily_stats[day.isoformat()] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    
    for entry in entries:
        day_key = entry.date.isoformat()
        if day_key in daily_stats:
            daily_stats[day_key]["calories"] += entry.calories * entry.servings
            daily_stats[day_key]["protein"] += entry.protein * entry.servings
            daily_stats[day_key]["carbs"] += entry.carbs * entry.servings
            daily_stats[day_key]["fat"] += entry.fat * entry.servings
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "daily_stats": daily_stats
    }


# ============ Weight Endpoints ============

@router.get("/weight/{user_id}")
async def get_weight_entries(
    user_id: int, 
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """Get weight entries for a user"""
    entries = db.query(WeightEntry).filter(
        WeightEntry.user_id == user_id
    ).order_by(WeightEntry.date.desc()).limit(limit).all()
    return entries


@router.post("/weight")
async def create_weight_entry(entry: WeightEntryCreate, db: Session = Depends(get_db)):
    """Create or update weight entry for a date"""
    # Check if entry exists for this date
    existing = db.query(WeightEntry).filter(
        WeightEntry.user_id == entry.user_id,
        WeightEntry.date == entry.date
    ).first()
    
    if existing:
        existing.weight = entry.weight
        existing.note = entry.note
        db.commit()
        db.refresh(existing)
        return existing
    
    db_entry = WeightEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/weight/{entry_id}")
async def delete_weight_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a weight entry"""
    entry = db.query(WeightEntry).filter(WeightEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db.delete(entry)
    db.commit()
    return {"status": "deleted"}


# ============ Favorites Endpoints ============

@router.get("/favorites/{user_id}")
async def get_favorites(user_id: int, db: Session = Depends(get_db)):
    """Get favorite foods for a user"""
    favorites = db.query(FavoriteFood).filter(
        FavoriteFood.user_id == user_id
    ).order_by(FavoriteFood.name).all()
    return favorites


@router.post("/favorites")
async def add_favorite(favorite: FavoriteFoodCreate, db: Session = Depends(get_db)):
    """Add a food to favorites"""
    db_fav = FavoriteFood(**favorite.dict())
    db.add(db_fav)
    db.commit()
    db.refresh(db_fav)
    return db_fav


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(favorite_id: int, db: Session = Depends(get_db)):
    """Remove a food from favorites"""
    fav = db.query(FavoriteFood).filter(FavoriteFood.id == favorite_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(fav)
    db.commit()
    return {"status": "deleted"}
