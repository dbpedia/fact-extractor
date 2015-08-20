#!/usr/bin/env python
# -*- encoding: utf-8 -*-
FRAME_IT_TO_EN = {
    "frame":
    {
        # Kicktionary
        u"Partita": u"match",
        u"Sconfitta": u"defeat",
        u"Vittoria": u"victory",
        # Direct translation
        u"Stato": u"status",
        # Mapped to DBPO
        u"Attività": None,
        u"Trofeo": None
    },
    "FE": {
        # FrameNet
        u"Perdente": u"loser", # Beat_opponent
        u"Vincitore": u"winner", # Beat_opponent
        u"Competizione": u"competition", # Finish_competition
        u"Squadra_1": u"competitor", # Finish_competition
        u"Squadra_2": u"opponent", # Finish_competition
        u"Luogo": u"place", # Beat_opponent / Finish_competition
        u"Tempo": u"time", # Beat_opponent / Finish_competition
        # Direct translation
        u"Agente": u"agent",
        u"Concorrente": u"participant",
        u"Entità": u"entity",
        u"Premio": u"prize",
        # Mapped to DBPO
        u"Classifica": None,
        u"Durata": None,
        u"Punteggio": None,
        u"Squadra": None,
        u"Stato": None
    }

}
