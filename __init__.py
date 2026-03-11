#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
import os

# Definizione del dominio e del percorso traduzioni
PluginLanguageDomain = 'slSetting'
PluginLanguagePath = 'Extensions/slSetting/res/locale'

def localeInit():
    # Cerca la cartella delle traduzioni nel percorso del plugin
    lang_path = resolveFilename(SCOPE_PLUGINS, PluginLanguagePath)
    gettext.bindtextdomain(PluginLanguageDomain, lang_path)

def _(txt):
    # Funzione di traduzione rapida
    if txt == "":
        return ""
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t:
        return t
    return gettext.gettext(txt)

# Inizializzazione automatica al caricamento
localeInit()
language.addCallback(localeInit)
