# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Console import Console
import os

# --- CONFIGURAZIONE ---
URL_BASE = "http://webplusfeeds.sat-lodge.it/settings/"
ICON_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/slSetting/res/pics/"
VERSION = "4.2"

class slDownloader(Screen):
    def __init__(self, session, url, scelta):
        self.session = session
        self.scelta = scelta
        self.skin = """
            <screen position="center,center" size="700,250" title="SatLodge Installer">
                <widget name="status" position="20,60" size="660,100" font="Regular;32" halign="center" valign="center" />
                <widget name="info" position="20,160" size="660,40" font="Regular;22" halign="center" foregroundColor="#00ffcc00" />
            </screen>"""
        Screen.__init__(self, session)
        self["status"] = Label("Pulizia e Installazione...")
        self["info"] = Label("Il box si riavvierà tra poco...")
        self["actions"] = ActionMap(["OkCancelActions"], {"cancel": self.close}, -1)
        
        self.console = Console()
        self.onLayoutFinish.append(self.startProcess)

    def startProcess(self):
        UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        base_cmd = "wget -U '%s' --no-check-certificate -T 10 -t 1" % UA
        
        if self.scelta == "xml":
            # Per il satellites.xml non serve riavviare Enigma2, basta rimpiazzarlo
            cmd = "%s %ssatellites.xml -O /etc/tuxbox/satellites.xml" % (base_cmd, URL_BASE)
        else:
            f = {"mono": "mono_13.zip", "dual": "dual_13_19.zip", "dual_dtt": "dual_13_19_dtt.zip"}.get(self.scelta, "")
            
            # --- SEQUENZA DEFINITIVA ---
            # 1. Elimina i vecchi file per evitare "voci vuote"
            # 2. Scarica e scompatta i nuovi
            # 3. Forza il riavvio della GUI (Enigma2) per pulire la memoria
            cmd = "rm -rf /etc/enigma2/userbouquet.* && rm -rf /etc/enigma2/bouquets.tv && " \
                  "%s %s%s -O /tmp/sl.zip && unzip -o /tmp/sl.zip -d / && " \
                  "rm -f /tmp/sl.zip && sleep 2 && killall -9 enigma2" % (base_cmd, URL_BASE, f)

        self.console.ePopen(cmd, self.finished)

    def finished(self, result, retval, extra_args=None):
        # Se Enigma2 viene killato, questo messaggio potrebbe non apparire nemmeno
        # perché il box si riavvia istantaneamente. È normale.
        from Screens.MessageBox import MessageBox
        if retval != 0:
            self.session.open(MessageBox, "Errore durante l'installazione!", MessageBox.TYPE_ERROR)

class slSettingMain(Screen):
    def __init__(self, session):
        self.session = session
        self.skin = """<screen position="center,center" size="1280,720" title=" " backgroundColor="#101010" flags="wfNoBorder">
                            <eLabel position="0,0" size="1280,90" backgroundColor="#1a1a1a" zPosition="-1" />
                            <widget name="title" position="40,20" size="800,50" font="Regular;42" foregroundColor="#00ffcc00" backgroundColor="#1a1a1a" transparent="1" />
                            <widget name="version" position="1100,25" size="140,40" font="Regular;24" halign="right" foregroundColor="#ffffff" backgroundColor="#1a1a1a" transparent="1" />
                            <widget name="menu" position="50,140" size="650,450" itemHeight="75" font="Regular;34" scrollbarMode="showOnDemand" transparent="1" selectionColor="#333333" />
                            <widget name="preview" position="720,140" size="500,400" alphatest="on" />
                            <eLabel position="0,630" size="1280,90" backgroundColor="#1a1a1a" zPosition="-1" />
                            <widget name="status" position="40,655" size="1200,40" font="Regular;30" halign="center" foregroundColor="#ffffff" backgroundColor="#1a1a1a" transparent="1" />
                         </screen>"""
        Screen.__init__(self, session)
        self.list = [
            ("SatLodge Mono (13E)", "mono"),
            ("SatLodge Dual (13E + 19E)", "dual"),
            ("SatLodge Dual + DTT (13E+19E+DTT)", "dual_dtt"),
            ("Aggiorna satellites.xml", "xml")
        ]
        self["title"] = Label("SAT-LODGE SETTINGS PANEL")
        self["version"] = Label("v" + VERSION)
        self["status"] = Label("Seleziona e premi OK")
        self["menu"] = MenuList(self.list)
        self["preview"] = Pixmap()
        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"], {
            "ok": self.okClicked,
            "cancel": self.close,
            "up": self.up,
            "down": self.down,
        }, -1)
        self.onLayoutFinish.append(self.selectionChanged)

    def up(self):
        self["menu"].up()
        self.selectionChanged()

    def down(self):
        self["menu"].down()
        self.selectionChanged()

    def selectionChanged(self):
        current = self["menu"].getCurrent()
        if current:
            p = ICON_PATH + current[1] + ".png"
            if not os.path.exists(p): p = ICON_PATH + "tvlogofhd.png"
            if os.path.exists(p): self["preview"].instance.setPixmapFromFile(p)

    def okClicked(self):
        current = self["menu"].getCurrent()
        if current:
            self.session.open(slDownloader, URL_BASE, current[1])

def main(session, **kwargs):
    session.open(slSettingMain)

def Plugins(**kwargs):
    return [PluginDescriptor(name="SatLodge Settings", description="Aggiornamento Canali", where=PluginDescriptor.WHERE_PLUGINMENU, icon="res/pics/logo.png", fnc=main)]
