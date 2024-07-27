from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta, date
from models import db, User,Product, Transaksi, DetailTransaksi, JenisTransaksi
from config import Config
from sqlalchemy import func, extract
import calendar
import json
import io
import pdfkit

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login berhasil!', 'success')
            return redirect(url_for('beranda'))
        else:
            flash('Login gagal. Periksa username dan password.', 'danger')
    
    return render_template('login.html')
  

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/beranda")
def beranda():
    if 'user_id' in session:
        today = date.today()
        daily_sales_query = db.session.query(func.sum(Transaksi.total_harga)).filter(
            Transaksi.tanggal == today, Transaksi.jenis == JenisTransaksi.PENJUALAN).scalar() or 0
        
        current_month = today.month
        monthly_sales_query = db.session.query(func.sum(Transaksi.total_harga)).filter(
            extract('month', Transaksi.tanggal) == current_month, Transaksi.jenis == JenisTransaksi.PENJUALAN).scalar() or 0

        recent_transactions = Transaksi.query.order_by(Transaksi.tanggal.desc()).limit(10).all()

        # Calculate the date 7 days ago from today
        start_date = today - timedelta(days=6)

        # Query for sales data from the last 7 days
        last_7_days_sales = db.session.query(
            Transaksi.tanggal,
            func.sum(Transaksi.total_harga).label('total')
        ).filter(
            Transaksi.tanggal >= start_date,
            Transaksi.tanggal <= today,
            Transaksi.jenis == JenisTransaksi.PENJUALAN
        ).group_by(Transaksi.tanggal).all()

        # Prepare data for the chart
        sales_chart_data = {
            "labels": [(start_date + timedelta(days=i)).strftime('%A') for i in range(7)],
            "data": [0] * 7
        }
        
        for sale in last_7_days_sales:
            day_index = (sale.tanggal - start_date).days
            sales_chart_data["data"][day_index] = sale.total

        return render_template('beranda.html',  
                           daily_sales=daily_sales_query, 
                           monthly_sales=monthly_sales_query, 
                           recent_transactions=recent_transactions,
                           sales_chart_data=sales_chart_data)
   
    return redirect(url_for('login'))


@app.route('/api/search_products')
def search_products():
    query = request.args.get('query')
    results = Product.query.filter(Product.name.like(f'%{query}%')).all()
    return jsonify([product.name for product in results])

#Transaksi
@app.route('/transaksi-list')
def transaksi_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    jenis = request.args.get('jenis', 'semua')
    if jenis == 'semua':
        transaksis = Transaksi.query.all()
    else:
        transaksis = Transaksi.query.filter_by(jenis=jenis).all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if the request is an AJAX request
        return render_template('transaksi/_transaksi_table.html', transaksis=transaksis)
    
    return render_template('transaksi/transaksi.html', transaksis=transaksis)

# @app.route('/transaksi-list')
# def transaksi_list():
#     if 'user_id' in session:
#         transaksis = Transaksi.query.all()
                    
#     return render_template('transaksi/transaksi.html', transaksis=transaksis)

@app.route('/transaksi_baru', methods=['GET', 'POST'])
def transaksi_baru():
    if request.method == 'POST':
        user_id = session.get('user_id')
        jenis = request.form['jenis']
        total_amount = 0
        tanggal = request.form.get('tanggal')

        if not user_id:
            flash('User tidak ditemukan. Silakan login ulang.', 'danger')
            return redirect(url_for('login'))
        
        if jenis == 'penjualan':
            try:
                transaksi = Transaksi(user_id=user_id, total_harga=total_amount, tanggal=tanggal, jenis=jenis)
                db.session.add(transaksi)
                db.session.flush()

                # Process products
                products = request.form.getlist('products[][product_id]')
                quantities = request.form.getlist('products[][quantity]')

                details = []
                for i in range(len(products)):
                    product_id = products[i]
                    quantity = quantities[i]

                    if not product_id or not quantity:
                        continue

                    product_id = int(product_id)
                    quantity = int(quantity)
                    product_obj = Product.query.get(product_id)
                    if not product_obj:
                        raise ValueError(f'Produk dengan ID {product_id} tidak ditemukan.')
                    if product_obj.stock < quantity:
                        raise ValueError(f'Stok produk {product_obj.name} tidak mencukupi.')

                    subtotal = product_obj.harga_jual * quantity
                    total_amount += subtotal

                    detail = DetailTransaksi(transaksi_id=transaksi.id, product_id=product_id, jumlah=quantity, subtotal=subtotal)
                    details.append(detail)
                    product_obj.stock -= quantity
                    db.session.add(product_obj)

                for detail in details:
                    db.session.add(detail)

                transaksi.total_harga = total_amount
                db.session.commit()

                flash('Transaksi berhasil ditambahkan!', 'success')
                return redirect(url_for('transaksi_list'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('transaksi_baru'))
            
        elif jenis == 'pembelian':
            try:
                transaksi = Transaksi(user_id=user_id, total_harga=total_amount, tanggal=tanggal, jenis=jenis)
                db.session.add(transaksi)
                db.session.flush()

                # Process products
                products = request.form.getlist('products[][product_id]')
                quantities = request.form.getlist('products[][quantity]')

                details = []
                for i in range(len(products)):
                    product_id = products[i]
                    quantity = quantities[i]

                    if not product_id or not quantity:
                        continue

                    product_id = int(product_id)
                    quantity = int(quantity)
                    product_obj = Product.query.get(product_id)
                    if not product_obj:
                        raise ValueError(f'Produk dengan ID {product_id} tidak ditemukan.')

                    subtotal = product_obj.harga_beli * quantity
                    total_amount += subtotal

                    detail = DetailTransaksi(transaksi_id=transaksi.id, product_id=product_id, jumlah=quantity, subtotal=subtotal)
                    details.append(detail)
                    product_obj.stock += quantity
                    db.session.add(product_obj)

                for detail in details:
                    db.session.add(detail)

                transaksi.total_harga = total_amount
                db.session.commit()

                flash('Transaksi berhasil ditambahkan!', 'success')
                return redirect(url_for('transaksi_list'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('transaksi_baru'))

    products = Product.query.all()
    return render_template('transaksi/transaksi_baru.html', products=products)

@app.route('/transaksi/<int:transaksi_id>', methods=['GET', 'POST'])
def transaksi_detail(transaksi_id):
    transaksi = Transaksi.query.get_or_404(transaksi_id)
    products = Product.query.all()
    details = transaksi.details
    return render_template('transaksi/detail_transaksi.html', transaksi=transaksi, details=details, products=products)

@app.route('/transaksi/edit/<int:detail_id>', methods=['GET', 'POST'])
def edit_detail(detail_id):
    detail = DetailTransaksi.query.get_or_404(detail_id)
    transaksi = Transaksi.query.get(detail.transaksi_id)
    jenis = transaksi.jenis.value
    user_id = session.get('user_id')

    user = User.query.get(user_id)

    if not user:
        flash('User tidak valid.', 'danger')
        return redirect(url_for('login'))

    original_jumlah = detail.jumlah
    product = Product.query.get(detail.product_id)

    if request.method == 'POST':
        if jenis == 'penjualan':
            try:
                new_jumlah = int(request.form['jumlah'])
                jumlah_diff = original_jumlah -new_jumlah
                detail.jumlah = new_jumlah
                detail.subtotal = product.harga_jual * new_jumlah
                product.stock += jumlah_diff
                transaksi.total_harga -= (jumlah_diff * product.harga_jual)

                db.session.commit()

                flash('Detail transaksi berhasil diperbarui!', 'success')
                return redirect(url_for('transaksi_detail', transaksi_id=detail.transaksi_id))

            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('edit_detail', detail_id=detail.id))

        elif jenis == 'pembelian':
            try:
                new_jumlah = int(request.form['jumlah'])
                jumlah_diff = original_jumlah -new_jumlah
                detail.jumlah = new_jumlah
                detail.subtotal = product.harga_beli * new_jumlah
                product.stock -= jumlah_diff
                transaksi.total_harga -= (jumlah_diff * product.harga_beli)

                db.session.commit()

                flash('Detail transaksi berhasil diperbarui!', 'success')
                return redirect(url_for('transaksi_detail', transaksi_id=detail.transaksi_id))

            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('edit_detail', detail_id=detail.id))

    return render_template('transaksi/edit_detail_transaksi.html', detail=detail, product=product)

@app.route('/transaksi/delete_detail/<int:detail_id>', methods=['POST'])
def delete_detail(detail_id):
    detail = DetailTransaksi.query.get_or_404(detail_id)
    transaksi = Transaksi.query.get(detail.transaksi_id)
    jenis = transaksi.jenis.value
    user_id = session.get('user_id')

    user = User.query.get(user_id)

    if not user:
        flash('User tidak valid.', 'danger')
        return redirect(url_for('login'))

    if jenis == 'penjualan':
        try:
            product = Product.query.get(detail.product_id)
            product.stock += detail.jumlah
            transaksi.total_harga -= detail.subtotal

            db.session.delete(detail)
            db.session.commit()

            flash('Detail transaksi berhasil dihapus!', 'success')
            return redirect(url_for('transaksi_detail', transaksi_id=detail.transaksi_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('transaksi_detail', transaksi_id=detail.transaksi_id))
    
    elif jenis == 'pembelian':
        try:
            product = Product.query.get(detail.product_id)
            product.stock -= detail.jumlah
            transaksi.total_harga -= detail.subtotal

            db.session.delete(detail)
            db.session.commit()

            flash('Detail transaksi berhasil dihapus!', 'success')
            return redirect(url_for('transaksi_detail', transaksi_id=detail.transaksi_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('transaksi_detail', transaksi_id=detail.transaksi_id))

@app.route('/transaksi/delete/<int:transaksi_id>', methods=['POST'])
def delete_transaksi(transaksi_id):
    transaksi = Transaksi.query.get_or_404(transaksi_id)
    jenis = transaksi.jenis.value
    user_id = session.get('user_id')

    user = User.query.get(user_id)

    if not user:
        flash('User tidak valid.', 'danger')
        return redirect(url_for('login'))

    if jenis == 'penjualan':
        try:
            # Return product stock to the original amount
            for detail in transaksi.details:
                product = Product.query.get(detail.product_id)
                product.stock += detail.jumlah
                db.session.delete(detail)
            
            db.session.delete(transaksi)
            db.session.commit()

            flash('Transaksi berhasil dihapus!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'danger')

        return redirect(url_for('transaksi_list'))
    
    elif jenis == 'pembelian':
        try:
            for detail in transaksi.details:
                product = Product.query.get(detail.product_id)
                if product:
                    product.stock -= detail.jumlah
                    db.session.delete(detail)
            
            db.session.delete(transaksi)
            db.session.commit()

            flash('Transaksi berhasil dihapus!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('transaksi_list'))

#Produk
@app.route('/product_search', methods=['GET'])
def product_search():
    query = request.args.get('q', '')
    if 'user_id' not in session:
        return jsonify([]), 403  # Return an empty list and forbidden status if user is not logged in

    user_id = session.get('user_id')
    
    user = User.query.get(user_id)
    if user:
        products = Product.query.filter(Product.name.ilike(f'%{query}%'), Product.user_id == user.id).all()
    else:
        return jsonify([]), 404  # User not found
    
    # else:
    #     User = User.query.filter_by(id=user_id).first()
    #     if User:
    #         products = Product.query.filter(Product.name.ilike(f'%{query}%'), Product.user_id == User.owner_id).all()
    #     else:
    #         return jsonify([]), 404  # User not found

    results = [
        {'id': product.id, 'name': product.name, 'stock': product.stock}
        for product in products
    ]
    return jsonify(results)

@app.route("/produk")
def produk():
    if 'user_id' in session:
        products = Product.query.all()

    return render_template('produk/produk.html', products=products)

@app.route('/product/new', methods=['GET', 'POST'])
def new_product():
    if 'role' in session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            harga_beli = float(request.form['harga_beli'])
            harga_jual = float(request.form['harga_jual'])
            category = request.form['category']
            image_file = request.files['image']
            if image_file.filename and image_file.filename != '':
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join('static/product_images', image_filename))
            else:
                alt_filename = 'static/product_images/product-default.png'
                image_filename = secure_filename(os.path.basename(alt_filename))

            # image_filename = secure_filename(image_file.filename)
            # image_file.save(os.path.join('static/product_images', image_filename))

            new_product = Product(name=name, description=description, harga_beli=harga_beli, harga_jual=harga_jual, category=category, image=image_filename, user_id=session['user_id'])
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('produk'))

    return render_template('produk/produk_baru.html')

@app.route('/suggest_categories', methods=['GET'])
def suggest_categories():
    query = request.args.get('query', '')
    if query:
        categories = db.session.query(Product.category).filter(Product.category.like(f'%{query}%')).distinct().all()
        categories = [category[0] for category in categories]
    else:
        categories = []
    return jsonify(categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('produk/detail_produk.html', product=product)

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            product.name = request.form['name']
            product.description = request.form['description']
            product.harga_beli = float(request.form['harga_beli'])
            product.harga_jual = float(request.form['harga_jual'])
            product.category = request.form['category']

            if 'image' in request.files:
                image_file = request.files['image']
                if image_file.filename != '':
                    image_filename = secure_filename(image_file.filename)
                    image_file.save(os.path.join('static/product_images', image_filename))
                    product.image = image_filename

            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('product_detail', product_id=product.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('edit_product', product_id=product.id))

    return render_template('produk/edit_produk.html', product=product)

@app.route('/product/delete/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    if request.method == 'POST':
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    return redirect(url_for('produk'))

@app.route('/search')
def search_product():
    query = request.args.get('query')
    products = Product.query.filter(Product.name.like(f'%{query}%')).all()
    
    return render_template('produk/produk.html', products=products)

#Pengaturan
@app.route('/pengaturan')
def pengaturan():
    user_id = session.get('user_id')
    if 'role' in session:
        if session['role'] == 'pemilik':
            user = User.query.get_or_404(user_id)
            user_id = user.id
            # Handle 'pemilik' role logic
        else:
            user = User.query.get_or_404(user_id)
            user_id = user.id
            # Handle other roles logic
        # Continue processing for settings based on user role
    else:
        # Handle case where 'role' is not set in session
        # This could be redirecting to a login page or displaying an error message
        return 'Role not found in session. Please log in.'

    # Additional logic for settings page
    return render_template('pengaturan/pengaturan.html', user=user)

@app.route('/ubah-password', methods=['GET', 'POST'])
def ubah_password():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    else:
        user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not check_password_hash(user.password, current_password):
            flash('Password saat ini salah!', 'danger')
        elif new_password != confirm_password:
            flash('Password baru tidak cocok!', 'danger')
        else:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return redirect(url_for('pengaturan'))

    return render_template('pengaturan/ubah_password.html', user=user)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user_id = session.get('user_id')
    if 'role' in session:
        user = User.query.get_or_404(user_id)
    else:
        return 'Role not found in session. Please log in.'

    return render_template('pengaturan/profile.html', user=user)

@app.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    user_id = session.get('user_id')
    if 'role' in session:
        user = User.query.get_or_404(user_id)
        if request.method == 'POST':
            user.nama_pengguna = request.form['nama_pengguna']
            user.username = request.form['username']
            user.email = request.form['email']
            user.phone = request.form['phone']
            if 'profile_pic' in request.files:
                image_file = request.files['profile_pic']
                if image_file.filename != '':
                    image_filename = secure_filename(image_file.filename)
                    image_file.save(os.path.join(app.config['FOLDER_PROFILE_P'], image_filename))
                    user.profile_pic = image_filename
            db.session.commit()
            flash('Profil diperbarui!', 'success')
            return redirect(url_for('profile', user_id=user.id))
    else:
        return 'Role not found in session. Please log in.'
    
    return render_template('pengaturan/edit_profile.html', user=user)

#User
@app.route('/daftar-karyawan')
def daftar_karyawan():
    if 'user_id' not in session or session['role'] != 'pemilik':
        return redirect(url_for('login'))
    karyawan = User.query.filter_by(role='karyawan').all()
    return render_template('karyawan/daftar_karyawan.html', karyawan=karyawan)

@app.route('/tambah-karyawan', methods=['GET', 'POST'])
def tambah_karyawan():
    if 'user_id' not in session or session['role'] != 'pemilik':
        return redirect(url_for('login'))
    if request.method == 'POST':
        nama_pengguna = request.form['namaK']
        username = request.form['usernameK']
        password = generate_password_hash(request.form['passwordK'])
        email = request.form['emailK']
        phone = request.form['phoneK']
        profile_pic = request.files['profile_pic_k']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username sudah digunakan.', 'warning')
            return redirect(url_for('tambah_karyawan'))

        if profile_pic.filename and profile_pic.filename != '':
            image_filename = secure_filename(profile_pic.filename)
            profile_pic.save(os.path.join(app.config['FOLDER_PROFILE_P'], image_filename))
        else:
            alt_filename = 'static/profile-pic/alt-pic.jpg'
            image_filename = secure_filename(os.path.basename(alt_filename))

        karyawan_baru = User(
            nama_pengguna=nama_pengguna,
            username=username, 
            password=password, 
            email=email, 
            phone=phone, 
            profile_pic=image_filename,
            role='karyawan'
        )
        db.session.add(karyawan_baru)
        db.session.commit()
        return redirect(url_for('daftar_karyawan'))
    return render_template('karyawan/tambah_karyawan.html')

@app.route('/detail-karyawan/<int:karyawan_id>')
def detail_karyawan(karyawan_id):
    karyawan = User.query.get_or_404(karyawan_id)
    return render_template('karyawan/detail_karyawan.html', karyawan=karyawan)

@app.route('/edit-karyawan/<int:karyawan_id>', methods=['GET', 'POST'])
def edit_karyawan(karyawan_id):
    if 'user_id' not in session or session['role'] != 'pemilik':
        return redirect(url_for('login'))
    
    karyawan = User.query.get_or_404(karyawan_id)

    if request.method == 'POST':
        new_username = request.form['usernameK']
        
        # Check if the new username is different from the current username
        if new_username != karyawan.username:
            # Check if the new username already exists in the database
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash('Username sudah digunakan.', 'warning')
                return redirect(url_for('edit_karyawan', karyawan_id=karyawan.id))
        
        karyawan.nama_pengguna = request.form['namaK']
        karyawan.username = request.form['usernameK']
        karyawan.email = request.form['emailK']
        karyawan.phone = request.form['phoneK']

        if 'profile_pic_k' in request.files:
            image_file = request.files['profile_pic_k']
            if image_file.filename != '':
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['FOLDER_PROFILE_P'], image_filename))
                karyawan.profile_pic = image_filename
                
        db.session.commit()
        return redirect(url_for('detail_karyawan', karyawan_id=karyawan.id))
    return render_template('karyawan/edit_data_karyawan.html', karyawan=karyawan)

@app.route('/hapus-karyawan/<int:karyawan_id>', methods=['GET', 'POST'])
def hapus_karyawan(karyawan_id):
    if 'user_id' not in session or session['role'] != 'pemilik':
        return redirect(url_for('login'))
    if request.method == 'POST':
        karyawan = User.query.get_or_404(karyawan_id)
        db.session.delete(karyawan)
        db.session.commit()
    return redirect(url_for('daftar_karyawan'))

@app.route('/laporan')
def laporan():
    today = date.today()
    
    # Daily and Monthly Sales
    daily_sales_query = db.session.query(func.sum(Transaksi.total_harga)).filter(
        Transaksi.tanggal == today, Transaksi.jenis == JenisTransaksi.PENJUALAN).scalar() or 0
    current_month = today.month
    monthly_sales_query = db.session.query(func.sum(Transaksi.total_harga)).filter(
        extract('month', Transaksi.tanggal) == current_month, Transaksi.jenis == JenisTransaksi.PENJUALAN).scalar() or 0

    # Total Sales and Total Purchases
    total_sales_query = db.session.query(func.sum(Transaksi.total_harga)).filter(
        Transaksi.jenis == JenisTransaksi.PENJUALAN).scalar() or 0
    total_purchases_query = db.session.query(func.sum(Transaksi.total_harga)).filter(
        Transaksi.jenis == JenisTransaksi.PEMBELIAN).scalar() or 0

    # Net Profit
    net_profit = total_sales_query - total_purchases_query

    # Recent Transactions
    recent_transactions = Transaksi.query.order_by(Transaksi.tanggal.desc()).limit(10).all()

    # Weekly Sales (Last 7 Days)
    end_of_week = today
    start_of_week = end_of_week - timedelta(days=6)
    weekly_sales = db.session.query(
        Transaksi.tanggal,
        func.sum(Transaksi.total_harga).label('total')
    ).filter(
        Transaksi.tanggal >= start_of_week,
        Transaksi.tanggal <= end_of_week,
        Transaksi.jenis == JenisTransaksi.PENJUALAN
    ).group_by(Transaksi.tanggal).all()

    weekly_sales_chart_data = {
        "labels": [(start_of_week + timedelta(days=i)).strftime('%A') for i in range(7)],
        "data": [0] * 7
    }
    
    for sale in weekly_sales:
        day_index = (sale.tanggal - start_of_week).days
        weekly_sales_chart_data["data"][day_index] = sale.total

    # Monthly Sales (Current Year)
    current_year = today.year
    monthly_sales = db.session.query(
        extract('month', Transaksi.tanggal).label('month'),
        func.sum(Transaksi.total_harga).label('total')
    ).filter(
        extract('year', Transaksi.tanggal) == current_year,
        Transaksi.jenis == JenisTransaksi.PENJUALAN
    ).group_by('month').all()

    monthly_sales_chart_data = {
        "labels": [calendar.month_name[i] for i in range(1, 13)],
        "data": [0] * 12
    }

    for sale in monthly_sales:
        month_index = int(sale.month) - 1
        monthly_sales_chart_data["data"][month_index] = sale.total

    return render_template('laporan.html', 
                           daily_sales=daily_sales_query, 
                           monthly_sales=monthly_sales_query, 
                           recent_transactions=recent_transactions,
                           weekly_sales_chart_data=weekly_sales_chart_data,
                           monthly_sales_chart_data=monthly_sales_chart_data,
                           total_sales=total_sales_query,
                           total_purchases=total_purchases_query,
                           net_profit=net_profit)

@app.route('/print_report')
def print_report():
    report_type = request.args.get('reportType')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    transactions_query = db.session.query(Transaksi).filter(
        Transaksi.tanggal >= start_date,
        Transaksi.tanggal <= end_date
    )

    if report_type == 'sales':
        transactions_query = transactions_query.filter(Transaksi.jenis == JenisTransaksi.PENJUALAN)
    elif report_type == 'purchases':
        transactions_query = transactions_query.filter(Transaksi.jenis == JenisTransaksi.PEMBELIAN)

    transactions = transactions_query.all()

    total_price = sum(transaksi.total_harga for transaksi in transactions)

    rendered = render_template('report.html', transactions=transactions, start_date=start_date, end_date=end_date, report_type=report_type, total_price=total_price)
    
    # Specify the path to wkhtmltopdf executable if needed
    path_to_wkhtmltopdf = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'  # Ensure this path is correct
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    # Define the path to save the PDF
    pdf_directory = 'static/pdf'
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)

    pdf_path = os.path.join(pdf_directory, 'report.pdf')
    pdfkit.from_string(rendered, pdf_path, configuration=config)
    
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name='report.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)

