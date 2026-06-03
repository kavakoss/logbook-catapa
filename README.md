# Auto Logbook Binus x Catapa

Script automasi untuk mengisi LogBook *Enrichment* / Magang Binus secara otomatis dengan menarik riwayat absensi (Clock In / Clock Out) dari sistem *CATAPA*. Script ini dibuat menggunakan **Python**.

## Fitur Utama

- **Integrasi Langsung (API):** Melakukan request HTTP secara langsung, jauh lebih cepat daripada menggunakan bot UI (Selenium/Playwright).
- **Auto-Sync Waktu Absen:** Otomatis menarik jam *Clock In* dan *Clock Out* dari sistem Catapa dan menyesuaikannya dengan format Binus.
- **Smart Skip:** Dapat mendeteksi mana data yang **sudah terisi** di sistem Binus, sehingga akan otomatis di-*skip*.
- **Auto-Weekend & Holiday Checker:** Secara otomatis akan melewati (skip) hari Sabtu & Minggu. Jika tidak terdeteksi jam absen dari Catapa di hari kerja (Senin - Jumat), program akan bertanya apakah hari tersebut tanggal merah/libur, dan bisa di-autofill menjadi `OFF`.
- **Default Description & Activity:** Meminta isian (input) aktivitas default di awal. Pada saat *looping* untuk setiap harinya, kamu bisa menekan tombol `Enter` untuk memakai data default tersebut, atau mengetik jika deskripsi aktivitas hari itu berbeda.

## Prasyarat

- Terinstal **Python 3.x**.
- Memiliki *library* **Requests**.
  ```bash
  pip install requests
  ```

## Persiapan Data

Sebelum menjalankan script, pastikan Anda mendapatkan dua data penting ini:

1. **Cookie Catapa:** 
   - Login ke `https://ess.catapa.com/`. 
   - Inspect Element (F12) > `Network`. 
   - Filter `presence-records` > cari header `Cookie`. Copy seluruh nilainya. 
2. **Cookie Binus & LogBookHeaderID:**
   - Login ke `https://activity-enrichment.apps.binus.ac.id/`.
   - Inspect Element (F12) > `Network`. 
   - Buka tab bulan logbook yang mau diisi (misal bulan `May`).
   - Cari request API `GetLogBook` atau `StudentSave`.
   - Di tab *Headers*, cari `Cookie` dan copy.
   - Pada bagian *Request Payload* / *Form Data* dari request tersebut, perhatikan parameter `logBookHeaderID` atau `model[LogBookHeaderID]`. Copy ID unik (berbentuk UUID) tersebut.

## Cara Menjalankan

1. Clone atau download script ini.
2. Buka terminal (CMD / PowerShell / Bash).
3. Jalankan perintah:
   ```bash
   python isi_logbook_binus.py
   ```
4. Ikuti instruksi interaktif yang muncul di terminal (memasukkan Tahun, Bulan, Activity, Header ID, dan Cookie).
5. Tunggu proses *looping* selesai!

## Disclaimer
Proyek ini dibuat untuk tujuan edukasi (memahami cara kerja POST payload & API request via Python) demi mempermudah rutinitas logbook magang tanpa meniatkan penyalahgunaan data. Harap perhatikan kredensial session (*Cookie*) di-handle secara hati-hati oleh user. 

---
_Made by kavakoss_