#!/bin/bash
# Download JJK images from Fandom wiki via MediaWiki API
set -e
DIR="/home/himesh/Documents/pt2/jjk_panels"
mkdir -p "$DIR"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
API="https://jujutsu-kaisen.fandom.com/api.php"
MANIFEST="$DIR/manifest.txt"
: > "$MANIFEST"

# slot -> "primary file" "fallback1" "fallback2" "output name"
slots=(
  "Satoru_Gojo.png" "" "" "gojo.png"
  "Satoru_Gojo's_cursed_energy.png" "" "" "gojo_ce.png"
  "Yuji_Itadori.png" "" "" "itadori.png"
  "Yuji_Itadori_(Anime).png" "" "" "itadori_color.png"
  "Megumi_Fushiguro.png" "" "" "megumi.png"
  "Nobara_Kugisaki.png" "" "" "nobara.png"
  "Sukuna_(Anime).png" "Sukuna's_Demonic_Feretory.png" "" "sukuna.png"
  "Toji_Fushiguro.png" "" "" "toji.png"
  "Kento_Nanami.png" "" "" "nanami.png"
  "Mahito_(Anime).png" "" "" "mahito.png"
  "Geto_(Kaikai_Kitan).png" "Suguru_Geto's_Imposter.png" "" "geto.png"
  "Unlimited_Void_(SpecialZ).png" "Unlimited_Void.gif" "" "gojo_domain.png"
  "Malevolent_Shrine_(SpecialZ).png" "Malevolent_Shrine.gif" "" "sukuna_domain.png"
  "Chimera_Shadow_Garden_inside_Horizon_of_the_Captivating_Skandha.png" "" "" "megumi_domain.png"
  "Self-Embodiment_of_Perfection_(SpecialZ).png" "Mahito's_Domain_Expansion_of_0.2_seconds.png" "" "mahito_domain.png"
  "Domain_Expansion_of_0.2_seconds.png" "" "" "domain_hands.png"
  "Satoru_Gojo's_Black_Flash.png" "" "" "black_flash.png"
  "Shibuya.png" "Shibuya_(Anime).png" "" "shibuya.png"
  "Shibuya_Map.png" "" "" "shibuya_map.png"
  "Prison_Realm.png" "" "" "prison_realm.png"
  "Riko_Amanai_(Anime).png" "Riko_Amanai.png" "" "riko.png"
  "Divine_Dogs_(Anime).png" "Divine_Dogs.gif" "" "divine_dogs.png"
  "Sukuna's_Finger.png" "" "" "finger.png"
  "Cursed_Energy.png" "" "" "cursed_energy.png"
  "Sukuna's_domain_destroys_Shinjuku.png" "" "" "sukuna_rampage.png"
)

resolve_url() {
  local file="$1"
  local encoded
  encoded=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$file")
  curl -s "$API?action=query&titles=File:$encoded&prop=imageinfo&iiprop=url&format=json" -H "User-Agent: $UA" --max-time 20 | jq -r '.query.pages[].imageinfo[0].url // empty' 2>/dev/null
}

download() {
  local url="$1" out="$2"
  curl -s -L "$url" \
    -H "User-Agent: $UA" \
    -H "Referer: https://jujutsu-kaisen.fandom.com/" \
    -o "$DIR/$out" --max-time 40 -w "%{http_code}" 2>/dev/null
}

for slot in "${slots[@]}"; do
  read -r primary fb1 fb2 out <<< "$slot"
  echo "--- $out ---"
  resolved=""
  for cand in "$primary" "$fb1" "$fb2"; do
    [ -z "$cand" ] && continue
    resolved=$(resolve_url "$cand")
    if [ -n "$resolved" ]; then
      echo "  found: $cand"
      break
    fi
  done
  if [ -z "$resolved" ]; then
    echo "  FAILED to resolve any candidate"
    echo "$out || RESOLVE_FAILED" >> "$MANIFEST"
    continue
  fi
  code=$(download "$resolved" "$out")
  size=$(wc -c < "$DIR/$out" 2>/dev/null || echo 0)
  ftype=$(file -b "$DIR/$out" 2>/dev/null | cut -c1-40)
  echo "  HTTP:$code SIZE:$size TYPE:$ftype"
  echo "$out || $resolved" >> "$MANIFEST"
  sleep 0.5
done

echo "=== DONE ==="
ls -la "$DIR"