import requests
import re
import sys
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# --- CONFIGURATIE ---
URL = 'https://www.gocomics.com/nonsequitur'
# Googlebot vermomming om de beveiligingsmuur te passeren
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

print(f"--- START SCRAPE: Non Sequitur ---")

# Stap 1: Haal de pagina op
try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    html = response.text
    print(f"SUCCES: Pagina geladen (Status {response.status_code})")
except Exception as e:
    print(f"FOUT: Verbinding mislukt. {e}")
    sys.exit(1)

# Stap 2: Zoek de unieke strip-ID
# We zoeken specifiek naar de 32-cijferige ID die in het asset-pad staat.
# Dit is de meest stabiele methode die ook bij je andere feeds werkt.
match = re.search(r'assets[\\\/]+([a-f0-9]{32})', html)

if match:
    asset_id = match.group(1)
    # Bouw de URL op met hoge kwaliteit parameters
    image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
    print(f"GEVONDEN ID: {asset_id}")
    print(f"GEGENEREERDE URL: {image_url}")
else:
    print("FOUT: Geen strip-ID gevonden in de broncode.")
    sys.exit(1)

# Stap 3: Bouw de RSS-feed
fg = FeedGenerator()
fg.id(URL)
fg.title('Non Sequitur')
fg.link(href=URL, rel='alternate')
fg.description('De dagelijkse Non Sequitur strip via GoComics.')
fg.language('en')

current_date = datetime.now(timezone.utc)
date_str = current_date.strftime("%Y-%m-%d")

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Non Sequitur - {date_str}')
fe.link(href=URL)
fe.pubDate(current_date)
# Afbeelding direct in de RSS reader tonen
fe.description(f'<img src="{image_url}" alt="Non Sequitur strip van {date_str}" />')

# Stap 4: Schrijf het XML-bestand weg
try:
    fg.rss_file('nonsequitur.xml', pretty=True)
    print("KLAAR: 'nonsequitur.xml' is succesvol aangemaakt.")
except Exception as e:
    print(f"FOUT bij wegschrijven XML: {e}")
    sys.exit(1)