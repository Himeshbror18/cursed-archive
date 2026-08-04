#!/usr/bin/env python3
"""Download JJK images from Fandom wiki via MediaWiki API."""
import os, sys, time, json, subprocess, urllib.parse, urllib.request

DIR = "/home/himesh/Documents/pt2/jjk_panels"
os.makedirs(DIR, exist_ok=True)
MANIFEST = os.path.join(DIR, "manifest.txt")
API = "https://jujutsu-kaisen.fandom.com/api.php"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# slot -> (candidates list, output name)
slots = [
    (["Satoru_Gojo.png"], "gojo.png"),
    (["Satoru_Gojo's_cursed_energy.png"], "gojo_ce.png"),
    (["Yuji_Itadori.png"], "itadori.png"),
    (["Yuji_Itadori_(Anime).png"], "itadori_color.png"),
    (["Megumi_Fushiguro.png"], "megumi.png"),
    (["Nobara_Kugisaki.png"], "nobara.png"),
    (["Sukuna_(Anime).png", "Sukuna's_Demonic_Feretory.png"], "sukuna.png"),
    (["Toji_Fushiguro.png"], "toji.png"),
    (["Kento_Nanami.png"], "nanami.png"),
    (["Mahito_(Anime).png"], "mahito.png"),
    (["Geto_(Kaikai_Kitan).png", "Suguru_Geto's_Imposter.png"], "geto.png"),
    (["Unlimited_Void_(SpecialZ).png", "Unlimited_Void.gif"], "gojo_domain.png"),
    (["Malevolent_Shrine_(SpecialZ).png", "Malevolent_Shrine.gif"], "sukuna_domain.png"),
    (["Chimera_Shadow_Garden_inside_Horizon_of_the_Captivating_Skandha.png"], "megumi_domain.png"),
    (["Self-Embodiment_of_Perfection_(SpecialZ).png", "Mahito's_Domain_Expansion_of_0.2_seconds.png"], "mahito_domain.png"),
    (["Domain_Expansion_of_0.2_seconds.png"], "domain_hands.png"),
    (["Satoru_Gojo's_Black_Flash.png", "Satoru_Gojo's_cursed_energy.png"], "black_flash.png"),
    (["Shibuya.png", "Shibuya_(Anime).png"], "shibuya.png"),
    (["Shibuya_Map.png"], "shibuya_map.png"),
    (["Prison_Realm.png"], "prison_realm.png"),
    (["Riko_Amanai_(Anime).png", "Riko_Amanai.png"], "riko.png"),
    (["Divine_Dogs_(Anime).png", "Divine_Dogs.gif"], "divine_dogs.png"),
    (["Sukuna's_Finger.png"], "finger.png"),
    (["Cursed_Energy.png"], "cursed_energy.png"),
    (["Sukuna's_domain_destroys_Shinjuku.png"], "sukuna_rampage.png"),
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
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
        with open(outpath, "wb") as f:
            f.write(data)
        return len(data)
    except Exception as e:
        print(f"  download error: {e}")
        return 0

with open(MANIFEST, "w") as mf:
    for cands, out in slots:
        print(f"--- {out} ---")
        resolved = None
        for cand in cands:
            resolved = resolve_url(cand)
            if resolved:
                print(f"  found: {cand}")
                break
        if not resolved:
            print("  FAILED to resolve")
            mf.write(f"{out} || RESOLVE_FAILED\n")
            continue
        size = download(resolved, os.path.join(DIR, out))
        print(f"  SIZE:{size}")
        if size > 0:
            mf.write(f"{out} || {resolved}\n")
        time.sleep(0.4)

print("=== DONE ===")
for f in sorted(os.listdir(DIR)):
    if f != "manifest.txt":
        p = os.path.join(DIR, f)
        print(f"  {f}: {os.path.getsize(p)} bytes")