import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import os
import schedule
import matplotlib.pyplot as plt
import pandas as pd
import logging
import re
import json
import random

# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# List of User-Agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]


# Headers to mimic a browser
def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.minimx.fr/',
    }


# Base URL of the site
BASE_URL = 'https://www.minimx.fr/'

# List of category URLs
CATEGORY_URLS = [
    "https://www.minimx.fr/fr/419-motocross",
    "https://www.minimx.fr/fr/670-motocross-crz-erz",
    "https://www.minimx.fr/fr/782-les-electriques",
    "https://www.minimx.fr/fr/666-motocross-150cc",
    "https://www.minimx.fr/fr/667-motocross-250cc",
    "https://www.minimx.fr/fr/668-les-motocross-300cc",
    "https://www.minimx.fr/fr/736-les-motocross-450cc",
    "https://www.minimx.fr/fr/736-les-motocross-450cc",
    "https://www.minimx.fr/fr/100-dirt-bike-pit-bike-motocross",
    "https://www.minimx.fr/fr/476-les-mini-moto-electriques",
    "https://www.minimx.fr/fr/136-les-50cc-70cc-88cc-enfant-et-mini-rider",
    "https://www.minimx.fr/fr/749-les-110cc",
    "https://www.minimx.fr/fr/133-dirt-bike-125cc-lifan-yx",
    "https://www.minimx.fr/fr/135-dirt-bike-moteur-150cc-yx",
    "https://www.minimx.fr/fr/533-les-dirt-bike-et-pit-bike-160cc",
    "https://www.minimx.fr/fr/535-les-pit-bike-et-dirt-bike-190cc",
    "https://www.minimx.fr/fr/346-les-motocross-250cc",
    "https://www.minimx.fr/fr/629-les-motocross-300cc",
    "https://www.minimx.fr/fr/737-les-450cc",
    "https://www.minimx.fr/fr/3-dirt-bike-mini-mx?page=1",
    "https://www.minimx.fr/fr/327-taille-de-roue-grande-roue-dirt-bike",
    "https://www.minimx.fr/fr/328-dirt-bike-10-12-petites-roues",
    "https://www.minimx.fr/fr/329-dirt-bike-12-14-taille-standard",
    "https://www.minimx.fr/fr/330-dirt-bike-grandes-roues-14-arriere-et-17-avant",
    "https://www.minimx.fr/fr/334-motocross-16-19-grandes-roues",
    "https://www.minimx.fr/fr/519-motocross-18-21",
    "https://www.minimx.fr/3-dirt-bike-mini-mx/s-2/hauteur_de_selle-89_cm+83_cm",
    "https://www.minimx.fr/fr/392-vehicules-pocket-cross-et-pocket-electrique",
    "https://www.minimx.fr/fr/306-pocket-cross-thermique",
    "https://www.minimx.fr/fr/416-pocket-cross-electriques",
    "https://www.minimx.fr/fr/413-les-cylindrees-de-pocket-bike-thermique-et-electrique",
    "https://www.minimx.fr/fr/414-49cc-enfant-de-3-a-8ans",
    "https://www.minimx.fr/fr/739-60cc-enfant-de-6-a-12ans",
    "https://www.minimx.fr/fr/556-Pocket-Quad-Quad-Electrique-et-Quad-4-Temps",
    "https://www.minimx.fr/fr/557-pocket-quad-2-temps-pour-enfant",
    "https://www.minimx.fr/fr/558-quad-4-temps-pour-enfant",
    "https://www.minimx.fr/fr/559-quad-electriques-pour-enfant",
    "https://www.minimx.fr/fr/744-quad-adultes-a-partir-de-14-ans",
    "https://www.minimx.fr/fr/633-draisienne-electrique-pour-enfant",
    "https://www.minimx.fr/fr/829-electrique",
    "https://www.minimx.fr/fr/827-non-electrique",
    "https://www.minimx.fr/fr/636-pieces-detachees-pour-draisienne-crz",
    "https://www.minimx.fr/633-draisienne-electrique-pour-enfant/s-88/cylindree_puissance-500w_electrique",
    "https://www.minimx.fr/fr/631-voitures-electrique-pour-enfant",
    "https://www.minimx.fr/fr/632-voiture-electrique-buggy-4x4-pour-enfant",
    "https://www.minimx.fr/fr/649-quad-electrique-pour-enfant",
    "https://www.minimx.fr/fr/652-voiture-electrique-pour-enfant",
    "https://www.minimx.fr/fr/778-voiture-rc-telecommande-electrique",
    "https://www.minimx.fr/632-voiture-electrique-buggy-4x4-pour-enfant",
    "https://www.minimx.fr/fr/616-velo-electrique-ville-et-vtt",
    "https://www.minimx.fr/fr/617-velo-electrique-pliant-crz",
    "https://www.minimx.fr/fr/618-vtt-electrique",
    "https://www.minimx.fr/fr/619-vtc-electrique",
    "https://www.minimx.fr/fr/771-moto-dax-skyteam-homologue",
    "https://www.minimx.fr/fr/772-thermique-a-essencemoto-dax-skyteam-thermique-50cc-et-125cc",
    "https://www.minimx.fr/fr/773-electrique",
    "https://www.minimx.fr/fr/785-pieces-detachees-dax-skyteam",
    "https://www.minimx.fr/index.php?id_product=12584&controller=product&id_lang=2",
    "https://www.minimx.fr/fr/419-motocross",
    "https://www.minimx.fr/fr/665-motocross-par-cylindree",
    "https://www.minimx.fr/fr/670-motocross-crz-erz",
    "https://www.minimx.fr/fr/782-les-electriques",
    "https://www.minimx.fr/fr/666-motocross-150cc",
    "https://www.minimx.fr/fr/667-motocross-250cc",
    "https://www.minimx.fr/fr/668-les-motocross-300cc",
    "https://www.minimx.fr/fr/736-les-motocross-450cc",
    "https://www.minimx.fr/fr/736-les-motocross-450cc",
    "https://www.minimx.fr/fr/669-motocross-par-marque",
    "https://www.minimx.fr/index.php?id_product=18319&controller=product&id_lang=2",
    "https://www.minimx.fr/fr/670-motocross-crz-erz",
    "https://www.minimx.fr/fr/671-motocross-bastos",
    "https://www.minimx.fr/fr/672-motocross-mini-mx",
    "https://www.minimx.fr/fr/835-sur-ron",
    "https://www.minimx.fr/fr/673-motocross-gunshot",
    "https://www.minimx.fr/fr/735-motocross-probike",
    "https://www.minimx.fr/fr/745-motocross-kayo-motors",
    "https://www.minimx.fr/fr/674-motocross-par-taille-de-roue",
    "https://www.minimx.fr/fr/777-14-17-",
    "https://www.minimx.fr/fr/675-motocross-16-arriere-19-avant",
    "https://www.minimx.fr/fr/676-motocross-18-arriere-et-21-avant",
    "https://www.minimx.fr/index.php?id_category=672&controller=category&id_lang=2",
    "https://www.minimx.fr/fr/677-pieces-par-vehicule",
    "https://www.minimx.fr/fr/542-pieces-motocross-crz-erz-150cc-et-250cc",
    "https://www.minimx.fr/fr/775-erz-450cc-r",
    "https://www.minimx.fr/fr/851-erz-450cc-sx",
    "https://www.minimx.fr/fr/847-pieces-sur-ron",
    "https://www.minimx.fr/fr/540-pieces-detachees-motocross-erz-250-pro-big-mx-250-300s",
    "https://www.minimx.fr/fr/648-pieces-detachees-motocross-crz-erz-300-liquide",
    "https://www.minimx.fr/fr/719-gunshot-250cc-mx-3",
    "https://www.minimx.fr/fr/703-bastos-mxr-150cc250cc",
    "https://www.minimx.fr/fr/705-bastos-rsr-250cc",
    "https://www.minimx.fr/fr/717-gunshot-150-250cc-mx-1",
    "https://www.minimx.fr/fr/718-gunshot-250cc-mx-2",
    "https://www.minimx.fr/fr/719-gunshot-250cc-mx-3",
    "https://www.minimx.fr/fr/605-pieces-detachees-minimx-drift-lx",
    "https://www.minimx.fr/fr/707-pieces-ktm",
    "https://www.minimx.fr/fr/420-ktm-50sx",
    "https://www.minimx.fr/fr/421-ktm-65sx",
    "https://www.minimx.fr/fr/422-ktm-85sx",
    "https://www.minimx.fr/fr/451-ktm-125sx",
    "https://www.minimx.fr/fr/670-motocross-crz-erz",
    "https://www.minimx.fr/index.php?id_product=12584&controller=product&id_lang=2",
    "https://www.minimx.fr/fr/100-dirt-bike-pit-bike-motocross",
    "https://www.minimx.fr/fr/137-par-puissance",
    "https://www.minimx.fr/fr/3-dirt-bike-mini-mx",
    "https://www.minimx.fr/fr/476-les-mini-moto-electriques",
    "https://www.minimx.fr/fr/136-les-50cc-70cc-88cc-enfant-et-mini-rider",
    "https://www.minimx.fr/fr/749-les-110cc",
    "https://www.minimx.fr/fr/133-dirt-bike-125cc-lifan-yx",
    "https://www.minimx.fr/fr/134-dirt-bike-moteur-140cc-yx",
    "https://www.minimx.fr/fr/135-dirt-bike-moteur-150cc-yx",
    "https://www.minimx.fr/fr/533-les-dirt-bike-et-pit-bike-160cc",
    "https://www.minimx.fr/fr/535-les-pit-bike-et-dirt-bike-190cc",
    "https://www.minimx.fr/fr/346-les-motocross-250cc",
    "https://www.minimx.fr/fr/629-les-motocross-300cc",
    "https://www.minimx.fr/fr/737-les-450cc",
    "https://www.minimx.fr/fr/310-marques-dirt-bike-pitbike-motocross",
    "https://www.minimx.fr/3-dirt-bike-mini-mx/s-2/hauteur_de_selle-89_cm+83_cm",
    "https://www.minimx.fr/fr/3-dirt-bike-mini-mx",
    "https://www.minimx.fr/fr/131-dirt-bike-pit-bike-crz-erz",
    "https://www.minimx.fr/fr/177-bastos",
    "https://www.minimx.fr/fr/5-gunshot-dirt-bike-pit-bike",
    "https://www.minimx.fr/fr/brand/80-varetti",
    "https://www.minimx.fr/fr/brand/128-pro-bike",
    "https://www.minimx.fr/fr/brand/186-kerox",
    "https://www.minimx.fr/fr/664-selection-motos-enfant",
    "https://www.minimx.fr/fr/750-type-d-embrayage",
    "https://www.minimx.fr/fr/751-full-automatique",
    "https://www.minimx.fr/fr/752-semi-automatique",
    "https://www.minimx.fr/fr/753-manuel",
    "https://www.minimx.fr/fr/327-taille-de-roue-grande-roue-dirt-bike",
    "https://www.minimx.fr/fr/328-dirt-bike-10-12-petites-roues",
    "https://www.minimx.fr/fr/329-dirt-bike-12-14-taille-standard",
    "https://www.minimx.fr/fr/330-dirt-bike-grandes-roues-14-arriere-et-17-avant",
    "https://www.minimx.fr/fr/334-motocross-16-19-grandes-roues",
    "https://www.minimx.fr/fr/519-motocross-18-21",
    "https://www.minimx.fr/fr/628-pit-bike-12-12-supermotard",
    "https://www.minimx.fr/6-pieces-detachees",
    "https://www.minimx.fr/fr/6-pieces-detachees",
    "https://www.minimx.fr/fr/540-pieces-detachees-motocross-erz-250-pro-big-mx-250-300s",
    "https://www.minimx.fr/fr/542-pieces-motocross-crz-erz-150cc-et-250cc",
    "https://www.minimx.fr/fr/648-pieces-detachees-motocross-crz-erz-300-liquide",
    "https://www.minimx.fr/fr/605-pieces-detachees-minimx-drift-lx",
    "https://www.minimx.fr/index.php?id_category=672&controller=category&id_lang=2",
    "https://www.minimx.fr/fr/305-pocket-bike",
    "https://www.minimx.fr/fr/392-vehicules-pocket-cross-et-pocket-electrique",
    "https://www.minimx.fr/fr/306-pocket-bike",
    "https://www.minimx.fr/fr/416-pocket-cross-electriques",
    "https://www.minimx.fr/fr/dirt-bike-pit-bike-crz-erz/16568-pocket-bike-crz-fury-double-pot-49cc-2t-1010-bleu-2024-3667155023192.html",
    "https://www.minimx.fr/fr/410-les-marques-pocket-bike-thermique-et-electrique",
    "https://www.minimx.fr/fr/411-crz",
    "https://www.minimx.fr/fr/412-kerox",
    "https://www.minimx.fr/fr/brand/193-offmx",
    "https://www.minimx.fr/fr/748-pro-bike",
    "https://www.minimx.fr/fr/768-diamon",
    "https://www.minimx.fr/fr/642-mini-mx",
    "https://www.minimx.fr/fr/137-par-puissance",
    "https://www.minimx.fr/fr/dirt-bike-pit-bike-crz-erz/16000-pit-bike-crz-fury-double-pot-60cc-2t-10-12-orange-2024-3667155022935.html",
    "https://www.minimx.fr/fr/659-les-electriques",
    "https://www.minimx.fr/fr/414-49cc-enfant-de-3-a-8ans",
    "https://www.minimx.fr/fr/739-60cc-enfant-de-6-a-12ans",
    "https://www.minimx.fr/fr/363-pieces-pocket-bike-cross",
    "https://www.minimx.fr/fr/365-carburateurs-pocket-bike",
    "https://www.minimx.fr/fr/613-pieces-detachees-pocket-electriques",
    "https://www.minimx.fr/fr/384-echappement-pour-pocket-bike",
    "https://www.minimx.fr/fr/379-freinage-pocket-bike",
    "https://www.minimx.fr/fr/375-guidon-commande-pocket-bike",
    "https://www.minimx.fr/fr/386-kit-plastique-reservoir-et-selle-pour-pocket-bike",
    "https://www.minimx.fr/fr/374-partie-cycle-pocket-bike",
    "https://www.minimx.fr/fr/370-pieces-electrique-et-allumage-pocket-bike",
    "https://www.minimx.fr/fr/367-pieces-moteur-pocket-bike",
    "https://www.minimx.fr/fr/378-roue-et-pneumatique-pour-pocket-bike",
    "https://www.minimx.fr/fr/376-chaine-et-transmission-pocket-bike",
    "https://www.minimx.fr/fr/391-Pieces-Detachees-Mini-Moto-YAMAHA-PW50-et-PW80",
    "https://www.minimx.fr/fr/337-pieces-pw50",
    "https://www.minimx.fr/fr/338-pieces-pw80",
    "https://www.minimx.fr/fr/488-pieces-detachees-kerox-efat-crz-ekid",
    "https://www.minimx.fr/fr/dirt-bike-pit-bike-crz-erz/16568-pocket-bike-crz-fury-double-pot-49cc-2t-1010-bleu-2024-3667155023192.html",
    "https://www.minimx.fr/fr/411-crz",
    "https://www.minimx.fr/fr/412-kerox",
    "https://www.minimx.fr/fr/555-pocket-quad-2t-quad-4t",
    "https://www.minimx.fr/fr/556-Pocket-Quad-Quad-Electrique-et-Quad-4-Temps",
    "https://www.minimx.fr/fr/pocket-quad-2-temps-pour-enfant/11367-135467-pocket-quad-crz-weely-49cc-vert-3667155100756.html#/687-pack_entretien_2t-sans_option",
    "https://www.minimx.fr/fr/558-quad-4-temps-pour-enfant",
    "https://www.minimx.fr/fr/559-quad-electriques-pour-enfant",
    "https://www.minimx.fr/fr/557-pocket-quad-2-temps-pour-enfant",
    "https://www.minimx.fr/fr/744-quad-adultes-a-partir-de-14-ans",
    "https://www.minimx.fr/fr/560-les-marques-de-pocket-bike-et-quad",
    "https://www.minimx.fr/fr/561-crz",
    "https://www.minimx.fr/fr/825-kayo-xtrem",
    "https://www.minimx.fr/fr/562-kerox",
    "https://www.minimx.fr/fr/563-diamon",
    "https://www.minimx.fr/fr/564-probike",
    "https://www.minimx.fr/fr/crz/11735-147645-quad-crz-weely-110cc-bleu.html#/692-pack_entretien_4t-sans_option",
    "https://www.minimx.fr/fr/565-les-cylindrees-pocket-quad-49cc-et-quad-110cc",
    "https://www.minimx.fr/fr/660-les-electriques",
    "https://www.minimx.fr/fr/566-49cc-enfant-de-3-a-8-ans",
    "https://www.minimx.fr/fr/567-110cc-enfant-de-8-a-12-ans",
    "https://www.minimx.fr/fr/568-125cc-enfant-de-10-a-15-ans",
    "https://www.minimx.fr/fr/740-150cc-adultes-a-partir-14-ans",
    "https://www.minimx.fr/fr/741-200cc-adultes-a-partir-16-ans",
    "https://www.minimx.fr/fr/741-200cc-adultes-a-partir-16-ans",
    "https://www.minimx.fr/fr/574-les-prix-pocket-quad-thermique-et-electrique",
    "https://www.minimx.fr/fr/575-de-299-a-499",
    "https://www.minimx.fr/fr/576-de-499-a-799",
    "https://www.minimx.fr/fr/577-de-799-a-999",
    "https://www.minimx.fr/fr/742-de-999-a-1999",
    "https://www.minimx.fr/fr/578-taille-de-roues",
    "https://www.minimx.fr/fr/579-4-petites-roues",
    "https://www.minimx.fr/fr/580-6-taille-standard",
    "https://www.minimx.fr/fr/581-7-grandes-roues",
    "https://www.minimx.fr/fr/583-8-grandes-roues",
    "https://www.minimx.fr/fr/743-10-grandes-roues",
    "https://www.minimx.fr/fr/741-200cc-adultes-a-partir-16-ans",
    "https://www.minimx.fr/fr/477-pieces-pocket-quad",
    "https://www.minimx.fr/fr/594-carburation",
    "https://www.minimx.fr/fr/595-echappement",
    "https://www.minimx.fr/fr/596-freinage",
    "https://www.minimx.fr/fr/597-guidon-commande",
    "https://www.minimx.fr/fr/598-habillage",
    "https://www.minimx.fr/fr/599-piece-moteur",
    "https://www.minimx.fr/fr/600-pieces-electriques",
    "https://www.minimx.fr/fr/601-roue-et-pneumatique",
    "https://www.minimx.fr/fr/602-partie-cycle",
    "https://www.minimx.fr/fr/603-transmission",
    "https://www.minimx.fr/fr/364-pieces-detachees-quad-4-temps",
    "https://www.minimx.fr/fr/584-carburation",
    "https://www.minimx.fr/fr/593-freinage",
    "https://www.minimx.fr/fr/585-echappement",
    "https://www.minimx.fr/fr/586-guidon-commande",
    "https://www.minimx.fr/fr/587-habillage",
    "https://www.minimx.fr/fr/588-pieces-moteur",
    "https://www.minimx.fr/fr/589-pieces-electriques",
    "https://www.minimx.fr/fr/590-roue-et-pneumatique",
    "https://www.minimx.fr/fr/591-partie-cycle",
    "https://www.minimx.fr/fr/592-transmission",
    "https://www.minimx.fr/fr/614-pieces-detachees-quad-electrique",
    "https://www.minimx.fr/fr/561-crz",
    "https://www.minimx.fr/fr/562-kerox",
    "https://www.minimx.fr/fr/630-vehicule-electrique-pour-enfant",
    "https://www.minimx.fr/fr/634-2-roues-pour-enfant-adolescent",
    "https://www.minimx.fr/fr/633-draisienne-electrique-pour-enfant",
    "https://www.minimx.fr/fr/650-moto-enfant-adolescent",
    "https://www.minimx.fr/fr/416-pocket-cross-electriques",
    "https://www.minimx.fr/fr/636-pieces-detachees-pour-draisienne-crz",
    "https://www.minimx.fr/fr/631-voitures-electrique-pour-enfant",
    "https://www.minimx.fr/fr/632-voiture-electrique-buggy-4x4-pour-enfant",
    "https://www.minimx.fr/fr/649-quad-electrique-pour-enfant",
    "https://www.minimx.fr/fr/652-voiture-electrique-pour-enfant",
    "https://www.minimx.fr/fr/616-velo-electrique-ville-et-vtt",
    "https://www.minimx.fr/fr/617-velo-electrique-pliant-crz",
    "https://www.minimx.fr/fr/619-vtc-electrique",
    "https://www.minimx.fr/fr/618-vtt-electrique",
    "https://www.minimx.fr/fr/771-moto-dax-skyteam-homologue",
    "https://www.minimx.fr/fr/772-thermique-a-essencemoto-dax-skyteam-thermique-50cc-et-125cc",
    "https://www.minimx.fr/fr/773-electrique",
    "https://www.minimx.fr/fr/778-voiture-rc-telecommande-electrique",
    "https://www.minimx.fr/fr/781-jusqu-a-48km-h",
    "https://www.minimx.fr/fr/784-pieces-detachees-voitures-rc-electrique",
    "https://www.minimx.fr/633-draisienne-electrique-pour-enfant/s-88/cylindree_puissance-500w_electrique/marque_2-crz",
    "https://www.minimx.fr/fr/616-velo-electrique-ville-et-vtt",
    "https://www.minimx.fr/fr/619-vtc-electrique",
    "https://www.minimx.fr/fr/618-vtt-electrique",
    "https://www.minimx.fr/fr/617-velo-electrique-pliant-crz",
    "https://www.minimx.fr/fr/771-moto-dax-skyteam-homologue",
    "https://www.minimx.fr/fr/772-thermique-a-essencemoto-dax-skyteam-thermique-50cc-et-125cc",
    "https://www.minimx.fr/fr/773-electrique",
    "https://www.minimx.fr/fr/785-pieces-detachees-dax-skyteam",
    "https://www.minimx.fr/fr/787-allumage",
    "https://www.minimx.fr/fr/789-carburation",
    "https://www.minimx.fr/fr/805-chaine-et-transmission",
    "https://www.minimx.fr/fr/793-echappement",
    "https://www.minimx.fr/fr/795-freinage",
    "https://www.minimx.fr/fr/803-moteur-complet",
    "https://www.minimx.fr/fr/797-partie-cycle",
    "https://www.minimx.fr/fr/801-pieces-moteur",
    "https://www.minimx.fr/fr/791-poste-de-commande",
    "https://www.minimx.fr/fr/799-roue-et-pneumatique",
    "https://www.minimx.fr/772-thermique-a-essence",
    "https://www.minimx.fr/773-electrique",
    "https://www.minimx.fr/fr/6-pieces-detachees",
    "https://www.minimx.fr/fr/30-pieces-electriques-et-allumages-dirt-bike",
    "https://www.minimx.fr/fr/boitier-cdi-dirt-bike-et-motocross/1389-boitier-cdi-v2-reprogramme-pour-dirt-bike-3667155001954.html?fast_search=fs",
    "https://www.minimx.fr/fr/31-bobine-et-bougie-dirt-bike",
    "https://www.minimx.fr/fr/33-boitier-cdi-dirt-bike-et-motocross",
    "https://www.minimx.fr/fr/37-pieces-carter-moteur-d-allumage-dirt-bike",
    "https://www.minimx.fr/fr/34-coupe-circuit-dirt-bike",
    "https://www.minimx.fr/fr/35-faisceau-electrique",
    "https://www.minimx.fr/fr/36-plateau-d-allumage-dirt-bike",
    "https://www.minimx.fr/fr/238-batterie",
    "https://www.minimx.fr/fr/284-compteur-d-heure-pour-moteur-dirt-bike",
    "https://www.minimx.fr/fr/549-pieces-detachees-demarreur-electrique",
    "https://www.minimx.fr/plateau-d-allumage-dirt-bike/290-allumage-rotor-interne-dirt-bike-3700944410435.html",
    "https://www.minimx.fr/fr/80-carburateur-et-filtre-dirt-bike",
    "https://www.minimx.fr/fr/81-carburateur-dirt-bike",
    "https://www.minimx.fr/fr/82-pipe-d-admission-joints-manchons",
    "https://www.minimx.fr/fr/192-durites-d-essence-de-couleur-pour-dirt-bike",
    "https://www.minimx.fr/fr/84-filtres-a-air-et-essence",
    "https://www.minimx.fr/fr/317-gicleur-ralentiprincipal",
    "https://www.minimx.fr/fr/550-boite-a-air",
    "https://www.minimx.fr/fr/carburateur-et-filtre/1033-pack-complet-carburateur-26mm-mikuni-avec-filtre-a-air-dirt-bike-3667155052338.html",
    "https://www.minimx.fr/fr/18-roue-et-pneumatique-dirt-bike",
    "https://www.minimx.fr/fr/22-axe-et-roulement",
    "https://www.minimx.fr/fr/19-chambre-a-air-et-bouchon-de-valve",
    "https://www.minimx.fr/fr/20-pneu",
    "https://www.minimx.fr/fr/21-jante-et-roue-complete",
    "https://www.minimx.fr/fr/roue-complete/571-pack-de-roue-complete-14-17-dirt-bike-3667155051966.html",
    "https://www.minimx.fr/fr/54-moteurs-complets",
    "https://www.minimx.fr/fr/767-moteurs-2-temps",
    "https://www.minimx.fr/fr/766-moteurs-4-temps",
    "https://www.minimx.fr/fr/55-yx-moteur-dirt-bike",
    "https://www.minimx.fr/fr/56-lifan-moteur-dirt-bike",
    "https://www.minimx.fr/fr/647-moteur-complet-zongshen",
    "https://www.minimx.fr/fr/362-moteur-ycf-engine-pour-dirt-bike",
    "https://www.minimx.fr/fr/350-huiles-moteurs-pour-moteur",
    "https://www.minimx.fr/fr/boitier-cdi-dirt-bike-et-motocross/1389-boitier-cdi-v2-reprogramme-pour-dirt-bike-3667155001954.html?fast_search=fs",
    "https://www.minimx.fr/fr/57-pieces-moteur",
    "https://www.minimx.fr/pack-pieces-moteur/818-pack-piston-segment-pochette-140cc-yx-dirt-bike.html",
    "https://www.minimx.fr/fr/65-arbre-de-boite-et-de-kick-dirt-bike",
    "https://www.minimx.fr/fr/68-pieces-carter-d-allumage-bas-moteur-dirt-bike",
    "https://www.minimx.fr/fr/67-pieces-carter-moteur-dirt-bike",
    "https://www.minimx.fr/fr/72-culasse-et-cylindre-lifan-yx-dirt-bike",
    "https://www.minimx.fr/fr/69-embrayage-et-vilebrequin-dirt-bike",
    "https://www.minimx.fr/fr/74-pistons-et-segments",
    "https://www.minimx.fr/fr/75-pochette-de-joints-lifan-yx-dirt-bike",
    "https://www.minimx.fr/fr/76-radiateur-dirt-bike",
    "https://www.minimx.fr/fr/189-pieces-trail-bike",
    "https://www.minimx.fr/fr/brand/44-daytona",
    "https://www.minimx.fr/fr/71-haut-moteur-lifan-yx-dirt-bike",
    "https://www.minimx.fr/fr/72-culasse-et-cylindre-lifan-yx-dirt-bike",
    "https://www.minimx.fr/fr/74-pistons-et-segments",
    "https://www.minimx.fr/fr/75-pochette-de-joints-lifan-yx-dirt-bike",
    "https://www.minimx.fr/fr/76-radiateur-dirt-bike",
    "https://www.minimx.fr/pack-pieces-moteur/3843-pack-piston-segment-pochette-140yx.html",
    "https://www.minimx.fr/fr/64-bas-moteur-lifan-yx-dirt-bike",
    "https://www.minimx.fr/fr/65-arbre-de-boite-et-de-kick-dirt-bike",
    "https://www.minimx.fr/fr/68-pieces-carter-d-allumage-bas-moteur-dirt-bike",
    "https://www.minimx.fr/fr/67-pieces-carter-moteur-dirt-bike",
    "https://www.minimx.fr/fr/69-embrayage-et-vilebrequin-dirt-bike",
    "https://www.minimx.fr/fr/127-pochette-de-joints-lifan-yx-dirt-bike",
    "https://www.minimx.fr/fr/24-frein-pedale-plaquette-disques-pour-dirt-bike",
    "https://www.minimx.fr/fr/25-disques-et-durite-de-freins-dirt-bike",
    "https://www.minimx.fr/fr/27-kit-de-frein-dirt-bike",
    "https://www.minimx.fr/fr/553-maitre-cylindre",
    "https://www.minimx.fr/fr/554-etrier-de-frein",
    "https://www.minimx.fr/fr/28-plaquette-de-frein",
    "https://www.minimx.fr/fr/29-pedale-et-levier-de-frein",
    "https://www.minimx.fr/fr/552-visseries-protections-accessoires",
    "https://www.minimx.fr/fr/58-piece-chaine-et-transmission-dirt-bike",
    "https://www.minimx.fr/fr/59-chaine-dirt-bike",
    "https://www.minimx.fr/fr/174-accessoires-roulette-de-chaine",
    "https://www.minimx.fr/fr/60-couronne-et-pignon",
    "https://www.minimx.fr/fr/62-tendeurs-de-chaine-et-guide-chaine",
    "https://www.minimx.fr/fr/521-configurateur-de-transmission",
    "https://www.minimx.fr/configurateur-de-transmission/894-139004-pack-nervosite-140cc-yx-lifan-chaine-pignon-couronne-dirt-bike.html#/24-pas_de_chaine-420/170-nombre_de_dents_couronne-39_dents/815-nombre_de_dents-14_dents",
    "https://www.minimx.fr/fr/7-guidon-commande-dirt-bike-pit-bike",
    "https://www.minimx.fr/fr/8-cable-d-embrayage-et-d-accelerateur-dirt-bike",
    "https://www.minimx.fr/fr/9-guidon-pontet-mousse-dirt-bike",
    "https://www.minimx.fr/fr/10-kick-et-selecteur-dirt-bike",
    "https://www.minimx.fr/fr/11-levier-d-embrayage-et-frein-dirt-bike",
    "https://www.minimx.fr/fr/13-tirage-et-poignee",
    "https://www.minimx.fr/levier-d-embrayage-et-frein-dirt-bike/12562-levier-d-embrayage-pro-taper-profile-perch-pour-dirt-bike.html",
    "https://www.minimx.fr/fr/254-pieces-detachees-dirt-bike-et-pit-bike-occasion",
    "https://www.minimx.fr/fr/77-echappement",
    "https://www.minimx.fr/fr/175-lignes-et-cartouches-d-echappement-dirt-bike",
    "https://www.minimx.fr/fr/176-joints-fixation-accessoires-dirt-bike",
    "https://www.minimx.fr/echappement-scalvini/15780-ligne-d-echappement-double-sorties-scalvini-carbon-crf110.html?fast_search=fs",
    "https://www.minimx.fr/fr/14-habillage-dirt-bike-pit-bike",
    "https://www.minimx.fr/fr/15-kit-plastique-dirt-bike",
    "https://www.minimx.fr/fr/178-housse-de-selle",
    "https://www.minimx.fr/fr/16-kit-decoration-et-stickers-dirt-bike",
    "https://www.minimx.fr/fr/49-reservoir-et-bouchon",
    "https://www.minimx.fr/fr/17-selle-dirt-bike",
    "https://www.minimx.fr/hsq-m/15866-kit-decoration-montser-hsq-m.html?fast_search=fs",
    "https://www.minimx.fr/fr/38-partie-cycle-dirt-bike",
    "https://www.minimx.fr/fr/43-bras-oscillant-et-cadre",
    "https://www.minimx.fr/fr/48-cale-pied-et-bequille",
    "https://www.minimx.fr/fr/49-reservoir-et-bouchon",
    "https://www.minimx.fr/fr/50-sabot-moteur",
    "https://www.minimx.fr/fr/39-suspensions-dirt-bike",
    "https://www.minimx.fr/cale-pied-et-bequille/1005-cales-pieds-rouge-cnc-ycf-pour-dirt-bike-pit-bike.html",
    "https://www.minimx.fr/fr/39-suspensions-dirt-bike",
    "https://www.minimx.fr/fr/40-amortisseurs-dirt-bike",
    "https://www.minimx.fr/fr/41-fourche-dirt-bike",
    "https://www.minimx.fr/fr/42-te-et-pontet-dirt-bike",
    "https://www.minimx.fr/fr/325-suspension-haut-de-gamme",
    "https://www.minimx.fr/amortisseurs-dirt-bike/1305-chaussette-d-amortisseur-320mm-monster.html",
    "https://www.minimx.fr/fr/179-pieces-supermotard",
    "https://www.minimx.fr/fr/181-visserie-generale",
    "https://www.minimx.fr/fr/847-pieces-sur-ron",
    "https://www.minimx.fr/fr/853-partie-cycle",
    "https://www.minimx.fr/fr/855-commande",
    "https://www.minimx.fr/fr/857-transmission",
    "https://www.minimx.fr/fr/859-freinage",
    "https://www.minimx.fr/fr/861-pieces-moteur",
    "https://www.minimx.fr/fr/863-habillage",
    "https://www.minimx.fr/fr/865-roue-et-pneumatique",
    "https://www.minimx.fr/fr/brand/174-mbf",
    "https://www.minimx.fr/fr/brand/65-trail-bike-parts",
    "https://www.minimx.fr/fr/brand/93-faba",
    "https://www.minimx.fr/fr/brand/84-formula",
    "https://www.minimx.fr/fr/brand/44-daytona",
    "https://www.minimx.fr/fr/brand/72-doma-racing",
    "https://www.minimx.fr/fr/brand/140-ycf-parts",
    "https://www.minimx.fr/fr/254-pieces-detachees-dirt-bike-et-pit-bike-occasion",
    "https://www.minimx.fr/fr/85-equipements-entretien",
    "https://www.minimx.fr/fr/93-huiles-et-lubrifiants",
    "https://www.minimx.fr/fr/143-huiles-moteurs",
    "https://www.minimx.fr/fr/144-huile-de-fourche-dirt-bike",
    "https://www.minimx.fr/fr/145-liquide-de-frein",
    "https://www.minimx.fr/fr/146-graisses-nettoyant-spray-dirt-bike",
    "https://www.minimx.fr/fr/94-outillage",
    "https://www.minimx.fr/fr/250-antivol",
    "https://www.minimx.fr/fr/251-accessoires",
    "https://www.minimx.fr/fr/165-entretien-cables-et-durites",
    "https://www.minimx.fr/fr/164-outils-de-lavage-dirt-bike",
    "https://www.minimx.fr/fr/166-outillage-roue-et-pneumatique",
    "https://www.minimx.fr/fr/167-outillage-chaine-et-transmission",
    "https://www.minimx.fr/fr/168-outils-moteur",
    "https://www.minimx.fr/fr/181-visserie-generale",
    "https://www.minimx.fr/fr/86-equipement-du-pilote",
    "https://www.minimx.fr/fr/354-les-bons-plans",
    "https://www.minimx.fr/fr/87-casques-dirt-bike",
    "https://www.minimx.fr/fr/390-bottes-et-chaussettes",
    "https://www.minimx.fr/fr/89-gants-dirt-bike",
    "https://www.minimx.fr/fr/163-maillots-pantalons-moto-cross-dirt-bike",
    "https://www.minimx.fr/fr/91-accessoires-dirt-bike",
    "https://www.minimx.fr/fr/88-masques-motocross",
    "https://www.minimx.fr/fr/90-protections-motocross",
    "https://www.minimx.fr/fr/163-maillots-pantalons-moto-cross-dirt-bike",
    "https://www.minimx.fr/fr/230-maillots",
    "https://www.minimx.fr/fr/231-pantalons",
    "https://www.minimx.fr/fr/232-pack-maillot-pantalon",
    "https://www.minimx.fr/fr/318-sportswear",
    "https://www.minimx.fr/fr/233-equipement-pour-enfant-motocross",
    "https://www.minimx.fr/fr/355-les-bons-plans-equipement-enfant-motocross",
    "https://www.minimx.fr/fr/320-bottes-enfants-motocross",
    "https://www.minimx.fr/fr/235-casques-enfant-motocross",
    "https://www.minimx.fr/fr/236-gants-enfants",
    "https://www.minimx.fr/fr/237-maillots-pantalons-enfant-motocross",
    "https://www.minimx.fr/fr/335-masques-motocross-enfant",
    "https://www.minimx.fr/fr/321-protections-motocross-enfant",
    "https://www.minimx.fr/fr/615-equipement-vtt",
    "https://www.minimx.fr/fr/620-casques",
    "https://www.minimx.fr/fr/621-maillots-pantalons",
    "https://www.minimx.fr/fr/622-protections",
    "https://www.minimx.fr/fr/623-gants",
    "https://www.minimx.fr/fr/brand/88-ipone",
    "https://www.minimx.fr/fr/brand/161-putoline",
    "https://www.minimx.fr/fr/brand/137-o-neal",
    "https://www.minimx.fr/fr/brand/151-fox-racing",
    "https://www.minimx.fr/fr/brand/55-100",
    "https://www.minimx.fr/fr/brand/40-shot",
    "https://www.minimx.fr/fr/brand/121-kenny",
    "https://www.minimx.fr/fr/brand/106-thor",
    "https://www.minimx.fr/fr/brand/122-pull",
    "https://www.minimx.fr/fr/500-outlet",
    "https://www.minimx.fr/fr/501-equipement-du-pilote",
    "https://www.minimx.fr/fr/504-casques",
    "https://www.minimx.fr/fr/505-masques-protections",
    "https://www.minimx.fr/fr/506-gants",
    "https://www.minimx.fr/fr/508-bottes-et-chaussettes",
    "https://www.minimx.fr/fr/502-maillots-pantalons",
    "https://www.minimx.fr/fr/515-maillots",
    "https://www.minimx.fr/fr/516-pantalons",
    "https://www.minimx.fr/fr/517-packs-maillot-pantalon",
    "https://www.minimx.fr/fr/503-equipement-pour-enfant",
    "https://www.minimx.fr/fr/509-bottes",
    "https://www.minimx.fr/fr/510-casques",
    "https://www.minimx.fr/fr/511-gants",
    "https://www.minimx.fr/fr/512-maillots-pantalons",
    "https://www.minimx.fr/fr/513-protections",
    "https://www.minimx.fr/fr/254-pieces-detachees-dirt-bike-et-pit-bike-occasion",
    "https://www.minimx.fr/fr/831-pieces-detachees",
    "https://www.minimx.fr/fr/833-vehicules",
    "https://www.minimx.fr/fr/254-pieces-detachees-dirt-bike-et-pit-bike-occasion"
]

# Directory to store CSV files and plots
DATA_DIR = 'stock_data'
PLOT_DIR = 'stock_plots'
CSV_FILE = os.path.join(DATA_DIR, 'stock_data.csv')


def setup_directories():
    """Create directories for data and plots if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR, exist_ok=True)


def initialize_csv():
    """Initialize a single CSV file for all products, overwriting if it exists."""
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['timestamp', 'id_product', 'category', 'name', 'stock_quantity', 'quantity_all_version', 'price',
             'price_without_reduction'])
    return CSV_FILE


def get_product_links(session, category_url):
    """Extract product links from a category page, handling pagination."""
    product_links = []
    page = 1
    while True:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        try:
            response = session.get(url, headers=get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find product links within id="products" using only a.product-thumbnail
            products_container = soup.select_one('#products')
            if not products_container:
                logging.info(f"No products container found on page {page} of {category_url}")
                break

            products = products_container.select('a.product-thumbnail')
            if not products:
                logging.info(f"No more products found on page {page} of {category_url}")
                break

            for product in products:
                href = product.get('href')
                if href and '/fr/' in href and 'index.php' not in href:
                    # Extract product ID from URL (e.g., /fr/quad/123-product1.html)
                    product_id = re.search(r'/(\d+)-', href)
                    product_id = product_id.group(1) if product_id else None
                    if product_id:
                        product_links.append({
                            'url': href,
                            'id_product': product_id,
                            'category': category_url
                        })
            logging.info(f"Found {len(products)} products on page {page} of {category_url}")
            page += 1
            time.sleep(5)  # Increased delay to avoid server overload
        except requests.RequestException as e:
            logging.error(f"Error fetching category page {url}: {e}")
            break
    return product_links


def get_all_products(session):
    """Get all product links by scanning category pages."""
    all_products = []
    for category_url in CATEGORY_URLS:
        logging.info(f"Scraping category: {category_url}")
        products = get_product_links(session, category_url)
        all_products.extend(products)
        time.sleep(5)  # Increased delay between categories

    # Remove duplicates based on product ID
    seen_ids = set()
    unique_products = []
    for product in all_products:
        if product['id_product'] not in seen_ids:
            unique_products.append(product)
            seen_ids.add(product['id_product'])

    logging.info(f"Total unique products found: {len(unique_products)}")
    return unique_products


def extract_product_details(session, product):
    """Extract detailed product information from product page."""
    try:
        response = session.get(product['url'], headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to extract product details from JSON data
        product_details_elem = soup.select_one('#product-details')
        if product_details_elem and 'data-product' in product_details_elem.attrs:
            try:
                product_json = json.loads(product_details_elem['data-product'])

                # Extract key details
                stock_quantity = product_json.get('quantity', 0)

                # Extract quantity_all_version
                quantity_all_version = product_json.get('quantity_all_version', 0)

                # Price details
                price = product_json.get('price_amount', 0)  # Changed from 'price' to 'price_amount'
                price_without_reduction = product_json.get('price_without_reduction', price)

                # Logging for verification
                logging.info(f"Product Details - ID: {product['id_product']}, URL: {product['url']}, "
                             f"Stock: {stock_quantity}, All Versions Stock: {quantity_all_version}, Price: {price}, "
                             f"Price without Reduction: {price_without_reduction}")

                return {
                    'id_product': product['id_product'],
                    'category': product['category'],  # Added category
                    'name': product['url'],  # Use product URL as name
                    'stock_quantity': stock_quantity,
                    'quantity_all_version': quantity_all_version,  # Added quantity_all_version
                    'price': price,
                    'price_without_reduction': price_without_reduction
                }
            except (json.JSONDecodeError, KeyError) as json_err:
                logging.error(f"Error parsing product JSON for {product['url']}: {json_err}")
                return None

        # Fallback parsing if JSON method fails
        logging.warning(f"Could not find product details JSON for {product['url']}")
        return None

    except requests.RequestException as e:
        logging.error(f"Error fetching product details for {product['url']}: {e}")
        return None


def save_stock_data(product_details):
    """Save stock data to a single CSV file."""
    csv_file = CSV_FILE
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            product_details['id_product'],
            product_details['category'],
            product_details['name'],
            product_details['stock_quantity'],
            product_details['quantity_all_version'],  # Added quantity_all_version
            product_details['price'],
            product_details['price_without_reduction']
        ])


def plot_stock_data(id_product):
    """Generate a line plot of stock levels over time."""
    csv_file = CSV_FILE
    if not os.path.exists(csv_file):
        logging.warning(f"No data to plot for Product ID: {id_product}")
        return

    # Read CSV data with explicit encoding and error handling
    try:
        df = pd.read_csv(csv_file, encoding='utf-8', encoding_errors='replace')
        df = df[df['id_product'] == id_product]  # Filter by Product ID
        if df.empty:
            logging.warning(f"No data to plot for Product ID: {id_product}")
            return
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Plot both stock quantities
        plt.figure(figsize=(12, 7))

        # Plot regular stock quantity
        plt.plot(df['timestamp'], df['stock_quantity'], marker='o', label='Current Version Stock')

        # Plot quantity_all_version if it exists in the DataFrame
        if 'quantity_all_version' in df.columns:
            plt.plot(df['timestamp'], df['quantity_all_version'], marker='s', linestyle='--',
                     color='green', label='All Versions Stock')

        plt.title(f'Stock Levels for Product ID {id_product}\n{df["name"].iloc[0]}')
        plt.xlabel('Timestamp')
        plt.ylabel('Stock Quantity')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Save plot with product ID sanitized for filename
        safe_id = re.sub(r'[^\w\-]', '_', str(id_product))[:100]
        plot_file = os.path.join(PLOT_DIR, f'{safe_id}_stock_plot.png')
        plt.savefig(plot_file)
        plt.close()
        logging.info(f"Plot saved: {plot_file}")
    except Exception as e:
        logging.error(f"Error plotting stock data for Product ID {id_product}: {e}")


def monitor_stocks():
    """Main function to monitor stock levels."""
    logging.info("Starting monitor_stocks...")
    setup_directories()
    initialize_csv()
    logging.info("Directories created: stock_data, stock_plots")

    # Create session
    session = requests.Session()

    # Get all products
    logging.info("Collecting products...")
    products = get_all_products(session)
    if not products:
        logging.error("No products found. Exiting.")
        return
    logging.info(f"Collected {len(products)} products")

    # Process each product
    for product in products:
        logging.info(f"Processing product: {product['id_product']}")

        # Extract product details
        product_details = extract_product_details(session, product)

        if product_details:
            # Save stock data
            save_stock_data(product_details)

            # Generate plot
            plot_stock_data(product_details['id_product'])

        # Delay between products to avoid overwhelming server
        time.sleep(5)


def main():
    """Schedule the stock monitoring task."""
    # Run immediately
    monitor_stocks()

    # Schedule to run every 2 hours
    schedule.every(2).hours.do(monitor_stocks)

    logging.info("Starting scheduler. Script will run every 2 hours. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()