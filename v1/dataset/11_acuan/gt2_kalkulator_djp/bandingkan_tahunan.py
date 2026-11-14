r"""Bandingkan hasil formulir PPh 21 Tahunan (A1/A2) kalkulator DJP (hasil_tahunan.csv) dengan perhitungan masa terakhir GT3.

    env\Scripts\python dataset\11_acuan\gt2_kalkulator_djp\bandingkan_tahunan.py

Yang dibandingkan adalah baris yang dihitung kalkulator. Baris isian (gaji, biaya jabatan, iuran, zakat, PPh yang telah
dipotong) disalin dari GT3 lewat rencana_tahunan.csv, jadi tidak menguji apa pun dan tidak dibandingkan.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# baris formulir A1 -> kunci expected.tahunan di GT3
BARIS = {"b8": "bruto_setahun", "b13": "neto_setahun", "b16": "ptkp", "b17": "pkp", "b18": "pph21_setahun",
         "b20": "pph21_masa_terakhir"}

rencana = {x["gt2_id"]: x for x in csv.DictReader(open(HERE / "rencana_tahunan.csv", encoding="utf-8"))}
rows = []
for r in csv.DictReader(open(HERE / "hasil_tahunan.csv", encoding="utf-8")):
    gt3 = rencana[r["gt2_id"]]["sumber"].split()[0]
    t = json.loads((ROOT / f"dataset/11_acuan/gt3_kasus_bertingkat/{gt3}.json").read_text(encoding="utf-8"))["expected"]["tahunan"]
    for b, kunci in BARIS.items():
        selisih = int(r[b]) - int(t[kunci])
        rows.append({"gt2_id": r["gt2_id"], "acuan": gt3, "baris": b, "fakta": kunci, "djp": int(r[b]),
                     "gt3": int(t[kunci]), "selisih": selisih, "sama": selisih == 0,
                     "putusan": "" if selisih == 0 else "perlu diselidiki"})
with open(HERE / "perbandingan_tahunan.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
for g in dict.fromkeys(x["gt2_id"] for x in rows):
    beda = [x for x in rows if x["gt2_id"] == g and not x["sama"]]
    print(g, next(x["acuan"] for x in rows if x["gt2_id"] == g), "sama" if not beda else beda)
print(f"{sum(x['sama'] for x in rows)}/{len(rows)} angka sama, {len({x['gt2_id'] for x in rows})} kasus")
