from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import sqlite3
import numpy as np
import pandas as pd
import os

app = FastAPI()

# Load Model ML (Pastikan model.pkl sudah ada di folder yang sama)
model = joblib.load('model.pkl')

# Setup Database SQLite (Tabel baru dengan Usia & Asal Wilayah)
def init_db():
    conn = sqlite3.connect('casis.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediksi_casis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT, usia INTEGER, asal_wilayah TEXT,
            lari REAL, pull_up INTEGER, push_up INTEGER,
            sit_up INTEGER, shuttle_run REAL, renang REAL,
            status TEXT, penempatan TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Schema Input dari Frontend
class CasisInput(BaseModel):
    nama: str
    usia: int
    asal_wilayah: str
    lari: float
    pull_up: int
    push_up: int
    sit_up: int
    shuttle_run: float
    renang: float

# Endpoint melayani halaman Frontend
@app.get("/")
def read_index():
    return FileResponse("index.html")

# Endpoint API Prediksi
@app.post("/api/predict")
def predict_casis(data: CasisInput):
    # Model ML HANYA menggunakan 6 data fisik, jadi Usia/Wilayah diabaikan untuk prediksi
    fitur = np.array([[data.lari, data.pull_up, data.push_up, data.sit_up, data.shuttle_run, data.renang]])
    prediksi = model.predict(fitur)[0]
    
    status = "LULUS" if prediksi == 1 else "TDK LULUS"
    penempatan = "BRIMOB" if status == "LULUS" else "STAFF"
    
    # Simpan semua data termasuk Usia & Wilayah ke Database
    conn = sqlite3.connect('casis.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO prediksi_casis 
        (nama, usia, asal_wilayah, lari, pull_up, push_up, sit_up, shuttle_run, renang, status, penempatan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.nama, data.usia, data.asal_wilayah, data.lari, data.pull_up, data.push_up, data.sit_up, data.shuttle_run, data.renang, status, penempatan))
    conn.commit()
    conn.close()
    
    return {"nama": data.nama, "status": status, "penempatan": penempatan}

# Endpoint Download Database ke Excel
@app.get("/api/download")
def download_excel():
    # Mengambil data dari SQLite
    conn = sqlite3.connect('casis.db')
    df = pd.read_sql_query("SELECT * FROM prediksi_casis", conn)
    conn.close()
    
    # Konversi ke Excel
    file_path = "Database_Casis.xlsx"
    df.to_excel(file_path, index=False)
    
    # Mengirim file ke pengguna
    return FileResponse(
        path=file_path, 
        filename="Database_Casis.xlsx", 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )