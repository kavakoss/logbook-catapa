import requests
import calendar
from datetime import datetime, timedelta

print("=== AUTOMATION ISI LOGBOOK BINUS + EXTRA CATAPA ===")
print("Pastikan kamu sudah mengambil Cookie dari web Enrichment Binus dan Catapa.\n")

tahun = int(input("Masukkan Tahun (contoh: 2026): "))
bulan = int(input("Masukkan Bulan (1-12): "))
header_id = input("Masukkan LogBookHeaderID Binus: ").strip()
default_activity = input("Masukkan Default Activity (sebagai standar): ").strip()
default_description = input("Masukkan Default Description (sebagai standar): ").strip()
cookie_catapa = input("Masukkan Cookie Catapa (untuk ambil jam absen): ").strip()
cookie_binus = input("Masukkan Cookie enrichment Binus: ").strip()

skip_filled = input("Skip tanggal yang sudah terisi di Binus? (y/n) [y]: ").strip().lower()
if skip_filled == '': skip_filled = 'y'

print("\n--- Mengambil Data Absen dari Catapa ---")
start_date = datetime(tahun, bulan, 1)
last_day = calendar.monthrange(tahun, bulan)[1]
end_date = datetime(tahun, bulan, last_day)

query_start = (start_date - timedelta(days=1)).strftime("%Y-%m-%d")
query_end = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")

catapa_url = f"https://api-apps.catapa.com/timemanagement/employees/me/presence-records?query=(date%3E{query_start}%2Cdate%3C{query_end})&sort=timeUtc%2CASC&page=0&size=100"
catapa_headers = {
    "accept": "application/json, text/plain, */*",
    "cookie": cookie_catapa,
    "origin": "https://ess.catapa.com",
    "referer": "https://ess.catapa.com/",
    "tenant": "BCA",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

catapa_data = {}
res_catapa = requests.get(catapa_url, headers=catapa_headers)
if res_catapa.status_code == 200:
    records = res_catapa.json().get("content", [])
    for record in records:
        date_str = record.get("date")
        label = record.get("label")
        time_utc_str = record.get("time")
        try:
            dt = datetime.fromisoformat(time_utc_str.replace("Z", "+00:00"))
            time_formatted = dt.strftime("%I:%M %p").lower()
        except Exception:
            time_formatted = "-"
        
        if date_str not in catapa_data:
            catapa_data[date_str] = {"TIME_IN": "-", "TIME_OUT": "-"}
        catapa_data[date_str][label] = time_formatted
    print("Data Catapa berhasil ditarik!\n")
else:
    print(f"Gagal menarik data Catapa. Status: {res_catapa.status_code}. Harus isi jam manual.\n")

print("Mulai memproses absen Binus...")

url = "https://activity-enrichment.apps.binus.ac.id/LogBook/StudentSave"
url_get_logbook = "https://activity-enrichment.apps.binus.ac.id/LogBook/GetLogBook"

headers = {
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "cookie": cookie_binus,
    "origin": "https://activity-enrichment.apps.binus.ac.id",
    "referer": "https://activity-enrichment.apps.binus.ac.id/LearningPlan/StudentIndex",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

binus_data = {}
print("--- Mengambil Data LogBook Binus yang sudah ada ---")
res_binus = requests.post(url_get_logbook, headers=headers, data={"logBookHeaderID": header_id})
if res_binus.status_code == 200:
    try:
        binus_entries = res_binus.json().get("data", [])
        for entry in binus_entries:
            b_date = entry.get("date", "").split("T")[0]
            b_clockin = entry.get("clockIn", "")
            binus_data[b_date] = b_clockin
        print("Data Binus berhasil ditarik!\n")
    except Exception as e:
        print("Gagal parsing data Binus:", e)
else:
    print(f"Gagal menarik data Binus. Status: {res_binus.status_code}\n")

last_day = calendar.monthrange(tahun, bulan)[1]
berhasil = 0
dilewati = 0

for day in range(1, last_day + 1):
    current_date = datetime(tahun, bulan, day)
    date_str = current_date.strftime('%Y-%m-%d')
    date_formatted = current_date.strftime("%Y-%m-%dT00:00:00")
    
    if current_date.weekday() >= 5:
        print(f"Skipping {date_str} (Weekend)")
        dilewati += 1
        continue
        
    print(f"\n--- Mengisi untuk tanggal {date_str} ---")
    
    b_clockin = binus_data.get(date_str, "")
    if skip_filled == 'y' and b_clockin != "":
        print(f"Skipping {date_str} karena sudah terisi di Binus: {b_clockin}")
        dilewati += 1
        continue

    c_in = catapa_data.get(date_str, {}).get("TIME_IN", "-")
    c_out = catapa_data.get(date_str, {}).get("TIME_OUT", "-")
    
    is_off = 'n'
    if c_in == "-" and c_out == "-":
        is_off = input("Catapa kosong untuk hari ini. Apakah hari ini libur/tanggal merah (OFF)? (y/n) [n]: ").strip().lower()
    else:
        print("Data Catapa ditemukan. Berarti bukan tanggal merah.")
        
    if is_off == 'y':
        c_in = "OFF"
        c_out = "OFF"
        current_activity = "OFF"
        current_description = "OFF"
    else:
        if c_in == "-":
            c_in = input(f"Jam Clock In kosong dari Catapa. Masukkan manual (contoh: 08:30 am): ").strip()
        else:
            print(f"Clock In (Catapa): {c_in}")

        if c_out == "-":
            c_out = input(f"Jam Clock Out kosong dari Catapa. Masukkan manual (contoh: 05:30 pm): ").strip()
        else:
            print(f"Clock Out (Catapa): {c_out}")

        act_input = input(f"Activity [{default_activity}]: ").strip()
        desc_input = input(f"Description [{default_description}]: ").strip()
        
        current_activity = act_input if act_input else default_activity
        current_description = desc_input if desc_input else default_description
    
    payload = {
        "model[ID]": "00000000-0000-0000-0000-000000000000",
        "model[LogBookHeaderID]": header_id,
        "model[Date]": date_formatted,
        "model[Activity]": current_activity,
        "model[ClockIn]": c_in,
        "model[ClockOut]": c_out,
        "model[Description]": current_description,
        "model[flagjulyactive]": "false"
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            print(f"Berhasil mengisi LogBook untuk tanggal {current_date.strftime('%Y-%m-%d')}")
            berhasil += 1
        else:
            print(f"Gagal untuk tanggal {current_date.strftime('%Y-%m-%d')} | Status Code: {response.status_code}")
            
    except Exception as e:
        print(f"Terjadi error pada tanggal {current_date.strftime('%Y-%m-%d')}: {e}")

print("\n=== SELESAI ===")
print(f"Total berhasil diisi : {berhasil} hari")
print(f"Total dilewati (weekend/terisi) : {dilewati} hari")
