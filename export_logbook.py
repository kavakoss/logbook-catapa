import requests
import csv
import re

print("=== BINUS LOGBOOK TO CSV EXPORTER ===")
print("Pastikan kamu sudah mengambil Cookie dari web Enrichment Binus.\n")

cookie_binus = input("Masukkan Cookie enrichment Binus: ").strip()
header_id = input("Masukkan LogBookHeaderID Binus: ").strip()
output_filename = input("Masukkan nama file hasil (contoh: logbook.csv) [logbook.csv]: ").strip()

if output_filename == '': 
    output_filename = 'logbook.csv'

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

print("\n--- Mengambil Data LogBook Binus ---")
try:
    res_binus = requests.post(url_get_logbook, headers=headers, data={"logBookHeaderID": header_id})

    if res_binus.status_code == 200:
        try:
            binus_entries = res_binus.json().get("data", [])
            
            if not binus_entries or binus_entries is None:
                print("Data kosong atau tidak ditemukan. Pastikan Cookie dan Header ID valid.")
            else:
                # Membuka file CSV untuk menulis data
                with open(output_filename, mode='w', newline='', encoding='utf-8') as csv_file:
                    # Menentukan header kolom CSV
                    fieldnames = ['Tanggal', 'ClockIn', 'ClockOut', 'Activity', 'Description', 'Acceptance', 'Status', 'CommentSS', 'CommentFS']
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    
                    baris_tercatat = 0
                    for entry in binus_entries:
                        raw_date = entry.get("date", "")
                        b_date = raw_date.split("T")[0] if "T" in raw_date else raw_date
                        
                        b_clockin = entry.get("clockIn") or entry.get("ClockIn") or ""
                        b_clockout = entry.get("clockOut") or entry.get("ClockOut") or ""
                        b_activity = entry.get("activity") or entry.get("Activity") or ""
                        b_desc = entry.get("description") or entry.get("Description") or ""
                        b_acceptance = entry.get("acceptance") or ""
                        b_acceptance_clean = re.sub(r'<[^>]+>', '', b_acceptance).strip()
                        b_status = entry.get("status") or ""
                        b_comments = entry.get("commentSS") or ""
                        b_commentfs = entry.get("commentFS") or ""
                        
                        writer.writerow({
                            'Tanggal': b_date,
                            'ClockIn': b_clockin,
                            'ClockOut': b_clockout,
                            'Activity': b_activity,
                            'Description': b_desc,
                            'Acceptance': b_acceptance_clean,
                            'Status': b_status,
                            'CommentSS': b_comments,
                            'CommentFS': b_commentfs
                        })
                        baris_tercatat += 1
                
                print(f"\nBerhasil! {baris_tercatat} baris data logbook telah disimpan ke '{output_filename}'.")
        except Exception as e:
            print("Gagal memproses/parsing data JSON dari Binus:", e)
    else:
        print(f"Gagal menarik data Binus. Status Code: {res_binus.status_code}")
        print("Response:", res_binus.text)

except Exception as e:
    print(f"Terjadi error sistem: {e}")

input("\nTekan Enter untuk keluar...")
