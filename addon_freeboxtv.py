#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Addon Stremio / Nuvio - Chaînes TV Françaises (Freebox TV / IPTV M3U)
---------------------------------------------------------------------
Ce script crée un véritable serveur d'addon compatible Stremio & Nuvio
à partir d'une playlist M3U / RTSP (comme celle de Freebox TV).
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

# Port du serveur de l'addon
PORT = 7000

# Catalogue des chaînes (extrait de votre liste M3U Freebox)
CHANNELS = [
    {
        "id": "fboxtv:france2",
        "name": "France 2",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/France_2_2018.svg/512px-France_2_2018.svg.png",
        "description": "France 2 en direct (Freebox TV RTSP)",
        "streams": [
            {
                "title": "🇫🇷 France 2 (HD)",
                "url": "rtsp://mafreebox.freebox.fr/fbxtv_pub/stream?namespace=1&service=201&flavour=hd"
            },
            {
                "title": "🇫🇷 France 2 (Auto)",
                "url": "rtsp://mafreebox.freebox.fr/fbxtv_pub/stream?namespace=1&service=201"
            },
            {
                "title": "🇫🇷 France 2 (Standard - SD)",
                "url": "rtsp://mafreebox.freebox.fr/fbxtv_pub/stream?namespace=1&service=201&flavour=sd"
            },
            {
                "title": "🇫🇷 France 2 (Bas débit - LD)",
                "url": "rtsp://mafreebox.freebox.fr/fbxtv_pub/stream?namespace=1&service=201&flavour=ld"
            }
        ]
    },
    {
        "id": "fboxtv:france3",
        "name": "France 3",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/France_3_2018.svg/512px-France_3_2018.svg.png",
        "description": "France 3 en direct (Freebox TV RTSP)",
        "streams": [
            {
                "title": "🇫🇷 France 3 (HD)",
                "url": "rtsp://mafreebox.freebox.fr/fbxtv_pub/stream?namespace=1&service=202&flavour=hd"
            },
            {
                "title": "🇫🇷 France 3 (Auto)",
                "url": "rtsp://mafreebox.freebox.fr/fbxtv_pub/stream?namespace=1&service=202"
            },
            {
                "title": "🇫🇷 France 3 (Standard - SD)",
                "url": "rtsp://mafreebox.freebox.fr/fbxtv_pub/stream?namespace=1&service=202&flavour=sd"
            }
        ]
    }
]

# Manifest officiel Stremio / Nuvio
MANIFEST = {
    "id": "org.freeboxtv.live.fr",
    "version": "1.0.0",
    "name": "🇫🇷 Freebox TV — Direct TNT",
    "description": "Chaînes de télévision françaises en direct via playlist Freebox / RTSP",
    "logo": "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Freebox_logo.svg/512px-Freebox_logo.svg.png",
    "resources": ["catalog", "meta", "stream"],
    "types": ["tv"],
    "idPrefixes": ["fboxtv:"],
    "catalogs": [
        {
            "type": "tv",
            "id": "freeboxtv-direct",
            "name": "🇫🇷 Direct TNT (Freebox)"
        }
    ]
}

class StremioAddonHandler(BaseHTTPRequestHandler):
    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        # 1. Manifest
        if path == "/manifest.json" or path == "/":
            self.send_json(MANIFEST)
            return

        # 2. Catalogue (Liste des chaînes TV)
        if path == "/catalog/tv/freeboxtv-direct.json":
            metas = []
            for ch in CHANNELS:
                metas.append({
                    "id": ch["id"],
                    "type": "tv",
                    "name": ch["name"],
                    "poster": ch["logo"],
                    "posterShape": "square",
                    "description": ch["description"]
                })
            self.send_json({"metas": metas})
            return

        # 3. Métadonnées d'une chaîne
        if path.startswith("/meta/tv/fboxtv:"):
            ch_id = path.split("/meta/tv/")[1].replace(".json", "")
            for ch in CHANNELS:
                if ch["id"] == ch_id:
                    self.send_json({
                        "meta": {
                            "id": ch["id"],
                            "type": "tv",
                            "name": ch["name"],
                            "poster": ch["logo"],
                            "posterShape": "square",
                            "description": ch["description"]
                        }
                    })
                    return
            self.send_json({"meta": {}})
            return

        # 4. Flux (Streams - Liens RTSP/IPTV)
        if path.startswith("/stream/tv/fboxtv:"):
            ch_id = path.split("/stream/tv/")[1].replace(".json", "")
            for ch in CHANNELS:
                if ch["id"] == ch_id:
                    self.send_json({"streams": ch["streams"]})
                    return
            self.send_json({"streams": []})
            return

        # Erreur 404
        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    print(f"🚀 Addon Freebox TV lancé sur le port {PORT}...")
    print(f"👉 Manifest URL : http://127.0.0.1:{PORT}/manifest.json")
    server = HTTPServer(("0.0.0.0", PORT), StremioAddonHandler)
    server.serve_forever()
