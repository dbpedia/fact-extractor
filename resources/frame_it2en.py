#!/usr/bin/env python
# -*- encoding: utf-8 -*-
FRAME_DBPO_MAP = {
    "frames":
    {
        # Kicktionary
        "Partita": "match",
        "Sconfitta": "defeat",
        "Vittoria": "victory",
        # Direct translation
        "Stato": "status",
        # Mapped to DBPO
        u"Attività": None,
        "Trofeo": None
    },
    "FEs": {
        # FrameNet
        "Perdente": "loser", # Beat_opponent
        "Vincitore": "winner", # Beat_opponent
        "Competizione": "competition", # Finish_competition
        "Squadra_1": "competitor", # Finish_competition
        "Squadra_2": "opponent", # Finish_competition
        "Luogo": "place", # Beat_opponent / Finish_competition
        "Tempo": "time", # Beat_opponent / Finish_competition
        # Direct translation
        "Agente": "agent",
        "Concorrente": "participant",
        u"Entità": "entity",
        "Premio": "prize",
        # Mapped to DBPO
        "Classifica": None,
        "Durata": None,
        "Punteggio": None,
        "Squadra": None,
        "Stato": None
    }

}