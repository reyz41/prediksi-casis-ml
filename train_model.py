import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
import joblib
import sqlite3
from faker import Faker

fake = Faker('id_ID')

wilayah_list = [
    'Sumatra (Aceh)', 'Sumatra (Sumut)', 'Sumatra (Sumbar)', 'Jawa (Jateng)',
    'Jawa (Jatim)', 'Jawa (Jabar)', 'Kalimantan (Kaltim)', 'Sulawesi (Sulsel)', 'Papua'
]

# 1. Generate 1000 Data Dummy
data = []
for i in range(1000):
    nama = fake.name()
    usia = random.randint(18, 22)
    asal_wilayah = random.choice(wilayah_list)
    lari = random.randint(2600, 3200)
    pull_up = random.randint(8, 20)
    push_up = random.randint(25, 50)
    sit_up = random.randint(25, 50)
    shuttle_run = round(random.uniform(15.0, 19.5), 1)
    renang = round(random.uniform(25.0, 38.0), 1)
    
    if (lari >= 2800 and pull_up >= 12 and push_up >= 32 and 
        sit_up >= 35 and shuttle_run <= 18.0 and renang <= 35.0):
        label = 1
        status = "LULUS"
        penempatan = "BRIMOB"
    else:
        label = 0
        status = "TDK LULUS"
        penempatan = "STAFF"
        
    data.append([nama, usia, asal_wilayah, lari, pull_up, push_up, sit_up, shuttle_run, renang, label, status, penempatan])

df = pd.DataFrame(data, columns=['nama', 'usia', 'asal_wilayah', 'lari', 'pull_up', 'push_up', 'sit_up', 'shuttle_run', 'renang', 'label', 'status', 'penempatan'])

# 2. Simpan 1000 data ke SQLite Database
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

cursor.execute('DELETE FROM prediksi_casis')

for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO prediksi_casis 
        (nama, usia, asal_wilayah, lari, pull_up, push_up, sit_up, shuttle_run, renang, status, penempatan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['nama'], row['usia'], row['asal_wilayah'], row['lari'], row['pull_up'], row['push_up'], row['sit_up'], row['shuttle_run'], row['renang'], row['status'], row['penempatan']))

conn.commit()
conn.close()
print("SUKSES: 1000 Data Dummy berhasil dimasukkan ke casis.db!")

# 3. Latih Model ML
X = df[['lari', 'pull_up', 'push_up', 'sit_up', 'shuttle_run', 'renang']]
y = df['label']

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
joblib.dump(model, 'model.pkl')