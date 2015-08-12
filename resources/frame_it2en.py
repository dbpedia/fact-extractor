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
        u"Perdente": u"hasLoser", # Beat_opponent
        u"Vincitore": u"hasWinner", # Beat_opponent
        u"Competizione": u"hasCompetition", # Finish_competition
        u"Squadra_1": u"hasCompetitor", # Finish_competition
        u"Squadra_2": u"hasOpponent", # Finish_competition
        u"Luogo": u"hasPlace", # Beat_opponent / Finish_competition
        u"Tempo": u"hasTime", # Beat_opponent / Finish_competition
        # Direct translation
        u"Agente": u"hasAgent",
        u"Concorrente": u"hasParticipant",
        u"Entità": u"hasEntity",
        u"Premio": u"hasPrize",
        # Mapped to DBPO
        u"Classifica": None,
        u"Durata": None,
        u"Punteggio": None,
        u"Squadra": None,
        u"Stato": None
    }

}
