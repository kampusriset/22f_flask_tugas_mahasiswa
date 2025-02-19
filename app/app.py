from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Konfigurasi MySQL untuk XAMPP
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tugas_db'
mysql = MySQL(app)

# Konfigurasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user[0], username=user[1])
    return None

# Route untuk halaman utama (dashboard)
@app.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tugas")
    tugas = cur.fetchall()
    cur.close()
    return render_template('index.html', tugas=tugas)

# Route untuk registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password, user[2].encode('utf-8')):
            user_obj = User(id=user[0], username=user[1])
            login_user(user_obj)
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!', 'error')
    return render_template('login.html')

# Route untuk logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# Route untuk menambah tugas
@app.route('/tambah', methods=['GET', 'POST'])
@login_required
def tambah_tugas():
    if request.method == 'POST':
        nama_tugas = request.form['nama_tugas']
        mata_kuliah = request.form['mata_kuliah']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tugas (nama_tugas, mata_kuliah) VALUES (%s, %s)", (nama_tugas, mata_kuliah))
        mysql.connection.commit()
        cur.close()

        flash('Tugas berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))
    return render_template('tambah.html')

# Route untuk update tugas
@app.route('/update/<int:id_tugas>', methods=['GET', 'POST'])
@login_required
def update_tugas(id_tugas):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tugas WHERE id_tugas = %s", (id_tugas,))
    tugas = cur.fetchone()
    cur.close()

    if not tugas:
        flash('Tugas tidak ditemukan!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        nama_tugas = request.form['nama_tugas']
        mata_kuliah = request.form['mata_kuliah']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE tugas SET nama_tugas = %s, mata_kuliah = %s WHERE id_tugas = %s", 
                    (nama_tugas, mata_kuliah, id_tugas))
        mysql.connection.commit()
        cur.close()

        flash('Tugas berhasil diupdate!', 'success')
        return redirect(url_for('index'))

    return render_template('update.html', tugas=tugas)

# Route untuk menghapus tugas
@app.route('/hapus/<int:id_tugas>')
@login_required
def hapus_tugas(id_tugas):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tugas WHERE id_tugas = %s", (id_tugas,))
    mysql.connection.commit()
    cur.close()

    flash('Tugas berhasil dihapus!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)