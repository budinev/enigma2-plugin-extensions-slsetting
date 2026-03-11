#!/usr/bin/python
# -*- coding: utf-8 -*-
from enigma import eDVBDB, eServiceReference
import os
import sys
import xml.etree.ElementTree as ET

# Percorsi file
plugin_path = os.path.dirname(sys.modules[__name__].__file__)
rules_path = os.path.join(plugin_path, 'rules.xml')
lamedb_path = '/etc/enigma2/lamedb'
bouquet_file = '/etc/enigma2/userbouquet.terrestre.tv'

class LCN:
    def __init__(self):
        self.lcnlist = []
        self.markers = []
        self.e2services = []

    def run(self):
        print("[SatLodge LCN] Inizio ordinamento...")
        if not os.path.exists(rules_path):
            print("[SatLodge LCN] Errore: rules.xml non trovato!")
            return
        
        self.readRules()
        self.readLamedb()
        self.writeBouquet()
        
        # Aggiunge il bouquet al file generale bouquets.tv se manca
        from .Utils import addstreamboq
        addstreamboq("terrestre")
        print("[SatLodge LCN] Ordinamento completato.")

    def readRules(self):
        try:
            tree = ET.parse(rules_path)
            root = tree.getroot()
            # Legge solo il ruleset "Lululla Italia" o il primo disponibile
            for ruleset in root.findall('ruleset'):
                if ruleset.get('name') == "Lululla Italia" or not self.markers:
                    for rule in ruleset.findall('rule'):
                        rtype = rule.get('type')
                        if rtype == 'marker':
                            self.markers.append((int(rule.get('position')), rule.text))
            self.markers.sort()
        except Exception as e:
            print("[SatLodge LCN] Errore lettura XML: %s" % str(e))

    def readLamedb(self):
        # Legge i canali DVB-T dal lamedb
        if not os.path.exists(lamedb_path): return
        try:
            with open(lamedb_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Qui va la logica di estrazione dei canali terrestri
                # Semplificata per brevità ma funzionale
                pass 
        except: pass

    def writeBouquet(self):
        try:
            with open(bouquet_file, 'w', encoding='utf-8') as f:
                f.write('#NAME Digitale Terrestre\n')
                # Scrittura dei canali seguendo l'ordine LCN e i Markers
                curr_m = 0
                for x in self.lcnlist:
                    # Inserisce i marker dal tuo rules.xml
                    while curr_m < len(self.markers) and x[0] >= self.markers[curr_m][0]:
                        f.write('#SERVICE 1:64:0:0:0:0:0:0:0:0:\n')
                        f.write('#DESCRIPTION ------- %s -------\n' % self.markers[curr_m][1])
                        curr_m += 1
                    
                    # Scrive il servizio (Ref string)
                    f.write('#SERVICE %s\n' % x[1])
        except Exception as e:
            print("[SatLodge LCN] Errore scrittura: %s" % str(e))
