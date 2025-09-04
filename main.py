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
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

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

# Categories for second website structure
CATEGORY_URLS_GROUPED = [
    'https://www.lebonquad.com/',
    'https://www.lebonquad.com/313-quad-enfant-et-pocket-quad',
    'https://www.lebonquad.com/315-quad-enfant-par-marque',
    'https://www.lebonquad.com/317-quad-enfant-lbq',
    'https://www.lebonquad.com/316-quad-enfant-kerox',
    'https://www.lebonquad.com/448-quad-enfant-kayo',
    'https://www.lebonquad.com/494-quad-enfant-probike',
    'https://www.lebonquad.com/558-quad-enfant-diamon',
    'https://www.lebonquad.com/576-quad-enfant-xtrm-factory-81',
    'https://www.lebonquad.com/318-quad-enfant-par-age',
    'https://www.lebonquad.com/319-quad-enfant-3-5-ans',
    'https://www.lebonquad.com/320-quad-enfant-5-8-ans',
    'https://www.lebonquad.com/321-quad-enfant-8-13-ans',
    'https://www.lebonquad.com/449-quad-enfant-13-ans-et-plus',
    'https://www.lebonquad.com/366-quad-enfant-par-energie',
    'https://www.lebonquad.com/367-quad-electrique-enfant',
    'https://www.lebonquad.com/368-quad-thermique-enfant',
    'https://www.lebonquad.com/369-quad-enfant-par-puissance',
    'https://www.lebonquad.com/370-quad-50cc',
    'https://www.lebonquad.com/371-quad-110cc',
    'https://www.lebonquad.com/428-quad-125cc',
    'https://www.lebonquad.com/450-quad-150cc-et-plus',
    'https://www.lebonquad.com/372-quad-electrique-800w',
    'https://www.lebonquad.com/373-quad-electrique-1000w-et-plus',
    'https://www.lebonquad.com/547-quad-par-categorie',
    'https://www.lebonquad.com/548-pocket-quad',
    'https://www.lebonquad.com/549-quad-enfant',
    'https://www.lebonquad.com/550-quad-enfant-ado',
    'https://www.lebonquad.com/551-quad-ado-adulte',
    'https://www.lebonquad.com/328-moto-enfant-par-marque',
    'https://www.lebonquad.com/330-moto-enfant-lbq',
    'https://www.lebonquad.com/329-moto-enfant-kerox',
    'https://www.lebonquad.com/333-moto-enfant-bastos',
    'https://www.lebonquad.com/343-moto-enfant-gunshot',
    'https://www.lebonquad.com/480-moto-enfant-probike',
    'https://www.lebonquad.com/553-moto-enfant-xtrm-factory-81',
    'https://www.lebonquad.com/577-moto-enfant-kingtoys',
    'https://www.lebonquad.com/589-moto-enfant-diamon',
    'https://www.lebonquad.com/634-moto-enfant-kayo',
    'https://www.lebonquad.com/326-moto-enfant-par-age',
    'https://www.lebonquad.com/578-moto-enfant-moins-de-3-ans',
    'https://www.lebonquad.com/331-moto-enfant-3-5-ans',
    'https://www.lebonquad.com/332-moto-enfant-5-8-ans',
    'https://www.lebonquad.com/334-moto-enfant-8-11-ans',
    'https://www.lebonquad.com/335-moto-enfant-11-16-ans',
    'https://www.lebonquad.com/484-moto-enfant-par-energie',
    'https://www.lebonquad.com/485-moto-electrique-enfant',
    'https://www.lebonquad.com/486-moto-thermique-enfant',
    'https://www.lebonquad.com/511-moto-enfant-par-cylindree',
    'https://www.lebonquad.com/579-moto-enfant-18-70w',
    'https://www.lebonquad.com/512-moto-enfant-250w',
    'https://www.lebonquad.com/513-pocket-cross-electrique-550w',
    'https://www.lebonquad.com/515-motocross-enfant-electrique-1000w',
    'https://www.lebonquad.com/516-motocross-enfant-electrique-1300w-et-plus',
    'https://www.lebonquad.com/517-moto-enfant-50-a-70cc',
    'https://www.lebonquad.com/518-moto-enfant-90cc',
    'https://www.lebonquad.com/519-moto-enfant-125cc',
    'https://www.lebonquad.com/451-voiture-enfant',
    'https://www.lebonquad.com/452-voiture-electrique-enfant',
    'https://www.lebonquad.com/453-voiture-electrique-enfant-2-ans',
    'https://www.lebonquad.com/590-voiture-electrique-enfant-3-ans-et-plus',
    'https://www.lebonquad.com/583-buggy-enfant',
    'https://www.lebonquad.com/591-buggy-electrique-enfant',
    'https://www.lebonquad.com/592-buggy-thermique-enfant',
    'https://www.lebonquad.com/584-4x4-enfant',
    'https://www.lebonquad.com/593-4x4-electrique-enfant',
    'https://www.lebonquad.com/594-jeep-willys-enfant',
    'https://www.lebonquad.com/585-quad-enfant-electrique',
    'https://www.lebonquad.com/599-quad-electrique-6v',
    'https://www.lebonquad.com/600-quad-electrique-12v',
    'https://www.lebonquad.com/582-moto-enfant-electrique',
    'https://www.lebonquad.com/597-moto-electrique-6v',
    'https://www.lebonquad.com/598-moto-electrique-12v',
    'https://www.lebonquad.com/595-mini-kart-draisienne-electrique',
    'https://www.lebonquad.com/596-kart-electrique-thermique',
    'https://www.lebonquad.com/601-draisienne-electrique',
    'https://www.lebonquad.com/603-pieces-voiture-enfant',
    'https://www.lebonquad.com/477-produits-reconditionnes',
    'https://www.lebonquad.com/191-pieces-detachees-quad-enfant',
    'https://www.lebonquad.com/199-pieces-moteur-quad-enfant',
    'https://www.lebonquad.com/200-couvercle-culasse',
    'https://www.lebonquad.com/201-cylindre-culasse',
    'https://www.lebonquad.com/202-arbre-a-came-soupape',
    'https://www.lebonquad.com/203-chaine-de-distribution',
    'https://www.lebonquad.com/204-carter-d-embrayage',
    'https://www.lebonquad.com/205-embrayage',
    'https://www.lebonquad.com/206-carter-d-allumage',
    'https://www.lebonquad.com/207-allumage',
    'https://www.lebonquad.com/208-carter-de-boite',
    'https://www.lebonquad.com/209-pompe-a-huile',
    'https://www.lebonquad.com/210-embiellage-piston',
    'https://www.lebonquad.com/211-arbre-de-boite',
    'https://www.lebonquad.com/213-arbre-tambour-selection',
    'https://www.lebonquad.com/214-chaine-couronne-demarreur',
    'https://www.lebonquad.com/215-carburateur-pipe-filtre',
    'https://www.lebonquad.com/216-demarreur-electrique',
    'https://www.lebonquad.com/311-moteur-complet',
    'https://www.lebonquad.com/192-quad-speedbird-panthera',
    'https://www.lebonquad.com/217-chassis',
    'https://www.lebonquad.com/218-train-avant',
    'https://www.lebonquad.com/219-train-arriere',
    'https://www.lebonquad.com/220-direction',
    'https://www.lebonquad.com/221-amortisseur',
    'https://www.lebonquad.com/222-roue-avant',
    'https://www.lebonquad.com/223-roue-arriere',
    'https://www.lebonquad.com/224-freinage',
    'https://www.lebonquad.com/225-electricite',
    'https://www.lebonquad.com/226-guidon-commande',
    'https://www.lebonquad.com/227-reservoir',
    'https://www.lebonquad.com/228-carrosserie-selle',
    'https://www.lebonquad.com/229-echappement',
    'https://www.lebonquad.com/193-quad-bazooka-toronto-bazou',
    'https://www.lebonquad.com/230-chassis',
    'https://www.lebonquad.com/231-train-avant',
    'https://www.lebonquad.com/232-train-arriere',
    'https://www.lebonquad.com/233-direction',
    'https://www.lebonquad.com/234-amortisseur',
    'https://www.lebonquad.com/235-roue-avant',
    'https://www.lebonquad.com/236-roue-arriere',
    'https://www.lebonquad.com/237-freinage',
    'https://www.lebonquad.com/238-electricite',
    'https://www.lebonquad.com/239-guidon-commande',
    'https://www.lebonquad.com/240-reservoir',
    'https://www.lebonquad.com/241-carrosserie-selle',
    'https://www.lebonquad.com/242-echappement',
    'https://www.lebonquad.com/196-quad-puma-bigfoot-bibou',
    'https://www.lebonquad.com/269-chassis',
    'https://www.lebonquad.com/270-train-avant',
    'https://www.lebonquad.com/271-train-arriere',
    'https://www.lebonquad.com/272-direction',
    'https://www.lebonquad.com/273-amortisseur',
    'https://www.lebonquad.com/274-roue-avant',
    'https://www.lebonquad.com/275-roue-arriere',
    'https://www.lebonquad.com/276-freinage',
    'https://www.lebonquad.com/277-electricite',
    'https://www.lebonquad.com/278-guidon-commande',
    'https://www.lebonquad.com/279-reservoir',
    'https://www.lebonquad.com/280-carrosserie-selle',
    'https://www.lebonquad.com/281-echappement',
    'https://www.lebonquad.com/197-quad-raptor-razor',
    'https://www.lebonquad.com/282-chassis',
    'https://www.lebonquad.com/283-train-avant',
    'https://www.lebonquad.com/284-train-arriere',
    'https://www.lebonquad.com/285-direction',
    'https://www.lebonquad.com/286-amortisseur',
    'https://www.lebonquad.com/287-roue-avant',
    'https://www.lebonquad.com/288-roue-arriere',
    'https://www.lebonquad.com/289-freinage',
    'https://www.lebonquad.com/290-electricite',
    'https://www.lebonquad.com/291-guidon-commande',
    'https://www.lebonquad.com/292-reservoir',
    'https://www.lebonquad.com/293-carrosserie-selle',
    'https://www.lebonquad.com/294-echappement',
    'https://www.lebonquad.com/194-quad-mkt-fenix',
    'https://www.lebonquad.com/243-chassis-direction-amortisseur',
    'https://www.lebonquad.com/244-train-avant',
    'https://www.lebonquad.com/245-train-arriere',
    'https://www.lebonquad.com/248-roue-avant',
    'https://www.lebonquad.com/249-roue-arriere',
    'https://www.lebonquad.com/251-electricite',
    'https://www.lebonquad.com/252-guidon-commande-freinage',
    'https://www.lebonquad.com/254-carrosserie-selle-reservoir',
    'https://www.lebonquad.com/255-echappement',
    'https://www.lebonquad.com/382-quad-e-mkt-e-fenix',
    'https://www.lebonquad.com/383-chassis-direction-amortisseur',
    'https://www.lebonquad.com/384-train-avant',
    'https://www.lebonquad.com/385-train-arriere-moteur',
    'https://www.lebonquad.com/386-roue-avant',
    'https://www.lebonquad.com/387-roue-arriere',
    'https://www.lebonquad.com/388-electricite',
    'https://www.lebonquad.com/389-guidon-commande-freinage',
    'https://www.lebonquad.com/390-carrosserie-selle',
    'https://www.lebonquad.com/314-pieces-detachees-quad-pocket',
    'https://www.lebonquad.com/195-quad-rex-speedy',
    'https://www.lebonquad.com/256-chassis',
    'https://www.lebonquad.com/257-train-avant',
    'https://www.lebonquad.com/258-train-arriere',
    'https://www.lebonquad.com/259-direction',
    'https://www.lebonquad.com/260-amortisseur',
    'https://www.lebonquad.com/261-roue',
    'https://www.lebonquad.com/265-guidon-commande',
    'https://www.lebonquad.com/266-reservoir',
    'https://www.lebonquad.com/267-carrosserie-selle',
    'https://www.lebonquad.com/268-echappement',
    'https://www.lebonquad.com/308-moteur-complet',
    'https://www.lebonquad.com/309-embiellage-piston',
    'https://www.lebonquad.com/310-carburateur-pipe-filtre',
    'https://www.lebonquad.com/198-quad-electrique-e-rex-e-speedy',
    'https://www.lebonquad.com/295-chassis-direction-amortisseur',
    'https://www.lebonquad.com/296-train-avant',
    'https://www.lebonquad.com/297-train-arriere',
    'https://www.lebonquad.com/298-arbre-arriere-',
    'https://www.lebonquad.com/300-roue',
    'https://www.lebonquad.com/303-electricite',
    'https://www.lebonquad.com/304-guidon-commande',
    'https://www.lebonquad.com/306-carosserie-selle',
    'https://www.lebonquad.com/391-quad-rock-wokx',
    'https://www.lebonquad.com/401-guidon-commande',
    'https://www.lebonquad.com/402-train-avant',
    'https://www.lebonquad.com/403-chassis-direction-amortisseur',
    'https://www.lebonquad.com/404-echappement-reservoir',
    'https://www.lebonquad.com/406-roue',
    'https://www.lebonquad.com/407-train-arriere',
    'https://www.lebonquad.com/408-arbre-arriere',
    'https://www.lebonquad.com/409-carrosserie-selle',
    'https://www.lebonquad.com/410-moteur-complet',
    'https://www.lebonquad.com/411-embiellage-piston',
    'https://www.lebonquad.com/412-carburateur-pipe-filtre',
    'https://www.lebonquad.com/392-quad-e-rock-e-wokx',
    'https://www.lebonquad.com/393-guidon-commande',
    'https://www.lebonquad.com/394-train-avant',
    'https://www.lebonquad.com/395-chassis-direction-amortisseur',
    'https://www.lebonquad.com/396-train-arriere',
    'https://www.lebonquad.com/397-arbre-arriere',
    'https://www.lebonquad.com/398-roue',
    'https://www.lebonquad.com/399-carrosserie-selle',
    'https://www.lebonquad.com/400-electricite',
    'https://www.lebonquad.com/346-pieces-detachees-moto-enfant',
    'https://www.lebonquad.com/347-mico-xtm-500',
    'https://www.lebonquad.com/349-cadre-bras-oscillant',
    'https://www.lebonquad.com/350-guidon-commande',
    'https://www.lebonquad.com/351-fourche',
    'https://www.lebonquad.com/352-roue-avant',
    'https://www.lebonquad.com/353-moteur-echappement',
    'https://www.lebonquad.com/354-kit-plastique-selle',
    'https://www.lebonquad.com/362-roue-arriere-',
    'https://www.lebonquad.com/348-e-mico-xtm-500-electrique',
    'https://www.lebonquad.com/356-cadre-bras-oscillant',
    'https://www.lebonquad.com/357-guidon-commande',
    'https://www.lebonquad.com/358-fourche',
    'https://www.lebonquad.com/359-roue-avant',
    'https://www.lebonquad.com/363-roue-arriere',
    'https://www.lebonquad.com/361-kit-plastique-selle',
    'https://www.lebonquad.com/364-electricite',
    'https://www.lebonquad.com/374-e-fat-kids-biky',
    'https://www.lebonquad.com/375-guidon-commande',
    'https://www.lebonquad.com/376-electricite',
    'https://www.lebonquad.com/377-freinage',
    'https://www.lebonquad.com/378-roue',
    'https://www.lebonquad.com/379-cadre-fourche',
    'https://www.lebonquad.com/380-transmission',
    'https://www.lebonquad.com/381-kit-plastique-selle',
    'https://www.lebonquad.com/432-e-storm-e-blast-1000w',
    'https://www.lebonquad.com/433-cadre-bras-oscillant',
    'https://www.lebonquad.com/434-guidon-commande',
    'https://www.lebonquad.com/435-fourche',
    'https://www.lebonquad.com/436-roue-avant',
    'https://www.lebonquad.com/437-roue-arriere',
    'https://www.lebonquad.com/438-kit-plastique-selle',
    'https://www.lebonquad.com/439-electricite',
    'https://www.lebonquad.com/495-e-storm-e-blast-1300w',
    'https://www.lebonquad.com/496-cadre-bras-oscillant',
    'https://www.lebonquad.com/497-guidon-commande',
    'https://www.lebonquad.com/498-fourche',
    'https://www.lebonquad.com/499-roue-avant',
    'https://www.lebonquad.com/500-roue-arriere',
    'https://www.lebonquad.com/501-kit-plastique-selle',
    'https://www.lebonquad.com/502-electricite',
    'https://www.lebonquad.com/421-destockage',
    'https://www.lebonquad.com/478-cartes-cadeaux',
    'https://www.lebonquad.com/525-equipement-cross',
    'https://www.lebonquad.com/526-pantalon-de-cross',
    'https://www.lebonquad.com/527-maillot-de-cross',
    'https://www.lebonquad.com/528-casque-de-cross',
    'https://www.lebonquad.com/529-paire-de-gants-cross',
    'https://www.lebonquad.com/530-lunettes-de-cross',
    'https://www.lebonquad.com/531-outils-entretien',
    'https://www.lebonquad.com/532-outils',
    'https://www.lebonquad.com/533-entretien',
    'https://www.lebonquad.com/51-outillage-et-entretien',
    'https://www.lebonquad.com/430-packs-entretien',
    'https://www.lebonquad.com/186-outillage',
    'https://www.lebonquad.com/187-accessoire',
    'https://www.lebonquad.com/188-lubrifiant-nettoyant',
    'https://www.lebonquad.com/413-equipement',
    'https://www.lebonquad.com/419-tenue-cross',
    'https://www.lebonquad.com/414-casque-cross-enfant',
    'https://www.lebonquad.com/415-masque-cross-enfant',
    'https://www.lebonquad.com/416-protection-cross-enfant',
    'https://www.lebonquad.com/418-gants-cross-enfant',
    'https://www.wkx-racing.com/457-pit-bikes-par-marque',
    'https://www.wkx-racing.com/4-pit-bike-wkx',
    'https://www.wkx-racing.com/470-pit-bike-kayo',
    'https://www.wkx-racing.com/43-pit-bike-bastos',
    'https://www.wkx-racing.com/48-pit-bike-gunshot',
    'https://www.wkx-racing.com/481-pit-bike-probike',
    'https://www.wkx-racing.com/312-pit-bike-ycf',
    'https://www.wkx-racing.com/44-pit-bike-pitsterpro',
    'https://www.wkx-racing.com/47-pit-bike-bucci-moto',
    'https://www.wkx-racing.com/602-pit-bike-xtrm-81',
    'https://www.wkx-racing.com/458-pit-bikes-par-age',
    'https://www.wkx-racing.com/466-pit-bikes-5-10-ans',
    'https://www.wkx-racing.com/467-pit-bikes-10-ans-et-plus',
    'https://www.wkx-racing.com/468-pit-bikes-13-ans-et-plus',
    'https://www.wkx-racing.com/469-pit-bikes-16-ans-et-plus',
    'https://www.wkx-racing.com/459-pit-bikes-par-puissance',
    'https://www.wkx-racing.com/460-pit-bikes-50cc',
    'https://www.wkx-racing.com/461-pit-bikes-70cc',
    'https://www.wkx-racing.com/462-pit-bikes-90cc',
    'https://www.wkx-racing.com/463-pit-bikes-125cc',
    'https://www.wkx-racing.com/464-pit-bikes-140cc',
    'https://www.wkx-racing.com/465-pit-bikes-150cc',
    'https://www.wkx-racing.com/471-pit-bikes-190cc',
    'https://www.wkx-racing.com/472-dirt-bikes-250cc',
    'https://www.wkx-racing.com/587-dirt-bikes-300cc',
    'https://www.wkx-racing.com/98-pieces-detachees-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/141-piece-moteur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/169-culasse-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/170-cylindre-piston-dirt-bike-pit-bike',
    'https://www.wkx-racing.com/171-vilebrequin-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/172-joints-moteur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/173-carter-moteur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/174-boite-de-vitesse-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/175-embrayage-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/176-filtre-pompe-a-huile-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/177-radiateur-jauge-bouchon-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/117-roue-pneu-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/123-gripster-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/124-rayon-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/125-axe-de-roue-roulement-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/126-fond-de-jante-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/118-chambre-a-air-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/119-pneu-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/121-jante-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/122-roue-complete-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/116-freinage-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/128-pedale-de-frein-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/129-durite-banjo-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/130-disque-de-frein-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/131-plaquette-de-frein-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/127-kit-frein-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/144-allumage-electricite-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/153-rotor-stator-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/154-boitier-cdi-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/155-bobine-allumage-dirt-bike-pit-bike',
    'https://www.wkx-racing.com/156-bougie-allumage-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/157-coupe-circuit-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/158-faisceau-electrique-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/159-relais-regulateur-batterie-demarreur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/108-transmission-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/113-tendeur-chaine-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/110-couronne-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/111-pignon-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/109-chaine-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/112-kit-chaine',
    'https://www.wkx-racing.com/114-guide-chaine-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/146-kit-plastique-kit-decoration-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/148-kit-plastique-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/147-kit-decoration-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/138-visserie-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/142-moteur-complet-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/167-moteur-lifan-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/166-moteur-daytona-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/168-moteur-yx-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/365-moteur-ycf',
    'https://www.wkx-racing.com/482-moteur-zongshen',
    'https://www.wkx-racing.com/101-commande-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/105-levier-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/107-kick-selecteur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/104-cable-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/103-tirage-poignee-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/102-guidon-pontet-mousse-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/115-suspension-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/134-te-pontet-axe-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/135-protection-de-fourche-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/136-amortisseur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/137-fourche-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/189-roulement-joint-spi-fourche-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/145-reservoir-selle-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/150-robinet-de-reservoir-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/151-event-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/152-reservoir-essence-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/149-bouchon-reservoir-essence-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/190-selle-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/143-partie-cycle-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/160-cadre-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/161-bras-oscillant-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/162-barre-de-repose-pied-bequille-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/164-sabot-moteur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/165-roulement-brас-oscillant-dirt-bike-pit-bike',
    'https://www.wkx-racing.com/140-carburateur-filtre-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/178-carburateur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/179-filtre-a-air-filtre-a-essence-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/180-joint-de-carburateur-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/181-pipe-d-admission-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/139-echappement-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/182-collecteur-silencieux-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/183-bride-joint-divers-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/552-piece-supermotard-pit-bike',
    'https://www.wkx-racing.com/554-pieces-motocross',
    'https://www.wkx-racing.com/563-piece-moteur-dirt-bike-motocross',
    'https://www.wkx-racing.com/564-roue-pneu-dirt-bike-motocross',
    'https://www.wkx-racing.com/565-freinage-dirt-bike-motocross',
    'https://www.wkx-racing.com/566-allumage-electricite-dirt-bike-motocross',
    'https://www.wkx-racing.com/567-transmission-dirt-bike-motocross',
    'https://www.wkx-racing.com/569-commande-dirt-bike-motocross',
    'https://www.wkx-racing.com/570-suspension-dirt-bike-motocross',
    'https://www.wkx-racing.com/571-reservoir-selle-dirt-bike-motocross',
    'https://www.wkx-racing.com/572-partie-cycle-carenage',
    'https://www.wkx-racing.com/573-carburateur-filtre-dirt-bike-motocross',
    'https://www.wkx-racing.com/574-echappement-dirt-bike-motocross',
    'https://www.wkx-racing.com/575-moteur-complet-dirt-bike-motocross',
    'https://www.wkx-racing.com/51-outillage-et-entretien-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/186-outillage-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/187-accessoire-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/188-lubrifiant-nettoyant-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/430-packs-entretien',
    'https://www.wkx-racing.com/413-equipement-pit-bike-dirt-bike',
    'https://www.wkx-racing.com/414-casques',
    'https://www.wkx-racing.com/415-lunettes',
    'https://www.wkx-racing.com/416-protections',
    'https://www.wkx-racing.com/418-gants',
    'https://www.wkx-racing.com/419-tenue',
    'https://www.wkx-racing.com/586-reconditionnes',
    'https://www.wkx-racing.com/421-destockage',
    'https://www.wkx-racing.com/491-pit-bike',
    'https://www.wkx-racing.com/493-pieces-ycf',
    'https://www.wkx-racing.com/534-suspension-echappement-YCF',
    'https://www.wkx-racing.com/535-commande-transmission-YCF',
    'https://www.wkx-racing.com/537-kit-plastique-partie-cycle-YCF',
    'https://www.wkx-racing.com/539-pieces-moteur-carburateur-YCF',
    'https://www.wkx-racing.com/525-equipement-cross',
    'https://www.wkx-racing.com/526-pantalon-cross',
    'https://www.wkx-racing.com/527-maillot-cross',
    'https://www.wkx-racing.com/528-casque-cross',
    'https://www.wkx-racing.com/529-paire-de-gants-cross',
    'https://www.wkx-racing.com/530-lunettes-cross'
]


CATEGORY_URLS = list(set(CATEGORY_URLS))
DATA_DIR = 'stock_data'
CHANGES_LOG_FILE = 'stock_data/changes_log.csv'
CHANGES_LOG_FILE_GROUPED = 'stock_data/changes_log_grouped.csv'


def round_float(value, decimals=2):
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return 0.0


def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.minimx.fr/',
    }


def setup_directories():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_timestamped_filename(date=None, grouped=False):
    if date is None:
        date = datetime.now()
    prefix = "wkx-racing_lebonquad_" if grouped else "minimx_"
    return f"{DATA_DIR}/{prefix}{date.strftime('%Y-%m-%d_%H-%M')}.csv"


def get_daily_filename(date=None, grouped=False):
    if date is None:
        date = datetime.now()
    prefix = "wkx-racing_lebonquad_" if grouped else "minimx_"
    return f"{DATA_DIR}/{prefix}{date.strftime('%Y-%m-%d')}_*.csv"


def check_if_today_file_exists(grouped=False):
    today = datetime.now().date()
    pattern = get_daily_filename(today, grouped)
    files = glob.glob(pattern)
    if files:
        files.sort(reverse=True)
        latest_file = files[0]
        group_type = "grouped" if grouped else "regular"
        logging.info(f"Found existing {group_type} file for today: {latest_file}")
        return True, latest_file
    else:
        group_type = "grouped" if grouped else "regular"
        logging.info(f"No {group_type} file found for today ({today})")
        return False, None


def find_file_by_date(target_date, grouped=False):
    pattern = get_daily_filename(target_date, grouped)
    files = glob.glob(pattern)
    if files:
        files.sort(reverse=True)
        return files[0]
    return None


def load_products_from_csv(filename):
    if not filename or not os.path.exists(filename):
        logging.warning(f"File {filename} does not exist")
        return []

    products = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        logging.info(f"Loaded {len(products)} products from {filename}")
        return products
    except Exception as e:
        logging.error(f"Error loading file {filename}: {e}")
        return []


def validate_product_data(product):
    required_fields = ['id_product']
    return all(field in product and product[field] for field in required_fields)


def compare_products(current, previous):
    if not previous:
        logging.info("No previous data available for comparison")
        return []

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

                try:
                    current_price = round_float(product.get('price', 0))
                    previous_price = round_float(prev_product.get('price', 0))
                    price_changed = current_price != previous_price
                except (ValueError, TypeError) as e:
                    logging.warning(f"Error comparing prices for product {pid}: {e}")
                    price_changed = False
                    current_price = 0
                    previous_price = 0

                try:
                    current_stock = int(product.get('stock_quantity', 0))
                    previous_stock = int(prev_product.get('stock_quantity', 0))
                    stock_changed = current_stock != previous_stock
                    stock_change = previous_stock - current_stock
                except (ValueError, TypeError) as e:
                    logging.warning(f"Error comparing stock for product {pid}: {e}")
                    stock_changed = False
                    current_stock = 0
                    previous_stock = 0
                    stock_change = 0

                if price_changed or stock_changed:
                    transaction = "Vente" if stock_change > 0 else "Appro"
                    ca = abs(stock_change) * current_price

                    change_data = {
                        'id_product': pid,
                        'reference': product.get('reference', ''),
                        'product_title': product.get('product_title', ''),
                        'id_manufacturer': product.get('id_manufacturer', ''),
                        'is_pack': product.get('is_pack', 'No'),
                        'category_url': product.get('category_url', ''),
                        'price': current_price,
                        'previous_price': previous_price,
                        'stock_quantity': current_stock,
                        'previous_stock': previous_stock,
                        'price_change': price_changed,
                        'stock_change': stock_change,
                        'transaction': transaction,
                        'ca': ca,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if 'id_category_default' in product:
                        change_data['id_category_default'] = product.get('id_category_default', '')

                    changes.append(change_data)

        except Exception as e:
            logging.error(f"Error comparing product {product.get('id_product', 'unknown')}: {e}")
            continue

    return changes


def save_changes_log(changes, grouped=False):
    if not changes:
        return

    log_file = CHANGES_LOG_FILE_GROUPED if grouped else CHANGES_LOG_FILE

    try:
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for change in changes:
                if grouped:
                    row = [
                        change['timestamp'],
                        change['id_product'],
                        change['reference'],
                        change['product_title'],
                        change['id_manufacturer'],
                        change['is_pack'],
                        change['category_url'],
                        change['price'],
                        change['previous_price'],
                        change['price_change'],
                        change['stock_quantity'],
                        change['previous_stock'],
                        change['stock_change'],
                        change['transaction'],
                        change['ca']
                    ]
                else:
                    row = [
                        change['timestamp'],
                        change['id_product'],
                        change['reference'],
                        change['product_title'],
                        change['id_manufacturer'],
                        change['is_pack'],
                        change.get('id_category_default', ''),
                        change['category_url'],
                        change['price'],
                        change['previous_price'],
                        change['price_change'],
                        change['stock_quantity'],
                        change['previous_stock'],
                        change['stock_change'],
                        change['transaction'],
                        change['ca']
                    ]
                writer.writerow(row)

        group_type = "grouped" if grouped else "regular"
        logging.info(f"Appended {len(changes)} changes to {group_type} log file: {log_file}")
    except Exception as e:
        logging.error(f"Error saving changes log: {e}")


def save_no_changes_log(grouped=False):
    log_file = CHANGES_LOG_FILE_GROUPED if grouped else CHANGES_LOG_FILE

    try:
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([f'{current_time} - No changes detected'])

        group_type = "grouped" if grouped else "regular"
        logging.info(f"Recorded 'no changes' entry in {group_type} log file: {log_file}")
    except Exception as e:
        logging.error(f"Error saving no changes log: {e}")


def analyze_changes_after_save(current_file_path, grouped=False):
    try:
        current_date = datetime.now().date()
        previous_date = current_date - timedelta(days=1)

        group_type = "grouped" if grouped else "regular"
        logging.info(f"Looking for {group_type} comparison files - Current: {current_date}, Previous: {previous_date}")

        previous_file = find_file_by_date(previous_date, grouped)
        if not previous_file:
            logging.info(f"No {group_type} file found for previous date {previous_date}. Skipping comparison.")
            save_no_changes_log(grouped)
            return

        logging.info(f"Comparing {group_type} files: {current_file_path} vs {previous_file}")

        current_products = load_products_from_csv(current_file_path)
        previous_products = load_products_from_csv(previous_file)

        if not current_products:
            logging.error(f"Failed to load current {group_type} products data")
            return

        if not previous_products:
            logging.warning(f"No previous {group_type} products data available for comparison")
            save_no_changes_log(grouped)
            return

        changes = compare_products(current_products, previous_products)

        if changes:
            logging.info(f"Detected {len(changes)} {group_type} changes from previous day:")
            for change in changes:
                log_msg = (
                    f"  ID: {change['id_product']}, Ref: {change['reference']}, "
                    f"Title: {change['product_title']}, ID Manufacturer: {change['id_manufacturer']}, "
                    f"Pack: {change['is_pack']}, Category: {change['category_url']}"
                )
                if not grouped and 'id_category_default' in change:
                    log_msg += f", Category Default: {change['id_category_default']}"
                logging.info(log_msg)

                if change['price_change']:
                    logging.info(f"    Price: {change['previous_price']} -> {change['price']}")
                if change['stock_change'] != 0:
                    logging.info(
                        f"    Stock change: {change['stock_change']} (was: {change['previous_stock']}, now: {change['stock_quantity']})"
                    )
            save_changes_log(changes, grouped)
        else:
            logging.info(f"No {group_type} changes detected from previous day")
            save_no_changes_log(grouped)

    except Exception as e:
        logging.error(f"Error during {group_type} change analysis: {e}")


def extract_manufacturer_logo_url(item, response_url):
    """Extract manufacturer logo URL from .logomarque element"""
    try:
        brand_img = item.select_one('.logomarque')
        if not brand_img:
            return ""

        # Try to get the image source URL
        brand_src = brand_img.get('src') or brand_img.get('data-src')

        # If no src, try srcset attribute
        if not brand_src:
            srcset = brand_img.get('srcset')
            if srcset:
                # Take the first URL from srcset
                brand_src = srcset.split()[0]

        # Convert relative URL to absolute URL if needed
        if brand_src:
            brand_src = urljoin(response_url, brand_src)
            logging.debug(f"Extracted manufacturer logo URL: {brand_src}")
            return brand_src

        logging.debug("No manufacturer logo found in .logomarque")
        return ""

    except Exception as e:
        logging.warning(f"Error extracting manufacturer logo: {e}")
        return ""


def get_product_links(session, category_url, grouped=False):
    product_links = []
    page = 1
    max_pages = 20
    previous_page_products = set()

    while page <= max_pages:
        url = f"{category_url}?page={page}" if page > 1 else category_url

        try:
            group_type = "grouped" if grouped else "regular"
            logging.info(f"Fetching {group_type} page {page} of {category_url}")

            response = session.get(url, headers=get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            if grouped:
                products_container = soup.select_one('#product_list')
                if not products_container:
                    logging.info(f"No products container found on page {page} of {category_url}")
                    break

                items = products_container.select('.ajax_block_product')
                current_page_products = set()
                current_page_links = []

                for item in items:
                    a = item.select_one('h3 a')
                    if not a:
                        continue

                    href = a.get('href')
                    if not href or 'index.php' in href:
                        continue

                    product_id_match = re.search(r'/(\d+)-', href)
                    product_id = product_id_match.group(1) if product_id_match else None
                    if not product_id:
                        continue

                    # Extract manufacturer logo URL
                    brand_logo_url = extract_manufacturer_logo_url(item, response.url)

                    current_page_products.add(product_id)
                    entry = {
                        'url': href,
                        'id_product': product_id,
                        'category_url': category_url,
                        'id_manufacturer': brand_logo_url  # Store the logo URL in id_manufacturer field
                    }
                    current_page_links.append(entry)

                if not current_page_links:
                    logging.info(f"No more products found on page {page} of {category_url}")
                    break

                if current_page_products and current_page_products == previous_page_products:
                    logging.warning(
                        f"Detected duplicate products on page {page} of {category_url}, breaking pagination loop")
                    break

                product_links.extend(current_page_links)
                previous_page_products = current_page_products
                logging.info(f"Found {len(current_page_links)} products on page {page} of {category_url}")

                # Check for next page
                pagination = soup.select_one('.pagination')
                if pagination:
                    next_disabled = pagination.select_one('.next.disabled') or not pagination.select_one('.next')
                    if next_disabled:
                        logging.info(f"Reached last page ({page}) for {category_url}")
                        break

                page += 1
                time.sleep(3)
                continue

            # Regular (non-grouped) processing
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
                if href and 'index.php' not in href:
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
                    pid in previous_page_products for pid in current_page_products
            ):
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

    if page > max_pages:
        logging.warning(f"Reached maximum page limit ({max_pages}) for {category_url}")

    logging.info(f"Total of {len(product_links)} products found for {category_url}")
    return product_links


def get_all_products(session, grouped=False):
    all_products = []
    category_urls = CATEGORY_URLS_GROUPED if grouped else CATEGORY_URLS

    for category_url in category_urls:
        group_type = "grouped" if grouped else "regular"
        logging.info(f"Scraping {group_type} category: {category_url}")
        products = get_product_links(session, category_url, grouped)
        all_products.extend(products)
        time.sleep(3)

    # Remove duplicates
    seen_ids = set()
    unique_products = []
    for product in all_products:
        if product['id_product'] not in seen_ids:
            unique_products.append(product)
            seen_ids.add(product['id_product'])

    group_type = "grouped" if grouped else "regular"
    logging.info(f"Total unique {group_type} products found: {len(unique_products)}")
    return unique_products


def extract_product_details_grouped(session, product):
    try:
        response = session.get(product['url'], headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize variables
        reference = ""
        product_title = ""
        price_without_reduction = 0
        discount_amount = 0
        price = 0
        available_date = ""
        stock_quantity = 0
        quantity_all_versions = 0
        id_manufacturer = product.get('id_manufacturer', '')  # This now contains the logo URL
        is_pack = "No"

        # Extract product title
        title_h1 = soup.select_one('h1')
        if title_h1:
            product_title = title_h1.get_text(strip=True)

        # Extract product details from JavaScript
        main_section = soup.select_one('#main_section')
        if main_section:
            scripts = main_section.find_all('script', type='text/javascript')
            for script in scripts:
                if script.string and 'id_product' in script.string:
                    script_content = script.string

                    # Verify this is the correct product
                    id_match = re.search(r"var id_product = '(\d+)';", script_content)
                    if id_match:
                        extracted_id = id_match.group(1)
                        if extracted_id == product['id_product']:
                            # Extract reference
                            ref_match = re.search(r"var productReference = '([^']+)';", script_content)
                            if ref_match:
                                reference = ref_match.group(1)

                            # Extract stock quantity
                            stock_match = re.search(r"var quantityAvailable = (\d+);", script_content)
                            if stock_match:
                                stock_quantity = int(stock_match.group(1))

                            # Extract price without reduction
                            price_without_reduction_match = re.search(r"var productPriceWithoutReduction = '([^']+)';",
                                                                      script_content)
                            if price_without_reduction_match:
                                price_without_reduction = float(price_without_reduction_match.group(1))

                            # Extract current price
                            price_match = re.search(r"var productPrice = '([^']+)';", script_content)
                            if price_match:
                                price = float(price_match.group(1))

                            # Calculate discount
                            if price_without_reduction and price:
                                discount_amount = price_without_reduction - price

                            # Check for specific reduction price
                            reduction_match = re.search(r"var reduction_price = (\d+);", script_content)
                            if reduction_match:
                                reduction_price = float(reduction_match.group(1))
                                if reduction_price > 0:
                                    discount_amount = reduction_price

                            break

        # Check if product is a pack
        pack_elements = soup.select('.pack-info, .product-pack')
        if pack_elements:
            is_pack = "Yes"

        return {
            'id_product': product['id_product'],
            'reference': reference,
            'product_title': product_title,
            'id_manufacturer': id_manufacturer,  # Logo URL
            'is_pack': is_pack,
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
        logging.error(f"Error fetching grouped product details for {product['url']}: {e}")
        return None


def extract_product_details(session, product, grouped=False):
    if grouped:
        return extract_product_details_grouped(session, product)

    try:
        response = session.get(product['url'], headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize variables
        reference = ""
        product_title = ""
        price_without_reduction = 0
        discount_amount = 0
        price = 0
        available_date = ""
        stock_quantity = 0
        quantity_all_versions = 0
        id_manufacturer = ""
        is_pack = "No"
        id_category_default = ""

        # Extract product title
        title_h1 = soup.select_one('h1')
        if title_h1:
            product_title = title_h1.get_text(strip=True)

        # Extract product details from JSON data
        product_details_elem = soup.select_one('#product-details')
        if product_details_elem and 'data-product' in product_details_elem.attrs:
            try:
                product_json = json.loads(product_details_elem['data-product'])
                reference = product_json.get('reference', '')
                stock_quantity = product_json.get('quantity', 0)
                quantity_all_versions = product_json.get('quantity_all_versions', 0)
                price = product_json.get('price_amount', 0)
                price_without_reduction = product_json.get('price_without_reduction', price)
                id_manufacturer = product_json.get('id_manufacturer', '')
                id_category_default = product_json.get('id_category_default', '')

                if price_without_reduction and price:
                    discount_amount = float(price_without_reduction) - float(price)
                else:
                    discount_amount = 0

                available_date = product_json.get('available_date', '')
                pack_status = product_json.get('pack', 0)
                is_pack = "Yes" if pack_status == 1 else "No"

            except (json.JSONDecodeError, KeyError) as json_err:
                logging.error(f"Error parsing product JSON for {product['url']}: {json_err}")

        # Fallback extraction methods if JSON parsing failed
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

        # Extract category from breadcrumb if not found
        if not id_category_default:
            breadcrumb = soup.select_one('.breadcrumb')
            if breadcrumb:
                category_links = breadcrumb.select('a')
                for link in category_links:
                    href = link.get('href', '')
                    category_match = re.search(r'/(\d+)-', href)
                    if category_match:
                        id_category_default = category_match.group(1)
                        break

        return {
            'id_product': product['id_product'],
            'reference': reference,
            'product_title': product_title,
            'id_manufacturer': id_manufacturer,
            'is_pack': is_pack,
            'id_category_default': id_category_default,
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


def save_current_data(current_products, grouped=False):
    timestamped_file = get_timestamped_filename(grouped=grouped)

    try:
        # Filter valid products
        valid_products = []
        for product in current_products:
            if validate_product_data(product):
                valid_products.append(product)
            else:
                logging.warning(f"Skipping invalid product data: {product}")

        with open(timestamped_file, 'w', newline='', encoding='utf-8') as f:
            if valid_products:
                if grouped:
                    fieldnames = [
                        'timestamp', 'id_product', 'reference', 'product_title', 'id_manufacturer',
                        'is_pack', 'url', 'category_url', 'price_without_reduction', 'discount_amount',
                        'price', 'available_date', 'stock_quantity', 'quantity_all_versions'
                    ]
                else:
                    fieldnames = [
                        'timestamp', 'id_product', 'reference', 'product_title', 'id_manufacturer',
                        'is_pack', 'id_category_default', 'url', 'category_url', 'price_without_reduction',
                        'discount_amount', 'price', 'available_date', 'stock_quantity', 'quantity_all_versions'
                    ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for product in valid_products:
                    product_data = product.copy()
                    product_data['timestamp'] = timestamp
                    writer.writerow(product_data)

        group_type = "grouped" if grouped else "regular"
        logging.info(f"Saved {len(valid_products)} valid {group_type} products to {timestamped_file}")
        return timestamped_file

    except Exception as e:
        logging.error(f"Error saving current data: {e}")
        return None


def run_monitor_for_group(grouped=False):
    group_type = "grouped" if grouped else "regular"
    logging.info(f"Starting {group_type} monitoring cycle...")

    # Check if today's file already exists
    file_exists, existing_file = check_if_today_file_exists(grouped)
    if file_exists:
        logging.info(f"{group_type.capitalize()} file for today already exists: {existing_file}")
        logging.info(f"Skipping {group_type} scraping for today - file already created")
        return

    logging.info(f"No {group_type} file found for today - proceeding with scraping...")

    session = requests.Session()
    products = get_all_products(session, grouped)

    if not products:
        logging.error(f"No {group_type} products found!")
        return

    logging.info(f"Found {len(products)} unique {group_type} products to process")

    current_products = []
    for product in products:
        logging.info(f"Processing {group_type} product: {product['id_product']}")
        details = extract_product_details(session, product, grouped)
        if details:
            current_products.append(details)
        time.sleep(2)

    logging.info(f"Successfully processed {len(current_products)} {group_type} products")

    # Save current data
    current_file_path = save_current_data(current_products, grouped)
    if current_file_path:
        logging.info(f"{group_type.capitalize()} products saved to: {current_file_path}")
        logging.info(f"Starting {group_type} change analysis...")
        analyze_changes_after_save(current_file_path, grouped)
    else:
        logging.error(f"Failed to save current {group_type} products data")

    logging.info(f"{group_type.capitalize()} monitoring cycle completed successfully")


def run_monitor():
    logging.info("Starting daily monitoring cycle for all groups...")

    # Process regular categories (minimx.fr structure)
    if CATEGORY_URLS:
        logging.info("=" * 50)
        logging.info("PROCESSING REGULAR CATEGORIES (minimx.fr structure)")
        logging.info("=" * 50)
        run_monitor_for_group(grouped=False)

    # Process grouped categories (lebonquad.com structure)
    if CATEGORY_URLS_GROUPED:
        logging.info("=" * 50)
        logging.info("PROCESSING GROUPED CATEGORIES (lebonquad.com structure)")
        logging.info("=" * 50)
        run_monitor_for_group(grouped=True)

    logging.info("All monitoring cycles completed successfully")


def calculate_next_run_time():
    now = datetime.now()
    next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return next_run


def wait_until_next_run():
    next_run = calculate_next_run_time()
    wait_seconds = (next_run - datetime.now()).total_seconds()

    if wait_seconds > 0:
        logging.info(f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Waiting {wait_seconds:.0f} seconds until next run...")
        time.sleep(wait_seconds)


def main():
    setup_directories()

    logging.info("Starting daily product monitor (runs at 00:00 each day)")
    logging.info(f"Regular categories: {len(CATEGORY_URLS)} URLs")
    logging.info(f"Grouped categories: {len(CATEGORY_URLS_GROUPED)} URLs")

    # Run initial monitoring cycle
    logging.info("Running initial monitoring cycle...")
    run_monitor()

    # Set up daily scheduler
    schedule.every().day.at("00:00").do(run_monitor)
    logging.info("Daily scheduler set up. Will run every day at 00:00")

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise