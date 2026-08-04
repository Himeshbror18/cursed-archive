#!/usr/bin/env python3
"""Download remaining JJK images - second pass with alternate names."""
import os, time, json, urllib.parse, urllib.request

DIR = "/home/himesh/Documents/pt2/jjk_panels"
API = "https://jujutsu-kaisen.fandom.com/api.php"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# Only the failed slots, with new candidates
slots = [
    (["Satoru_Gojo's_cursed_energy.png", "Gojo's_cursed_energy.png", "Gojo's_technique_disturbed_by_the_Black_Rope_(Anime).png"], "gojo_ce.png"),
    (["Yuji_Itadori_(Anime).png", "Yuji_Itadori_(Anime_2).png", "Yuji_Itadori_(Anime_3).png"], "itadori_color.png"),
    (["SukunaP_(Gray).png", "SukunaP.png", "Sukuna_(Anime).png", "Sukuna_(Anime_2).png"], "sukuna.png"),
    (["MahitoP_(Anime).png", "MahitoP.png", "Mahito_(Anime).png", "Mahito_(Anime_2).png"], "mahito.png"),
    (["GetoP.png", "Geto_(Kaikai_Kitan).png", "Suguru_Geto's_last_moments.png"], "geto.png"),
    (["Self-Embodiment_of_Perfection_(SpecialZ).png", "Mahito's_Self-Embodiment_of_Perfection.gif", "Mahito's_Domain_Expansion_of_0.2_seconds_.png", "Mahito's_Domain_Expansion_of_0.2_seconds.png"], "mahito_domain.png"),
    (["Satoru_Gojo's_Black_Flash.png", "Black_Flash!_-_JUJUTSU_KAISEN", "Gojo's_voltage_ramps_up.png", "Black_Bird_Manipulation.png"], "black_flash.png"),
    (["Sukuna's_Finger.png", "Sukuna's_fingers.png", "FingerBearerP.png"], "finger.png"),
    (["Sukuna's_domain_destroys_Shinjuku.png", "Shinjuku_(Anime).png"], "sukuna_rampage.png"),
]

def api_get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())

def resolve_url(filename):
    enc = urllib.parse.quote(filename)
    try:
        data = api_get({"action": "query", "titles": f"File:{enc}", "prop": "imageinfo", "iiprop": "url", "format": "json"})
        for page in data.get("query", {}).get("pages", {}).values():
            ii = page.get("imageinfo")
            if ii:
                return ii[0]["url"]
    except Exception as e:
        print(f"  resolve error {filename}: {e}")
    return None

def download(url, outpath):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://jujutsu-kaisen.fandom.com/"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(outpath, "wb") as f:
            f.write(data)
        return len(data)
    except Exception as e:
        print(f"  download error: {e}")
        return 0

with open(os.path.join(DIR, "manifest2.txt"), "w") as mf:
    for cands, out in slots:
        print(f"--- {out} ---")
        resolved = None
        for cand in cands:
            resolved = resolve_url(cand)
            if resolved:
                print(f"  found: {cand}")
                break
        if not resolved:
            print("  FAILED all candidates")
            mf.write(f"{out} || RESOLVE_FAILED\n")
            continue
        size = download(resolved, os.path.join(DIR, out))
        print(f"  SIZE:{size}")
        if size > 0:
            mf.write(f"{out} || {resolved}\n")
        time.sleep(0.4)

print("=== DONE ===")
for f in ["gojo_ce.png", "itadori_color.png", "sukuna.png", "mahito.png", "geto.png", "mahito_domain.png", "black_flash.png", "finger.png", "sukuna_rampage.png"]:
    p = os.path.join(DIR, f)
    print(f"  {f}: {os.path.getsize(p) if os.path.exists(p) else 'MISSING'} bytes")