import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime, timedelta
import os
import schedule
import pandas as pd
import logging
import re
import json
import random
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# User-Agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

# Base URL and categories
BASE_URL = 'https://www.minimx.fr/'
CATEGORY_URLS = [
    'https://www.minimx.fr/amortisseurs-dirt-bike/1305-chaussette-d-amortisseur-320mm-monster.html',
    'https://www.minimx.fr/cale-pied-et-bequille/1005-cales-pieds-rouge-cnc-ycf-pour-dirt-bike-pit-bike.html',
    'https://www.minimx.fr/configurateur-de-transmission/894-139004-pack-nervosite-140cc-yx-lifan-chaine-pignon-couronne-dirt-bike.html#/24-pas_de_chaine-420/170-nombre_de_dents_couronne-39_dents/815-nombre_de_dents-14_dents',
    'https://www.minimx.fr/echappement-scalvini/15780-ligne-d-echappement-double-sorties-scalvini-carbon-crf110.html?fast_search=fs',
    'https://www.minimx.fr/fr/10-kick-et-selecteur-dirt-bike',
    'https://www.minimx.fr/fr/11-levier-d-embrayage-et-frein-dirt-bike',
    'https://www.minimx.fr/fr/127-pochette-de-joints-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/13-tirage-et-poignee',
    'https://www.minimx.fr/fr/14-habillage-dirt-bike-pit-bike',
    'https://www.minimx.fr/fr/143-huiles-moteurs',
    'https://www.minimx.fr/fr/144-huile-de-fourche-dirt-bike',
    'https://www.minimx.fr/fr/145-liquide-de-frein',
    'https://www.minimx.fr/fr/146-graisses-nettoyant-spray-dirt-bike',
    'https://www.minimx.fr/fr/15-kit-plastique-dirt-bike',
    'https://www.minimx.fr/fr/16-kit-decoration-et-stickers-dirt-bike',
    'https://www.minimx.fr/fr/163-maillots-pantalons-moto-cross-dirt-bike',
    'https://www.minimx.fr/fr/164-outils-de-lavage-dirt-bike',
    'https://www.minimx.fr/fr/165-entretien-cables-et-durites',
    'https://www.minimx.fr/fr/166-outillage-roue-et-pneumatique',
    'https://www.minimx.fr/fr/167-outillage-chaine-et-transmission',
    'https://www.minimx.fr/fr/168-outils-moteur',
    'https://www.minimx.fr/fr/17-selle-dirt-bike',
    'https://www.minimx.fr/fr/174-accessoires-roulette-de-chaine',
    'https://www.minimx.fr/fr/175-lignes-et-cartouches-d-echappement-dirt-bike',
    'https://www.minimx.fr/fr/176-joints-fixation-accessoires-dirt-bike',
    'https://www.minimx.fr/fr/178-housse-de-selle',
    'https://www.minimx.fr/fr/179-pieces-supermotard',
    'https://www.minimx.fr/fr/18-roue-et-pneumatique-dirt-bike',
    'https://www.minimx.fr/fr/181-visserie-generale',
    'https://www.minimx.fr/fr/189-pieces-trail-bike',
    'https://www.minimx.fr/fr/19-chambre-a-air-et-bouchon-de-valve',
    'https://www.minimx.fr/fr/192-durites-d-essence-de-couleur-pour-dirt-bike',
    'https://www.minimx.fr/fr/20-pneu',
    'https://www.minimx.fr/fr/21-jante-et-roue-complete',
    'https://www.minimx.fr/fr/22-axe-et-roulement',
    'https://www.minimx.fr/fr/230-maillots',
    'https://www.minimx.fr/fr/231-pantalons',
    'https://www.minimx.fr/fr/232-pack-maillot-pantalon',
    'https://www.minimx.fr/fr/233-equipement-pour-enfant-motocross',
    'https://www.minimx.fr/fr/235-casques-enfant-motocross',
    'https://www.minimx.fr/fr/236-gants-enfants',
    'https://www.minimx.fr/fr/237-maillots-pantalons-enfant-motocross',
    'https://www.minimx.fr/fr/238-batterie-chargeur-controlleur',
    'https://www.minimx.fr/fr/24-frein-pedale-plaquette-disques-pour-dirt-bike',
    'https://www.minimx.fr/fr/25-disques-et-durite-de-freins-dirt-bike',
    'https://www.minimx.fr/fr/250-antivol',
    'https://www.minimx.fr/fr/251-accessoires',
    'https://www.minimx.fr/fr/254-pieces-detachees-dirt-bike-et-pit-bike-occasion',
    'https://www.minimx.fr/fr/27-kit-de-frein-dirt-bike',
    'https://www.minimx.fr/fr/28-plaquette-de-frein',
    'https://www.minimx.fr/fr/284-compteur-d-heure-pour-moteur-dirt-bike',
    'https://www.minimx.fr/fr/29-pedale-et-levier-de-frein',
    'https://www.minimx.fr/fr/30-pieces-electriques-et-allumages-dirt-bike',
    'https://www.minimx.fr/fr/31-bobine-et-bougie-dirt-bike',
    'https://www.minimx.fr/fr/317-gicleur-ralentiprincipal',
    'https://www.minimx.fr/fr/318-sportswear',
    'https://www.minimx.fr/fr/320-bottes-enfants-motocross',
    'https://www.minimx.fr/fr/321-protections-motocross-enfant',
    'https://www.minimx.fr/fr/325-suspension-haut-de-gamme',
    'https://www.minimx.fr/fr/33-boitier-cdi-dirt-bike-et-motocross',
    'https://www.minimx.fr/fr/335-masques-motocross-enfant',
    'https://www.minimx.fr/fr/34-coupe-circuit-dirt-bike',
    'https://www.minimx.fr/fr/35-faisceau-electrique',
    'https://www.minimx.fr/fr/350-huiles-moteurs-pour-moteur',
    'https://www.minimx.fr/fr/354-les-bons-plans',
    'https://www.minimx.fr/fr/355-les-bons-plans-equipement-enfant-motocross',
    'https://www.minimx.fr/fr/36-plateau-d-allumage-dirt-bike',
    'https://www.minimx.fr/fr/362-moteur-ycf-engine-pour-dirt-bike',
    'https://www.minimx.fr/fr/37-pieces-carter-moteur-d-allumage-dirt-bike',
    'https://www.minimx.fr/fr/38-partie-cycle-dirt-bike',
    'https://www.minimx.fr/fr/39-suspensions-dirt-bike',
    'https://www.minimx.fr/fr/390-bottes-et-chaussettes',
    'https://www.minimx.fr/fr/40-amortisseurs-dirt-bike',
    'https://www.minimx.fr/fr/41-fourche-dirt-bike',
    'https://www.minimx.fr/fr/42-te-pontets-protection-de-fourche',
    'https://www.minimx.fr/fr/43-bras-oscillant-et-cadre',
    'https://www.minimx.fr/fr/48-cale-pied-et-bequille',
    'https://www.minimx.fr/fr/49-reservoir-et-bouchon',
    'https://www.minimx.fr/fr/50-sabot-moteur',
    'https://www.minimx.fr/fr/521-configurateur-de-transmission',
    'https://www.minimx.fr/fr/54-moteurs-complets',
    'https://www.minimx.fr/fr/540-pieces-detachees-motocross-erz-250-pro-big-mx-250-300s',
    'https://www.minimx.fr/fr/542-pieces-motocross-crz-erz-150cc-et-250cc',
    'https://www.minimx.fr/fr/549-pieces-detachees-demarreur-electrique',
    'https://www.minimx.fr/fr/55-yx-moteur-dirt-bike',
    'https://www.minimx.fr/fr/550-boite-a-air',
    'https://www.minimx.fr/fr/552-visseries-protections-accessoires',
    'https://www.minimx.fr/fr/553-maitre-cylindre',
    'https://www.minimx.fr/fr/554-etrier-de-frein',
    'https://www.minimx.fr/fr/56-lifan-moteur-dirt-bike',
    'https://www.minimx.fr/fr/57-pieces-moteur',
    'https://www.minimx.fr/fr/58-piece-chaine-et-transmission-dirt-bike',
    'https://www.minimx.fr/fr/59-chaine-dirt-bike',
    'https://www.minimx.fr/fr/6-pieces-detachees',
    'https://www.minimx.fr/fr/60-couronne-et-pignon',
    'https://www.minimx.fr/fr/605-pieces-detachees-minimx-drift-lx',
    'https://www.minimx.fr/fr/615-equipement-vtt',
    'https://www.minimx.fr/fr/62-tendeurs-de-chaine-et-guide-chaine',
    'https://www.minimx.fr/fr/620-casques',
    'https://www.minimx.fr/fr/621-maillots-pantalons',
    'https://www.minimx.fr/fr/622-protections',
    'https://www.minimx.fr/fr/623-gants',
    'https://www.minimx.fr/fr/64-bas-moteur-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/647-moteur-complet-zongshen',
    'https://www.minimx.fr/fr/648-pieces-detachees-motocross-crz-erz-300-liquide',
    'https://www.minimx.fr/fr/65-arbre-de-boite-et-de-kick-dirt-bike',
    'https://www.minimx.fr/fr/67-pieces-carter-moteur-dirt-bike',
    'https://www.minimx.fr/fr/677-pieces-par-vehicule',
    'https://www.minimx.fr/fr/68-pieces-carter-d-allumage-bas-moteur-dirt-bike',
    'https://www.minimx.fr/fr/69-embrayage-et-vilebrequin-dirt-bike',
    'https://www.minimx.fr/fr/7-guidon-commande-dirt-bike-pit-bike',
    'https://www.minimx.fr/fr/703-bastos-mxr-150cc250cc',
    'https://www.minimx.fr/fr/705-bastos-rsr-250cc',
    'https://www.minimx.fr/fr/707-pieces-ktm',
    'https://www.minimx.fr/fr/71-haut-moteur-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/717-gunshot-150-250cc-mx-1',
    'https://www.minimx.fr/fr/718-gunshot-250cc-mx-2',
    'https://www.minimx.fr/fr/719-gunshot-250cc-mx-3',
    'https://www.minimx.fr/fr/72-culasse-et-cylindre-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/74-pistons-et-segments',
    'https://www.minimx.fr/fr/75-pochette-de-joints-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/76-radiateur-dirt-bike',
    'https://www.minimx.fr/fr/766-moteurs-4-temps',
    'https://www.minimx.fr/fr/767-moteurs-2-temps',
    'https://www.minimx.fr/fr/77-echappement',
    'https://www.minimx.fr/fr/775-erz-450cc-r',
    'https://www.minimx.fr/fr/785-pieces-detachees-dax-skyteam',
    'https://www.minimx.fr/fr/8-cable-d-embrayage-et-d-accelerateur-dirt-bike',
    'https://www.minimx.fr/fr/80-carburateur-et-filtre-dirt-bike',
    'https://www.minimx.fr/fr/81-carburateur-dirt-bike',
    'https://www.minimx.fr/fr/82-pipe-d-admission-joints-manchons',
    'https://www.minimx.fr/fr/84-filtres-a-air-et-essence',
    'https://www.minimx.fr/fr/847-pieces-sur-ron',
    'https://www.minimx.fr/fr/85-equipements-entretien',
    'https://www.minimx.fr/fr/851-erz-450cc-sx',
    'https://www.minimx.fr/fr/853-partie-cycle',
    'https://www.minimx.fr/fr/855-commande',
    'https://www.minimx.fr/fr/857-transmission',
    'https://www.minimx.fr/fr/859-freinage',
    'https://www.minimx.fr/fr/86-equipement-du-pilote',
    'https://www.minimx.fr/fr/861-pieces-moteur',
    'https://www.minimx.fr/fr/863-habillage',
    'https://www.minimx.fr/fr/865-roue-et-pneumatique',
    'https://www.minimx.fr/fr/87-casques-dirt-bike',
    'https://www.minimx.fr/fr/879-electrique',
    'https://www.minimx.fr/fr/88-masques-motocross',
    'https://www.minimx.fr/fr/885-joints-roulements-visseries-axe-de-colonne',
    'https://www.minimx.fr/fr/887-crz-bull-200cc',
    'https://www.minimx.fr/fr/89-gants-dirt-bike',
    'https://www.minimx.fr/fr/9-guidon-pontet-mousse-dirt-bike',
    'https://www.minimx.fr/fr/90-protections-motocross',
    'https://www.minimx.fr/fr/91-accessoires-dirt-bike',
    'https://www.minimx.fr/fr/93-huiles-et-lubrifiants',
    'https://www.minimx.fr/fr/94-outillage',
    'https://www.minimx.fr/fr/boitier-cdi-dirt-bike-et-motocross/1389-boitier-cdi-v2-reprogramme-pour-dirt-bike-3667155001954.html?fast_search=fs',
    'https://www.minimx.fr/fr/brand/106-thor',
    'https://www.minimx.fr/fr/brand/121-kenny',
    'https://www.minimx.fr/fr/brand/122-pull',
    'https://www.minimx.fr/fr/brand/137-o-neal',
    'https://www.minimx.fr/fr/brand/140-ycf-parts',
    'https://www.minimx.fr/fr/brand/151-fox-racing',
    'https://www.minimx.fr/fr/brand/161-putoline',
    'https://www.minimx.fr/fr/brand/174-mbf',
    'https://www.minimx.fr/fr/brand/40-shot',
    'https://www.minimx.fr/fr/brand/44-daytona',
    'https://www.minimx.fr/fr/brand/55-100',
    'https://www.minimx.fr/fr/brand/65-trail-bike-parts',
    'https://www.minimx.fr/fr/brand/72-doma-racing',
    'https://www.minimx.fr/fr/brand/84-formula',
    'https://www.minimx.fr/fr/brand/88-ipone',
    'https://www.minimx.fr/fr/brand/93-faba',
    'https://www.minimx.fr/fr/carburateur-et-filtre/1033-pack-complet-carburateur-26mm-mikuni-avec-filtre-a-air-dirt-bike-3667155052338.html',
    'https://www.minimx.fr/fr/roue-complete/571-pack-de-roue-complete-14-17-dirt-bike-3667155051966.html',
    'https://www.minimx.fr/hsq-m/15866-kit-decoration-montser-hsq-m.html?fast_search=fs',
    'https://www.minimx.fr/levier-d-embrayage-et-frein-dirt-bike/12562-levier-d-embrayage-pro-taper-profile-perch-pour-dirt-bike.html',
    'https://www.minimx.fr/pack-pieces-moteur/3843-pack-piston-segment-pochette-140yx.html',
    'https://www.minimx.fr/pack-pieces-moteur/818-pack-piston-segment-pochette-140cc-yx-dirt-bike.html',
    'https://www.minimx.fr/plateau-d-allumage-dirt-bike/290-allumage-rotor-interne-dirt-bike-3700944410435.html',
    'https://www.minimx.fr/3-dirt-bike-mini-mx/s-2/hauteur_de_selle-89_cm+83_cm',
    'https://www.minimx.fr/6-pieces-detachees',
    'https://www.minimx.fr/632-voiture-electrique-buggy-4x4-pour-enfant',
    'https://www.minimx.fr/633-draisienne-electrique-pour-enfant/s-88/cylindree_puissance-500w_electrique',
    'https://www.minimx.fr/633-draisienne-electrique-pour-enfant/s-88/cylindree_puissance-500w_electrique/marque_2-crz',
    'https://www.minimx.fr/772-thermique-a-essence',
    'https://www.minimx.fr/773-electrique',
    'https://www.minimx.fr/amortisseurs-dirt-bike/1305-chaussette-d-amortisseur-320mm-monster.html',
    'https://www.minimx.fr/cale-pied-et-bequille/1005-cales-pieds-rouge-cnc-ycf-pour-dirt-bike-pit-bike.html',
    'https://www.minimx.fr/configurateur-de-transmission/894-139004-pack-nervosite-140cc-yx-lifan-chaine-pignon-couronne-dirt-bike.html#/24-pas_de_chaine-420/170-nombre_de_dents_couronne-39_dents/815-nombre_de_dents-14_dents',
    'https://www.minimx.fr/echappement-scalvini/15780-ligne-d-echappement-double-sorties-scalvini-carbon-crf110.html?fast_search=fs',
    'https://www.minimx.fr/fr/10-kick-et-selecteur-dirt-bike',
    'https://www.minimx.fr/fr/100-dirt-bike-pit-bike-motocross',
    'https://www.minimx.fr/fr/11-levier-d-embrayage-et-frein-dirt-bike',
    'https://www.minimx.fr/fr/127-pochette-de-joints-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/13-tirage-et-poignee',
    'https://www.minimx.fr/fr/131-dirt-bike-pit-bike-crz-erz',
    'https://www.minimx.fr/fr/133-dirt-bike-125cc-lifan-yx',
    'https://www.minimx.fr/fr/134-dirt-bike-moteur-140cc-yx',
    'https://www.minimx.fr/fr/135-dirt-bike-moteur-150cc-yx',
    'https://www.minimx.fr/fr/136-les-50cc-70cc-88cc-enfant-et-mini-rider',
    'https://www.minimx.fr/fr/137-par-puissance',
    'https://www.minimx.fr/fr/14-habillage-dirt-bike-pit-bike',
    'https://www.minimx.fr/fr/143-huiles-moteurs',
    'https://www.minimx.fr/fr/144-huile-de-fourche-dirt-bike',
    'https://www.minimx.fr/fr/145-liquide-de-frein',
    'https://www.minimx.fr/fr/146-graisses-nettoyant-spray-dirt-bike',
    'https://www.minimx.fr/fr/15-kit-plastique-dirt-bike',
    'https://www.minimx.fr/fr/16-kit-decoration-et-stickers-dirt-bike',
    'https://www.minimx.fr/fr/163-maillots-pantalons-moto-cross-dirt-bike',
    'https://www.minimx.fr/fr/164-outils-de-lavage-dirt-bike',
    'https://www.minimx.fr/fr/165-entretien-cables-et-durites',
    'https://www.minimx.fr/fr/166-outillage-roue-et-pneumatique',
    'https://www.minimx.fr/fr/167-outillage-chaine-et-transmission',
    'https://www.minimx.fr/fr/168-outils-moteur',
    'https://www.minimx.fr/fr/17-selle-dirt-bike',
    'https://www.minimx.fr/fr/174-accessoires-roulette-de-chaine',
    'https://www.minimx.fr/fr/175-lignes-et-cartouches-d-echappement-dirt-bike',
    'https://www.minimx.fr/fr/176-joints-fixation-accessoires-dirt-bike',
    'https://www.minimx.fr/fr/177-bastos',
    'https://www.minimx.fr/fr/178-housse-de-selle',
    'https://www.minimx.fr/fr/179-pieces-supermotard',
    'https://www.minimx.fr/fr/18-roue-et-pneumatique-dirt-bike',
    'https://www.minimx.fr/fr/181-visserie-generale',
    'https://www.minimx.fr/fr/189-pieces-trail-bike',
    'https://www.minimx.fr/fr/19-chambre-a-air-et-bouchon-de-valve',
    'https://www.minimx.fr/fr/192-durites-d-essence-de-couleur-pour-dirt-bike',
    'https://www.minimx.fr/fr/20-pneu',
    'https://www.minimx.fr/fr/21-jante-et-roue-complete',
    'https://www.minimx.fr/fr/22-axe-et-roulement',
    'https://www.minimx.fr/fr/230-maillots',
    'https://www.minimx.fr/fr/231-pantalons',
    'https://www.minimx.fr/fr/232-pack-maillot-pantalon',
    'https://www.minimx.fr/fr/233-equipement-pour-enfant-motocross',
    'https://www.minimx.fr/fr/235-casques-enfant-motocross',
    'https://www.minimx.fr/fr/236-gants-enfants',
    'https://www.minimx.fr/fr/237-maillots-pantalons-enfant-motocross',
    'https://www.minimx.fr/fr/238-batterie-chargeur-controlleur',
    'https://www.minimx.fr/fr/24-frein-pedale-plaquette-disques-pour-dirt-bike',
    'https://www.minimx.fr/fr/25-disques-et-durite-de-freins-dirt-bike',
    'https://www.minimx.fr/fr/250-antivol',
    'https://www.minimx.fr/fr/251-accessoires',
    'https://www.minimx.fr/fr/254-pieces-detachees-dirt-bike-et-pit-bike-occasion',
    'https://www.minimx.fr/fr/27-kit-de-frein-dirt-bike',
    'https://www.minimx.fr/fr/28-plaquette-de-frein',
    'https://www.minimx.fr/fr/284-compteur-d-heure-pour-moteur-dirt-bike',
    'https://www.minimx.fr/fr/29-pedale-et-levier-de-frein',
    'https://www.minimx.fr/fr/3-dirt-bike-mini-mx',
    'https://www.minimx.fr/fr/3-dirt-bike-mini-mx?page=1',
    'https://www.minimx.fr/fr/30-pieces-electriques-et-allumages-dirt-bike',
    'https://www.minimx.fr/fr/305-pocket-bike',
    'https://www.minimx.fr/fr/306-pocket-bike',
    'https://www.minimx.fr/fr/306-pocket-cross-thermique',
    'https://www.minimx.fr/fr/31-bobine-et-bougie-dirt-bike',
    'https://www.minimx.fr/fr/310-marques-dirt-bike-pitbike-motocross',
    'https://www.minimx.fr/fr/317-gicleur-ralentiprincipal',
    'https://www.minimx.fr/fr/318-sportswear',
    'https://www.minimx.fr/fr/320-bottes-enfants-motocross',
    'https://www.minimx.fr/fr/321-protections-motocross-enfant',
    'https://www.minimx.fr/fr/325-suspension-haut-de-gamme',
    'https://www.minimx.fr/fr/327-taille-de-roue-grande-roue-dirt-bike',
    'https://www.minimx.fr/fr/328-dirt-bike-10-12-petites-roues',
    'https://www.minimx.fr/fr/329-dirt-bike-12-14-taille-standard',
    'https://www.minimx.fr/fr/33-boitier-cdi-dirt-bike-et-motocross',
    'https://www.minimx.fr/fr/330-dirt-bike-grandes-roues-14-arriere-et-17-avant',
    'https://www.minimx.fr/fr/334-motocross-16-19-grandes-roues',
    'https://www.minimx.fr/fr/335-masques-motocross-enfant',
    'https://www.minimx.fr/fr/337-pieces-pw50',
    'https://www.minimx.fr/fr/338-pieces-pw80',
    'https://www.minimx.fr/fr/34-coupe-circuit-dirt-bike',
    'https://www.minimx.fr/fr/346-les-motocross-250cc',
    'https://www.minimx.fr/fr/35-faisceau-electrique',
    'https://www.minimx.fr/fr/350-huiles-moteurs-pour-moteur',
    'https://www.minimx.fr/fr/354-les-bons-plans',
    'https://www.minimx.fr/fr/355-les-bons-plans-equipement-enfant-motocross',
    'https://www.minimx.fr/fr/36-plateau-d-allumage-dirt-bike',
    'https://www.minimx.fr/fr/362-moteur-ycf-engine-pour-dirt-bike',
    'https://www.minimx.fr/fr/363-pieces-pocket-bike-cross',
    'https://www.minimx.fr/fr/364-pieces-detachees-quad-4-temps',
    'https://www.minimx.fr/fr/365-carburateurs-pocket-bike',
    'https://www.minimx.fr/fr/367-pieces-moteur-pocket-bike',
    'https://www.minimx.fr/fr/37-pieces-carter-moteur-d-allumage-dirt-bike',
    'https://www.minimx.fr/fr/370-pieces-electrique-et-allumage-pocket-bike',
    'https://www.minimx.fr/fr/374-partie-cycle-pocket-bike',
    'https://www.minimx.fr/fr/375-guidon-commande-pocket-bike',
    'https://www.minimx.fr/fr/376-chaine-et-transmission-pocket-bike',
    'https://www.minimx.fr/fr/378-roue-et-pneumatique-pour-pocket-bike',
    'https://www.minimx.fr/fr/379-freinage-pocket-bike',
    'https://www.minimx.fr/fr/38-partie-cycle-dirt-bike',
    'https://www.minimx.fr/fr/384-echappement-pour-pocket-bike',
    'https://www.minimx.fr/fr/386-kit-plastique-reservoir-et-selle-pour-pocket-bike',
    'https://www.minimx.fr/fr/39-suspensions-dirt-bike',
    'https://www.minimx.fr/fr/390-bottes-et-chaussettes',
    'https://www.minimx.fr/fr/391-Pieces-Detachees-Mini-Moto-YAMAHA-PW50-et-PW80',
    'https://www.minimx.fr/fr/392-vehicules-pocket-cross-et-pocket-electrique',
    'https://www.minimx.fr/fr/40-amortisseurs-dirt-bike',
    'https://www.minimx.fr/fr/41-fourche-dirt-bike',
    'https://www.minimx.fr/fr/410-les-marques-pocket-bike-thermique-et-electrique',
    'https://www.minimx.fr/fr/411-crz',
    'https://www.minimx.fr/fr/412-kerox',
    'https://www.minimx.fr/fr/413-les-cylindrees-de-pocket-bike-thermique-et-electrique',
    'https://www.minimx.fr/fr/414-49cc-enfant-de-3-a-8ans',
    'https://www.minimx.fr/fr/416-pocket-cross-electriques',
    'https://www.minimx.fr/fr/419-motocross',
    'https://www.minimx.fr/fr/42-te-pontets-protection-de-fourche',
    'https://www.minimx.fr/fr/420-ktm-50sx',
    'https://www.minimx.fr/fr/421-ktm-65sx',
    'https://www.minimx.fr/fr/422-ktm-85sx',
    'https://www.minimx.fr/fr/43-bras-oscillant-et-cadre',
    'https://www.minimx.fr/fr/451-ktm-125sx',
    'https://www.minimx.fr/fr/476-les-mini-moto-electriques',
    'https://www.minimx.fr/fr/477-pieces-pocket-quad',
    'https://www.minimx.fr/fr/48-cale-pied-et-bequille',
    'https://www.minimx.fr/fr/488-pieces-detachees-kerox-efat-crz-ekid',
    'https://www.minimx.fr/fr/49-reservoir-et-bouchon',
    'https://www.minimx.fr/fr/5-gunshot-dirt-bike-pit-bike',
    'https://www.minimx.fr/fr/50-sabot-moteur',
    'https://www.minimx.fr/fr/500-outlet',
    'https://www.minimx.fr/fr/501-equipement-du-pilote',
    'https://www.minimx.fr/fr/502-maillots-pantalons',
    'https://www.minimx.fr/fr/503-equipement-pour-enfant',
    'https://www.minimx.fr/fr/504-casques',
    'https://www.minimx.fr/fr/505-masques-protections',
    'https://www.minimx.fr/fr/506-gants',
    'https://www.minimx.fr/fr/508-bottes-et-chaussettes',
    'https://www.minimx.fr/fr/509-bottes',
    'https://www.minimx.fr/fr/510-casques',
    'https://www.minimx.fr/fr/511-gants',
    'https://www.minimx.fr/fr/512-maillots-pantalons',
    'https://www.minimx.fr/fr/513-protections',
    'https://www.minimx.fr/fr/515-maillots',
    'https://www.minimx.fr/fr/516-pantalons',
    'https://www.minimx.fr/fr/517-packs-maillot-pantalon',
    'https://www.minimx.fr/fr/519-motocross-18-21',
    'https://www.minimx.fr/fr/521-configurateur-de-transmission',
    'https://www.minimx.fr/fr/533-les-dirt-bike-et-pit-bike-160cc',
    'https://www.minimx.fr/fr/535-les-pit-bike-et-dirt-bike-190cc',
    'https://www.minimx.fr/fr/54-moteurs-complets',
    'https://www.minimx.fr/fr/540-pieces-detachees-motocross-erz-250-pro-big-mx-250-300s',
    'https://www.minimx.fr/fr/542-pieces-motocross-crz-erz-150cc-et-250cc',
    'https://www.minimx.fr/fr/549-pieces-detachees-demarreur-electrique',
    'https://www.minimx.fr/fr/55-yx-moteur-dirt-bike',
    'https://www.minimx.fr/fr/550-boite-a-air',
    'https://www.minimx.fr/fr/552-visseries-protections-accessoires',
    'https://www.minimx.fr/fr/553-maitre-cylindre',
    'https://www.minimx.fr/fr/554-etrier-de-frein',
    'https://www.minimx.fr/fr/555-pocket-quad-2t-quad-4t',
    'https://www.minimx.fr/fr/556-Pocket-Quad-Quad-Electrique-et-Quad-4-Temps',
    'https://www.minimx.fr/fr/557-pocket-quad-2-temps-pour-enfant',
    'https://www.minimx.fr/fr/558-quad-4-temps-pour-enfant',
    'https://www.minimx.fr/fr/559-quad-electriques-pour-enfant',
    'https://www.minimx.fr/fr/56-lifan-moteur-dirt-bike',
    'https://www.minimx.fr/fr/560-les-marques-de-pocket-bike-et-quad',
    'https://www.minimx.fr/fr/561-crz',
    'https://www.minimx.fr/fr/562-kerox',
    'https://www.minimx.fr/fr/563-diamon',
    'https://www.minimx.fr/fr/564-probike',
    'https://www.minimx.fr/fr/565-les-cylindrees-pocket-quad-49cc-et-quad-110cc',
    'https://www.minimx.fr/fr/566-49cc-enfant-de-3-a-8-ans',
    'https://www.minimx.fr/fr/567-110cc-enfant-de-8-a-12-ans',
    'https://www.minimx.fr/fr/568-125cc-enfant-de-10-a-15-ans',
    'https://www.minimx.fr/fr/57-pieces-moteur',
    'https://www.minimx.fr/fr/574-les-prix-pocket-quad-thermique-et-electrique',
    'https://www.minimx.fr/fr/575-de-299-a-499',
    'https://www.minimx.fr/fr/576-de-499-a-799',
    'https://www.minimx.fr/fr/577-de-799-a-999',
    'https://www.minimx.fr/fr/578-taille-de-roues',
    'https://www.minimx.fr/fr/579-4-petites-roues',
    'https://www.minimx.fr/fr/58-piece-chaine-et-transmission-dirt-bike',
    'https://www.minimx.fr/fr/580-6-taille-standard',
    'https://www.minimx.fr/fr/581-7-grandes-roues',
    'https://www.minimx.fr/fr/583-8-grandes-roues',
    'https://www.minimx.fr/fr/584-carburation',
    'https://www.minimx.fr/fr/585-echappement',
    'https://www.minimx.fr/fr/586-guidon-commande',
    'https://www.minimx.fr/fr/587-habillage',
    'https://www.minimx.fr/fr/588-pieces-moteur',
    'https://www.minimx.fr/fr/589-pieces-electriques',
    'https://www.minimx.fr/fr/59-chaine-dirt-bike',
    'https://www.minimx.fr/fr/590-roue-et-pneumatique',
    'https://www.minimx.fr/fr/591-partie-cycle',
    'https://www.minimx.fr/fr/592-transmission',
    'https://www.minimx.fr/fr/593-freinage',
    'https://www.minimx.fr/fr/594-carburation',
    'https://www.minimx.fr/fr/595-echappement',
    'https://www.minimx.fr/fr/596-freinage',
    'https://www.minimx.fr/fr/597-guidon-commande',
    'https://www.minimx.fr/fr/598-habillage',
    'https://www.minimx.fr/fr/599-piece-moteur',
    'https://www.minimx.fr/fr/6-pieces-detachees',
    'https://www.minimx.fr/fr/60-couronne-et-pignon',
    'https://www.minimx.fr/fr/600-pieces-electriques',
    'https://www.minimx.fr/fr/601-roue-et-pneumatique',
    'https://www.minimx.fr/fr/602-partie-cycle',
    'https://www.minimx.fr/fr/603-transmission',
    'https://www.minimx.fr/fr/605-pieces-detachees-minimx-drift-lx',
    'https://www.minimx.fr/fr/613-pieces-detachees-pocket-electriques',
    'https://www.minimx.fr/fr/614-pieces-detachees-quad-electrique',
    'https://www.minimx.fr/fr/615-equipement-vtt',
    'https://www.minimx.fr/fr/616-velo-electrique-ville-et-vtt',
    'https://www.minimx.fr/fr/617-velo-electrique-pliant-crz',
    'https://www.minimx.fr/fr/618-vtt-electrique',
    'https://www.minimx.fr/fr/619-vtc-electrique',
    'https://www.minimx.fr/fr/62-tendeurs-de-chaine-et-guide-chaine',
    'https://www.minimx.fr/fr/620-casques',
    'https://www.minimx.fr/fr/621-maillots-pantalons',
    'https://www.minimx.fr/fr/622-protections',
    'https://www.minimx.fr/fr/623-gants',
    'https://www.minimx.fr/fr/628-pit-bike-12-12-supermotard',
    'https://www.minimx.fr/fr/629-les-motocross-300cc',
    'https://www.minimx.fr/fr/630-vehicule-electrique-pour-enfant',
    'https://www.minimx.fr/fr/631-voitures-electrique-pour-enfant',
    'https://www.minimx.fr/fr/632-voiture-electrique-buggy-4x4-pour-enfant',
    'https://www.minimx.fr/fr/633-draisienne-electrique-pour-enfant',
    'https://www.minimx.fr/fr/634-2-roues-pour-enfant-adolescent',
    'https://www.minimx.fr/fr/636-pieces-detachees-pour-draisienne-crz',
    'https://www.minimx.fr/fr/64-bas-moteur-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/642-mini-mx',
    'https://www.minimx.fr/fr/647-moteur-complet-zongshen',
    'https://www.minimx.fr/fr/648-pieces-detachees-motocross-crz-erz-300-liquide',
    'https://www.minimx.fr/fr/649-quad-electrique-pour-enfant',
    'https://www.minimx.fr/fr/65-arbre-de-boite-et-de-kick-dirt-bike',
    'https://www.minimx.fr/fr/650-moto-enfant-adolescent',
    'https://www.minimx.fr/fr/652-voiture-electrique-pour-enfant',
    'https://www.minimx.fr/fr/659-les-electriques',
    'https://www.minimx.fr/fr/660-les-electriques',
    'https://www.minimx.fr/fr/664-selection-motos-enfant',
    'https://www.minimx.fr/fr/665-motocross-par-cylindree',
    'https://www.minimx.fr/fr/666-motocross-150cc',
    'https://www.minimx.fr/fr/667-motocross-250cc',
    'https://www.minimx.fr/fr/668-les-motocross-300cc',
    'https://www.minimx.fr/fr/669-motocross-par-marque',
    'https://www.minimx.fr/fr/67-pieces-carter-moteur-dirt-bike',
    'https://www.minimx.fr/fr/670-motocross-crz-erz',
    'https://www.minimx.fr/fr/671-motocross-bastos',
    'https://www.minimx.fr/fr/672-motocross-mini-mx',
    'https://www.minimx.fr/fr/673-motocross-gunshot',
    'https://www.minimx.fr/fr/674-motocross-par-taille-de-roue',
    'https://www.minimx.fr/fr/675-motocross-16-arriere-19-avant',
    'https://www.minimx.fr/fr/676-motocross-18-arriere-et-21-avant',
    'https://www.minimx.fr/fr/677-pieces-par-vehicule',
    'https://www.minimx.fr/fr/68-pieces-carter-d-allumage-bas-moteur-dirt-bike',
    'https://www.minimx.fr/fr/69-embrayage-et-vilebrequin-dirt-bike',
    'https://www.minimx.fr/fr/7-guidon-commande-dirt-bike-pit-bike',
    'https://www.minimx.fr/fr/703-bastos-mxr-150cc250cc',
    'https://www.minimx.fr/fr/705-bastos-rsr-250cc',
    'https://www.minimx.fr/fr/707-pieces-ktm',
    'https://www.minimx.fr/fr/71-haut-moteur-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/717-gunshot-150-250cc-mx-1',
    'https://www.minimx.fr/fr/718-gunshot-250cc-mx-2',
    'https://www.minimx.fr/fr/719-gunshot-250cc-mx-3',
    'https://www.minimx.fr/fr/72-culasse-et-cylindre-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/735-motocross-probike',
    'https://www.minimx.fr/fr/736-les-motocross-450cc',
    'https://www.minimx.fr/fr/737-les-450cc',
    'https://www.minimx.fr/fr/739-60cc-enfant-de-6-a-12ans',
    'https://www.minimx.fr/fr/74-pistons-et-segments',
    'https://www.minimx.fr/fr/740-150cc-adultes-a-partir-14-ans',
    'https://www.minimx.fr/fr/741-200cc-adultes-a-partir-16-ans',
    'https://www.minimx.fr/fr/742-de-999-a-1999',
    'https://www.minimx.fr/fr/743-10-grandes-roues',
    'https://www.minimx.fr/fr/744-quad-adultes-a-partir-de-14-ans',
    'https://www.minimx.fr/fr/745-motocross-kayo-motors',
    'https://www.minimx.fr/fr/748-pro-bike',
    'https://www.minimx.fr/fr/749-les-110cc',
    'https://www.minimx.fr/fr/75-pochette-de-joints-lifan-yx-dirt-bike',
    'https://www.minimx.fr/fr/750-type-d-embrayage',
    'https://www.minimx.fr/fr/751-full-automatique',
    'https://www.minimx.fr/fr/752-semi-automatique',
    'https://www.minimx.fr/fr/753-manuel',
    'https://www.minimx.fr/fr/76-radiateur-dirt-bike',
    'https://www.minimx.fr/fr/766-moteurs-4-temps',
    'https://www.minimx.fr/fr/767-moteurs-2-temps',
    'https://www.minimx.fr/fr/768-diamon',
    'https://www.minimx.fr/fr/77-echappement',
    'https://www.minimx.fr/fr/771-moto-dax-skyteam-homologue',
    'https://www.minimx.fr/fr/772-thermique-a-essencemoto-dax-skyteam-thermique-50cc-et-125cc',
    'https://www.minimx.fr/fr/773-electrique',
    'https://www.minimx.fr/fr/775-erz-450cc-r',
    'https://www.minimx.fr/fr/777-14-17-',
    'https://www.minimx.fr/fr/778-voiture-rc-telecommande-electrique',
    'https://www.minimx.fr/fr/781-jusqu-a-48km-h',
    'https://www.minimx.fr/fr/782-les-electriques',
    'https://www.minimx.fr/fr/784-pieces-detachees-voitures-rc-electrique',
    'https://www.minimx.fr/fr/785-pieces-detachees-dax-skyteam',
    'https://www.minimx.fr/fr/787-allumage',
    'https://www.minimx.fr/fr/789-carburation',
    'https://www.minimx.fr/fr/791-poste-de-commande',
    'https://www.minimx.fr/fr/793-echappement',
    'https://www.minimx.fr/fr/795-freinage',
    'https://www.minimx.fr/fr/797-partie-cycle',
    'https://www.minimx.fr/fr/799-roue-et-pneumatique',
    'https://www.minimx.fr/fr/8-cable-d-embrayage-et-d-accelerateur-dirt-bike',
    'https://www.minimx.fr/fr/80-carburateur-et-filtre-dirt-bike',
    'https://www.minimx.fr/fr/801-pieces-moteur',
    'https://www.minimx.fr/fr/803-moteur-complet',
    'https://www.minimx.fr/fr/805-chaine-et-transmission',
    'https://www.minimx.fr/fr/81-carburateur-dirt-bike',
    'https://www.minimx.fr/fr/82-pipe-d-admission-joints-manchons',
    'https://www.minimx.fr/fr/825-kayo-xtrem',
    'https://www.minimx.fr/fr/827-non-electrique',
    'https://www.minimx.fr/fr/829-electrique',
    'https://www.minimx.fr/fr/831-pieces-detachees',
    'https://www.minimx.fr/fr/833-vehicules',
    'https://www.minimx.fr/fr/835-sur-ron',
    'https://www.minimx.fr/fr/84-filtres-a-air-et-essence',
    'https://www.minimx.fr/fr/847-pieces-sur-ron',
    'https://www.minimx.fr/fr/85-equipements-entretien',
    'https://www.minimx.fr/fr/851-erz-450cc-sx',
    'https://www.minimx.fr/fr/853-partie-cycle',
    'https://www.minimx.fr/fr/855-commande',
    'https://www.minimx.fr/fr/857-transmission',
    'https://www.minimx.fr/fr/859-freinage',
    'https://www.minimx.fr/fr/86-equipement-du-pilote',
    'https://www.minimx.fr/fr/861-pieces-moteur',
    'https://www.minimx.fr/fr/863-habillage',
    'https://www.minimx.fr/fr/865-roue-et-pneumatique',
    'https://www.minimx.fr/fr/87-casques-dirt-bike',
    'https://www.minimx.fr/fr/879-electrique',
    'https://www.minimx.fr/fr/88-masques-motocross',
    'https://www.minimx.fr/fr/885-joints-roulements-visseries-axe-de-colonne',
    'https://www.minimx.fr/fr/887-crz-bull-200cc',
    'https://www.minimx.fr/fr/89-gants-dirt-bike',
    'https://www.minimx.fr/fr/9-guidon-pontet-mousse-dirt-bike',
    'https://www.minimx.fr/fr/90-protections-motocross',
    'https://www.minimx.fr/fr/91-accessoires-dirt-bike',
    'https://www.minimx.fr/fr/93-huiles-et-lubrifiants',
    'https://www.minimx.fr/fr/94-outillage',
    'https://www.minimx.fr/fr/boitier-cdi-dirt-bike-et-motocross/1389-boitier-cdi-v2-reprogramme-pour-dirt-bike-3667155001954.html?fast_search=fs',
    'https://www.minimx.fr/fr/brand/106-thor',
    'https://www.minimx.fr/fr/brand/121-kenny',
    'https://www.minimx.fr/fr/brand/122-pull',
    'https://www.minimx.fr/fr/brand/128-pro-bike',
    'https://www.minimx.fr/fr/brand/137-o-neal',
    'https://www.minimx.fr/fr/brand/140-ycf-parts',
    'https://www.minimx.fr/fr/brand/151-fox-racing',
    'https://www.minimx.fr/fr/brand/161-putoline',
    'https://www.minimx.fr/fr/brand/174-mbf',
    'https://www.minimx.fr/fr/brand/186-kerox',
    'https://www.minimx.fr/fr/brand/193-offmx',
    'https://www.minimx.fr/fr/brand/40-shot',
    'https://www.minimx.fr/fr/brand/44-daytona',
    'https://www.minimx.fr/fr/brand/55-100',
    'https://www.minimx.fr/fr/brand/65-trail-bike-parts',
    'https://www.minimx.fr/fr/brand/72-doma-racing',
    'https://www.minimx.fr/fr/brand/80-varetti',
    'https://www.minimx.fr/fr/brand/84-formula',
    'https://www.minimx.fr/fr/brand/88-ipone',
    'https://www.minimx.fr/fr/brand/93-faba',
    'https://www.minimx.fr/fr/carburateur-et-filtre/1033-pack-complet-carburateur-26mm-mikuni-avec-filtre-a-air-dirt-bike-3667155052338.html',
    'https://www.minimx.fr/fr/crz/11735-147645-quad-crz-weely-110cc-bleu.html#/692-pack_entretien_4t-sans_option',
    'https://www.minimx.fr/fr/dirt-bike-pit-bike-crz-erz/16000-pit-bike-crz-fury-double-pot-60cc-2t-10-12-orange-2024-3667155022935.html',
    'https://www.minimx.fr/fr/dirt-bike-pit-bike-crz-erz/16568-pocket-bike-crz-fury-double-pot-49cc-2t-1010-bleu-2024-3667155023192.html',
    'https://www.minimx.fr/fr/pocket-quad-2-temps-pour-enfant/11367-135467-pocket-quad-crz-weely-49cc-vert-3667155100756.html#/687-pack_entretien_2t-sans_option',
    'https://www.minimx.fr/fr/roue-complete/571-pack-de-roue-complete-14-17-dirt-bike-3667155051966.html',
    'https://www.minimx.fr/hsq-m/15866-kit-decoration-montser-hsq-m.html?fast_search=fs',
    'https://www.minimx.fr/index.php?id_category=672&controller=category&id_lang=2',
    'https://www.minimx.fr/index.php?id_product=12584&controller=product&id_lang=2',
    'https://www.minimx.fr/index.php?id_product=18319&controller=product&id_lang=2',
    'https://www.minimx.fr/levier-d-embrayage-et-frein-dirt-bike/12562-levier-d-embrayage-pro-taper-profile-perch-pour-dirt-bike.html',
    'https://www.minimx.fr/pack-pieces-moteur/3843-pack-piston-segment-pochette-140yx.html',
    'https://www.minimx.fr/pack-pieces-moteur/818-pack-piston-segment-pochette-140cc-yx-dirt-bike.html',
    'https://www.minimx.fr/plateau-d-allumage-dirt-bike/290-allumage-rotor-interne-dirt-bike-3700944410435.html',
]

CATEGORY_URLS = list(set(CATEGORY_URLS))

# Directory and output files
DATA_DIR = 'stock_data'
CHANGES_LOG_FILE = 'stock_data/changes_log.csv'


def round_float(value, decimals=2):
    """Round float value to specified decimal places"""
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return 0.0


def get_headers():
    """Generate headers to mimic a browser."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.minimx.fr/',
    }


def setup_directories():
    """Create directories for data if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_timestamped_filename():
    """Get filename with timestamp for products data"""
    now = datetime.now()
    return f"stock_data/{now.strftime('%Y-%m-%d_%H-%M')}.csv"


def get_product_links(session, category_url):
    """Extract product links from a category page, handling pagination."""
    product_links = []
    page = 1
    max_pages = 20
    previous_page_products = set()

    while page <= max_pages:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        try:
            logging.info(f"Fetching page {page} of {category_url}")
            response = session.get(url, headers=get_headers(), timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            products_container = soup.select_one('#products')
            if not products_container:
                logging.info(f"No products container found on page {page} of {category_url}")
                break

            products = products_container.select('a.product-thumbnail')
            if not products:
                logging.info(f"No more products found on page {page} of {category_url}")
                break

            pagination = soup.select_one('.pagination')
            if pagination:
                next_disabled = pagination.select_one('.next.disabled') or not pagination.select_one('.next')
                if next_disabled:
                    logging.info(f"Reached last page ({page}) for {category_url}")

            current_page_products = set()
            current_page_links = []

            for product in products:
                href = product.get('href')
                if href and '/fr/' in href and 'index.php' not in href:
                    product_id = re.search(r'/(\d+)-', href)
                    product_id = product_id.group(1) if product_id else None
                    if product_id:
                        current_page_products.add(product_id)
                        current_page_links.append({
                            'url': href,
                            'id_product': product_id,
                            'category_url': category_url
                        })

            if current_page_products and current_page_products == previous_page_products:
                logging.warning(
                    f"Detected duplicate products on page {page} of {category_url}, breaking pagination loop")
                break

            if page > 1 and len(current_page_products) == len(previous_page_products) and all(
                    pid in previous_page_products for pid in current_page_products):
                logging.warning(
                    f"Page {page} appears to contain the same products as previous page for {category_url}, stopping pagination")
                break

            if not current_page_links:
                logging.info(f"No new products found on page {page} of {category_url}")
                break

            product_links.extend(current_page_links)
            previous_page_products = current_page_products

            logging.info(f"Found {len(current_page_links)} products on page {page} of {category_url}")
            page += 1
            time.sleep(3)
        except requests.RequestException as e:
            logging.error(f"Error fetching category page {url}: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error processing page {page} of {category_url}: {e}")
            break

    if page > max_pages:
        logging.warning(f"Reached maximum page limit ({max_pages}) for {category_url}")

    logging.info(f"Total of {len(product_links)} products found for {category_url}")
    return product_links


def get_all_products(session):
    """Get all product links by scanning category pages."""
    all_products = []
    for category_url in CATEGORY_URLS:
        logging.info(f"Scraping category: {category_url}")
        try:
            products = get_product_links(session, category_url)
            all_products.extend(products)
            time.sleep(3)
        except Exception as e:
            logging.error(f"Error processing category {category_url}: {e}")
            continue

    # Remove duplicates based on product ID
    seen_ids = set()
    unique_products = []
    for product in all_products:
        if product.get('id_product') and product['id_product'] not in seen_ids:
            unique_products.append(product)
            seen_ids.add(product['id_product'])

    logging.info(f"Total unique products found: {len(unique_products)}")
    return unique_products


def extract_product_details(session, product):
    """Extract detailed product information from product page."""
    try:
        response = session.get(product['url'], headers=get_headers(), timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize default values
        reference = ""
        meta_title = ""
        price_without_reduction = 0
        discount_amount = 0
        price = 0
        available_date = ""
        stock_quantity = 0
        quantity_all_versions = 0

        # Extract meta title from page title
        title_tag = soup.find('title')
        if title_tag:
            meta_title = title_tag.get_text(strip=True)

        # Try to extract product details from JSON data
        product_details_elem = soup.select_one('#product-details')
        if product_details_elem and 'data-product' in product_details_elem.attrs:
            try:
                product_json = json.loads(product_details_elem['data-product'])

                reference = product_json.get('reference', '')
                stock_quantity = product_json.get('quantity', 0)
                quantity_all_versions = product_json.get('quantity_all_versions', 0)
                price = product_json.get('price_amount', 0)
                price_without_reduction = product_json.get('price_without_reduction', price)

                if price_without_reduction and price:
                    discount_amount = float(price_without_reduction) - float(price)
                else:
                    discount_amount = 0

                available_date = product_json.get('available_date', '')

            except (json.JSONDecodeError, KeyError) as json_err:
                logging.error(f"Error parsing product JSON for {product['url']}: {json_err}")

        # Alternative extraction methods if JSON parsing fails
        if not reference:
            ref_elem = soup.select_one('[data-product-reference]')
            if ref_elem:
                reference = ref_elem.get('data-product-reference', '')
            else:
                ref_patterns = [
                    soup.select_one('.product-reference'),
                    soup.select_one('.reference'),
                    soup.select_one('[class*="reference"]')
                ]
                for elem in ref_patterns:
                    if elem:
                        reference = elem.get_text(strip=True).replace('Référence:', '').strip()
                        break

        if not price:
            price_elem = soup.select_one('.price, .current-price, [class*="price"]')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', '.'))
                if price_match:
                    price = float(price_match.group())

        if not price_without_reduction:
            original_price_elem = soup.select_one('.regular-price, .old-price, [class*="original"]')
            if original_price_elem:
                price_text = original_price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', '.'))
                if price_match:
                    price_without_reduction = float(price_match.group())
            else:
                price_without_reduction = price

        if price_without_reduction and price and not discount_amount:
            discount_amount = float(price_without_reduction) - float(price)

        return {
            'id_product': product['id_product'],
            'reference': reference,
            'meta_title': meta_title,
            'url': product['url'],
            'category_url': product['category_url'],
            'price_without_reduction': round_float(price_without_reduction),
            'discount_amount': round_float(discount_amount),
            'price': round_float(price),
            'available_date': available_date,
            'stock_quantity': int(stock_quantity),
            'quantity_all_versions': int(quantity_all_versions)
        }

    except requests.RequestException as e:
        logging.error(f"Error fetching product details for {product['url']}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error extracting product details for {product['url']}: {e}")
        return None


def validate_product_data(product):
    """Validate that product data has required fields"""
    required_fields = ['id_product', 'reference', 'meta_title', 'url', 'category_url', 
                      'price_without_reduction', 'discount_amount', 'price', 
                      'available_date', 'stock_quantity', 'quantity_all_versions']
    
    for field in required_fields:
        if field not in product:
            logging.warning(f"Missing required field '{field}' in product data")
            return False
    
    return True


def load_previous_data():
    """Load previous data from the most recent file with error handling"""
    # Find all CSV files that match our naming pattern
    pattern = os.path.join(DATA_DIR, '*-*.csv')  # matches YYYY-MM-DD_HH-MM.csv
    product_files = glob.glob(pattern)
    
    # Filter out changes_log.csv
    product_files = [f for f in product_files if not f.endswith('changes_log.csv')]
    
    if not product_files:
        logging.info("No previous product data files found")
        return None

    # Sort files by datetime in filename (newest first)
    product_files.sort(reverse=True)
    latest_file = product_files[0]
    
    logging.info(f"Loading previous data from: {latest_file}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = []
            for row_num, row in enumerate(reader, 1):
                # Validate that required keys exist
                if 'id_product' not in row:
                    logging.warning(f"Row {row_num} in {latest_file} missing 'id_product' key. Available keys: {list(row.keys())}")
                    continue
                
                # Ensure all required fields have default values if missing
                row.setdefault('price', '0')
                row.setdefault('stock_quantity', '0')
                row.setdefault('reference', '')
                
                data.append(row)
            
            logging.info(f"Successfully loaded {len(data)} products from previous data")
            return data
            
    except Exception as e:
        logging.error(f"Error loading previous data from {latest_file}: {e}")
        return None


def compare_products(current, previous):
    """Compare current products with previous data with improved error handling"""
    if not previous:
        logging.info("No previous data available for comparison")
        return []

    # Create a dictionary from previous data with error handling
    prev_dict = {}
    for p in previous:
        if 'id_product' in p and p['id_product']:
            prev_dict[p['id_product']] = p
        else:
            logging.warning(f"Skipping previous product with missing or empty id_product: {p}")

    changes = []

    for product in current:
        try:
            pid = product.get('id_product')
            if not pid:
                logging.warning(f"Current product missing id_product: {product}")
                continue
                
            if pid in prev_dict:
                prev_product = prev_dict[pid]

                # Safe price comparison
                try:
                    current_price = round_float(product.get('price', 0))
                    previous_price = round_float(prev_product.get('price', 0))
                    price_changed = current_price != previous_price
                except (ValueError, TypeError) as e:
                    logging.warning(f"Error comparing prices for product {pid}: {e}")
                    price_changed = False
                    current_price = 0
                    previous_price = 0

                # Safe stock comparison
                try:
                    current_stock = int(product.get('stock_quantity', 0))
                    previous_stock = int(prev_product.get('stock_quantity', 0))
                    stock_changed = current_stock != previous_stock
                except (ValueError, TypeError) as e:
                    logging.warning(f"Error comparing stock for product {pid}: {e}")
                    stock_changed = False
                    current_stock = 0
                    previous_stock = 0

                if price_changed or stock_changed:
                    changes.append({
                        'id_product': pid,
                        'reference': product.get('reference', ''),
                        'price': current_price,
                        'previous_price': previous_price,
                        'stock_quantity': current_stock,
                        'previous_stock': previous_stock,
                        'price_change': price_changed,
                        'stock_change': stock_changed,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        except Exception as e:
            logging.error(f"Error comparing product {product.get('id_product', 'unknown')}: {e}")
            continue

    return changes


def save_current_data(current_products):
    """Save current products to timestamped file with validation"""
    timestamped_file = get_timestamped_filename()

    try:
        # Validate products before saving
        valid_products = []
        for product in current_products:
            if validate_product_data(product):
                valid_products.append(product)
            else:
                logging.warning(f"Skipping invalid product data: {product}")

        with open(timestamped_file, 'w', newline='', encoding='utf-8') as f:
            if valid_products:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'id_product', 'reference', 'meta_title', 'url', 'category_url',
                    'price_without_reduction', 'discount_amount', 'price', 'available_date',
                    'stock_quantity', 'quantity_all_versions'
                ])
                writer.writeheader()

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for product in valid_products:
                    product_data = product.copy()
                    product_data['timestamp'] = timestamp
                    writer.writerow(product_data)

        logging.info(f"Saved {len(valid_products)} valid products to {timestamped_file}")
        return len(valid_products)

    except Exception as e:
        logging.error(f"Error saving current data: {e}")
        return 0


def save_changes_log(changes):
    """Append changes to the unified changes log file"""
    if not changes:
        return

    # Check if file exists to determine if we need to write header
    file_exists = os.path.exists(CHANGES_LOG_FILE)

    try:
        with open(CHANGES_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write separator and timestamp header
            if file_exists:
                writer.writerow([])  # Empty line for separation

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([f'=== CHANGES DETECTED AT {current_time} ==='])

            # Write column headers
            writer.writerow([
                'timestamp', 'id_product', 'reference',
                'price', 'previous_price', 'price_change',
                'stock_quantity', 'previous_stock', 'stock_change'
            ])

            # Write changes data
            for change in changes:
                writer.writerow([
                    change['timestamp'],
                    change['id_product'],
                    change['reference'],
                    change['price'],
                    change['previous_price'],
                    change['price_change'],
                    change['stock_quantity'],
                    change['previous_stock'],
                    change['stock_change']
                ])

        logging.info(f"Appended {len(changes)} changes to {CHANGES_LOG_FILE}")

    except Exception as e:
        logging.error(f"Error saving changes log: {e}")


def save_no_changes_log():
    """Append 'no changes' entry to the changes log"""
    file_exists = os.path.exists(CHANGES_LOG_FILE)

    try:
        with open(CHANGES_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write separator if file exists
            if file_exists:
                writer.writerow([])  # Empty line for separation

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([f'{current_time} - No changes detected'])

        logging.info(f"Recorded 'no changes' entry in {CHANGES_LOG_FILE}")

    except Exception as e:
        logging.error(f"Error saving no changes log: {e}")


def run_monitor():
    """Daily monitoring function to run at 00:00 with improved error handling"""
    logging.info("Starting daily monitoring cycle...")

    try:
        session = requests.Session()
        session.timeout = 30  # Set session timeout

        # Get all products
        products = get_all_products(session)
        if not products:
            logging.error("No products found!")
            return

        logging.info(f"Found {len(products)} unique products to process")

        # Extract details for all products
        current_products = []
        successful_count = 0
        failed_count = 0
        
        for i, product in enumerate(products, 1):
            try:
                logging.info(f"Processing product {i}/{len(products)}: {product['id_product']}")
                details = extract_product_details(session, product)
                if details and validate_product_data(details):
                    current_products.append(details)
                    successful_count += 1
                else:
                    failed_count += 1
                    logging.warning(f"Failed to extract valid details for product: {product['id_product']}")
                
                time.sleep(2)  # Be nice to the server
                
                # Log progress every 100 products
                if i % 100 == 0:
                    logging.info(f"Progress: {i}/{len(products)} products processed ({successful_count} successful, {failed_count} failed)")
                    
            except Exception as e:
                failed_count += 1
                logging.error(f"Error processing product {product.get('id_product', 'unknown')}: {e}")
                continue

        logging.info(f"Processing completed: {successful_count} successful, {failed_count} failed out of {len(products)} total")

        if not current_products:
            logging.error("No valid products were processed!")
            return

        # Save current products to timestamped file
        saved_count = save_current_data(current_products)
        if saved_count == 0:
            logging.error("Failed to save current data!")
            return

        # Load previous data and compare
        previous_data = load_previous_data()
        changes = compare_products(current_products, previous_data)

        # Save changes to log
        if changes:
            logging.info(f"Detected {len(changes)} changes from previous run")
            save_changes_log(changes)
        else:
            logging.info("No changes detected from previous run")
            save_no_changes_log()

        logging.info("Daily monitoring cycle completed successfully")

    except Exception as e:
        logging.error(f"Fatal error in monitoring cycle: {e}")
        raise


def calculate_next_run_time():
    """Calculate next 00:00 run time"""
    now = datetime.now()
    # Next midnight (tomorrow 00:00)
    next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return next_run


def wait_until_next_run():
    """Wait until next scheduled run time"""
    next_run = calculate_next_run_time()
    wait_seconds = (next_run - datetime.now()).total_seconds()

    if wait_seconds > 0:
        logging.info(f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Waiting {wait_seconds:.0f} seconds until next run...")
        time.sleep(wait_seconds)


def main():
    """Main function with improved error handling"""
    try:
        setup_directories()
        logging.info("Starting daily product monitor (runs at 00:00 each day)")

        # Run immediately on startup
        logging.info("Running initial monitoring cycle...")
        run_monitor()

        # Schedule daily runs at 00:00
        schedule.every().day.at("00:00").do(run_monitor)
        logging.info("Daily scheduler set up. Will run every day at 00:00")

        while True:
            try:
                # Check for scheduled runs
                schedule.run_pending()

                # Sleep for 30 seconds and check again
                time.sleep(30)
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait a bit longer if there's an error
                continue

    except KeyboardInterrupt:
        logging.info("Script stopped by user")
    except Exception as e:
        logging.error(f"Fatal error in main function: {e}")
        raise


if __name__ == '__main__':
    main()