from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
from sqlalchemy.types import Enum as SQLAEnum

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_pengguna = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    profile_pic = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'pemilik' atau 'karyawan'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    harga_beli = db.Column(db.Float, nullable=False)
    harga_jual = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('users', lazy=True))

    __table_args__ = (
        db.CheckConstraint('harga_jual >= 0', name='check_harga_jual_nonnegative'),
        db.CheckConstraint('stock >= 0', name='check_stock_nonnegative'),
    )

class JenisTransaksi(Enum):
    PENJUALAN = 'penjualan'
    PEMBELIAN = 'pembelian'

class Transaksi(db.Model):
    __tablename__ = 'transaksi'

    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date, nullable=False)
    total_harga = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    user = db.relationship('User', backref=db.backref('transaksis', lazy=True))
    jenis = db.Column(SQLAEnum(JenisTransaksi), nullable=False)

class DetailTransaksi(db.Model):
    __tablename__ = 'detail_transaksi'

    id = db.Column(db.Integer, primary_key=True)
    transaksi_id = db.Column(db.Integer, db.ForeignKey('transaksi.id'), nullable=False, index=True)
    transaksi = db.relationship('Transaksi', backref=db.backref('details', lazy=True))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    product = db.relationship('Product', backref=db.backref('details', lazy=True))
    jumlah = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.CheckConstraint('jumlah >= 0', name='check_jumlah_nonnegative'),
        db.CheckConstraint('subtotal >= 0', name='check_subtotal_nonnegative'),
    )
