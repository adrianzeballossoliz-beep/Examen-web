import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Configuración de base de datos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "Database", "landing_page_2.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # Datos del restaurante
    restaurante = conn.execute('SELECT * FROM restaurante LIMIT 1').fetchone()
    # Lista de platos
    menu = conn.execute('SELECT * FROM menu_almuerzo').fetchall()
    # Suma total de ganancias
    ganancias = conn.execute('SELECT SUM(precio_pagado) as total FROM pedidos').fetchone()
    # Lista de los últimos 5 pedidos realizados
    ultimos_pedidos = conn.execute('SELECT * FROM pedidos ORDER BY id DESC LIMIT 5').fetchall()
    conn.close()
    
    return render_template('index.html', 
                           restaurante=restaurante, 
                           menu=menu, 
                           ingresos=ganancias['total'] or 0,
                           pedidos=ultimos_pedidos)

@app.route('/realizar_pedido', methods=['POST'])
def realizar_pedido():
    # Esta es la versión completa con correo
    nombre_cliente = request.form['cliente']
    correo_cliente = request.form['correo'] 
    plato_id = request.form['plato_id']
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = get_db_connection()
    plato = conn.execute('SELECT nombre_plato, precio FROM menu_almuerzo WHERE id = ?', (plato_id,)).fetchone()
    
    if plato:
        # Añadimos 'correo_cliente' al INSERT
        conn.execute('''
            INSERT INTO pedidos (nombre_cliente, correo_cliente, plato_pedido, precio_pagado, fecha_pedido)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre_cliente, correo_cliente, plato['nombre_plato'], plato['precio'], fecha_hoy))
        conn.commit()
    
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Esto es para que funcione en tu PC (Local)
    app.run(debug=True, port=5000)