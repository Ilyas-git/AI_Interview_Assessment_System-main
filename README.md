# AI Interview Assessment System

Sistem penilaian wawancara berbasis kecerdasan buatan (AI) yang menganalisis video respons wawancara menggunakan **Faster-Whisper (Speech-to-Text)** dan **Natural Language Processing (NLP)** untuk mengevaluasi *Clarity*, *Confidence*, dan *Technical Relevance*.

---

## ⚡ Cara Menjalankan via Terminal

Cukup jalankan satu perintah ini di terminal:

```powershell
python run.py
```

> **Apa yang dilakukan script ini secara otomatis?**
> 1. Mendeteksi virtual environment Python (`src/backend/venv`).
> 2. Menjalankan server backend FastAPI di port `8000`.
> 3. Menjalankan server frontend React Vite di port `5173`.
> 4. Menggabungkan log kedua server ke satu terminal secara rapi (*prefixed logging*).
> 5. Membuka browser secara otomatis ke `http://localhost:5173`.
> 6. Ketika Anda menekan **`Ctrl + C`**, kedua server akan dimatikan secara bersih.

---

## 🌐 Alamat Layanan
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)