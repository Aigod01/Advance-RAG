"""
SQLAlchemy database models for structured enterprise data.
Matches blueprint specification: companies, products, customers, sales, regions.
"""
from datetime import date
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    Numeric,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(100), default="Technology")
    ticker = Column(String(20), nullable=True)

    sales = relationship("Sale", back_populates="company")


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    customers = relationship("Customer", back_populates="region_rel")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # 'Laptops', 'Desktops', 'Tablets', 'Accessories', 'Servers'
    unit_price = Column(Float, nullable=False, default=0.0)

    sales = relationship("Sale", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    region = Column(String(100), nullable=False)  # region name string for simple queries
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    segment = Column(String(100), default="Enterprise")  # 'Enterprise', 'SMB', 'Consumer'

    region_rel = relationship("Region", back_populates="customers")
    sales = relationship("Sale", back_populates="customer")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, default=1)
    sale_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)

    product = relationship("Product", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    company = relationship("Company", back_populates="sales")
