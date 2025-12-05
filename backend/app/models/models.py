from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    calorie_goal = Column(Integer, default=2000)
    protein_goal = Column(Integer, default=150)  # grams
    carb_goal = Column(Integer, default=200)  # grams
    fat_goal = Column(Integer, default=65)  # grams
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    food_entries = relationship("FoodEntry", back_populates="user")
    weight_entries = relationship("WeightEntry", back_populates="user")


class FoodEntry(Base):
    __tablename__ = "food_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    
    # Food info
    name = Column(String(500), nullable=False)
    brand = Column(String(255), nullable=True)
    barcode = Column(String(50), nullable=True)
    
    # Serving
    serving_size = Column(Float, default=100)  # in grams
    servings = Column(Float, default=1)
    
    # Nutrition per serving
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)  # grams
    carbs = Column(Float, default=0)  # grams
    fat = Column(Float, default=0)  # grams
    fiber = Column(Float, default=0)  # grams
    sugar = Column(Float, default=0)  # grams
    
    # Source info
    source = Column(String(50), default="manual")  # openfoodfacts, manual, recipe
    external_id = Column(String(100), nullable=True)  # OpenFoodFacts ID or Recipe ID
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="food_entries")


class WeightEntry(Base):
    __tablename__ = "weight_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="weight_entries")


class FavoriteFood(Base):
    __tablename__ = "favorite_foods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Food info (cached from search)
    name = Column(String(500), nullable=False)
    brand = Column(String(255), nullable=True)
    barcode = Column(String(50), nullable=True)
    
    # Nutrition per 100g
    calories_per_100g = Column(Float, default=0)
    protein_per_100g = Column(Float, default=0)
    carbs_per_100g = Column(Float, default=0)
    fat_per_100g = Column(Float, default=0)
    
    source = Column(String(50), default="openfoodfacts")
    external_id = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
