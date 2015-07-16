# -*- encoding: utf-8 -*-
LU_FRAME_MAP = [
    {
        "lu":
        {
            "lemma": "esordire",
            "tokens":
            [
                "esordendo",
                "esordendovi",
                u"esordì",
                u"esordirà",
                "esordiranno",
                "esordire",
                "esordirono",
                "esordirvi",
                "esordisca",
                "esordisce",
                "esordiscono",
                "esordito",
                "esordiva"
            ],
            "frames":
            [
                {
                    "frame": u"Attività",
                    "FEs":
                    [
                        { "Competizione": "core" },
                        { "Squadra": "core" },
                        { "Agente": "extra" },
                        { "Durata": "extra" },
                        { "Luogo": "extra" },
                        { "Tempo": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerLeague": "Competizione" },
                        { "SoccerTournament": "Competizione" },
                        { "SoccerLeagueSeason": "Competizione" },
                        { "SoccerClub": "Squadra" },
                        { "Place": "Luogo" },
                        { "SoccerPlayer": "Agente" }
                    ]
                }
            ]
        }
    },    
    {
        "lu": 
        {
            "lemma": "giocare",
            "tokens":
            [
                "gioca",
                "giocai",
                "giocammo",
                "giocandoci",
                "giocando",
                "giocandogli",
                "giocandola",
                "giocandole",
                "giocandoli",
                "giocandolo",
                "giocandone",
                "giocandosela",
                "giocandoselo",
                "giocandosi",
                "giocandovi",
                "giocane",
                "giocano",
                "giocante",
                "giocanti",
                "giocarci",
                "giocare",
                "giocar",
                "giocargli",
                "giocarla",
                "giocarle",
                "giocarli",
                "giocarlo",
                "giocarne",
                "giocarono",
                "giocarsela",
                "giocarselo",
                "giocarsi",
                "giocarvi",
                "giocasi",
                "giocasse",
                "giocassero",
                "giocata",
                "giocate",
                "giocatesi",
                "giocatevi",
                "giocati",
                "giocato",
                "giocava",
                "giocavamo",
                "giocavano",
                "giocavi",
                "giocavo",
                u"giocherà",
                "giocheranno",
                "giocherebbe",
                "giocherebbero",
                "giocherei",
                "giocheremo",
                "giocheresti",
                "giocherete",
                u"giocherò",
                "giochiamo",
                "giochi",
                "giochino",
                "gioco",
                u"giocò"
            ],
            "frames":
            [
                {
                    "frame": "Partita",
                    "FEs":
                    [
                        { "Squadra_1": "core" },
                        { "Squadra_2": "core" },
                        { "Competizione": "extra"},
                        { "Luogo": "extra" },
                        { "Tempo": "extra" },
                        { "Punteggio": "extra" },
                        { "Classifica": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerLeague": "Competizione" },
                        { "SoccerTournament": "Competizione" },
                        { "SoccerLeagueSeason": "Competizione" },
                        { "SoccerClub": ["Squadra_1", "Squadra_2"] },
                        { "Place": "Luogo" }
                    ]
                },
                {
                    "frame": u"Attività",
                    "FEs":
                    [
                        { "Competizione": "core" },
                        { "Squadra": "core" },
                        { "Agente": "extra" },
                        { "Durata": "extra" },
                        { "Luogo": "extra" },
                        { "Tempo": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerLeague": "Competizione" },
                        { "SoccerTournament": "Competizione" },
                        { "SoccerLeagueSeason": "Competizione" },
                        { "SoccerClub": "Squadra" },
                        { "Place": "Luogo" },
                        { "SoccerPlayer": "Agente" }
                    ]
                }
            ]
        }
    },
    {
        "lu":
        {
            "lemma": "perdere",
            "tokens":
            [
                "perda",
                "perde",
                "perdemmo",
                "perdendo",
                "perdendola",
                "perdendole",
                "perdendoli",
                "perdendolo",
                "perdendone",
                u"perderà",
                "perderanno",
                "perdere",
                "perderla",
                "perderlo",
                "perderne",
                "perdersi",
                "perdesse",
                "perdessero",
                "perdessimo",
                "perdete",
                "perdeva",
                "perdevano",
                "perdilo",
                "perdono",
                "persa",
                "perse",
                "persero",
                "persi",
                "perso"
            ],
            "frames":
            [
                {
                    "frame": "Sconfitta",
                    "FEs":
                    [
                        { "Vincitore": "core" },
                        { "Perdente": "core" },
                        { "Competizione": "extra"},
                        { "Luogo": "extra" },
                        { "Tempo": "extra" },
                        { "Punteggio": "extra" },
                        { "Classifica": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerLeague": "Competizione" },
                        { "SoccerTournament": "Competizione" },
                        { "SoccerLeagueSeason": "Competizione" },
                        { "SoccerClub": ["Vincitore", "Perdente"] },
                        { "Place": "Luogo" }
                    ]
                }
            ]
        }
    },
    {
        "lu":
        {
            "lemma": "rimanere",
            "tokens":
            [
                "rimane",
                "rimanendo",
                "rimanendoci",
                "rimanendolo",
                "rimanendone",
                "rimanendovi",
                "rimaner",
                "rimanerci",
                "rimanere",
                "rimanermi",
                "rimanervi",
                "rimanesse",
                "rimanessero",
                "rimaneva",
                "rimanevano",
                "rimanga",
                "rimangono",
                "rimani",
                u"rimarrà",
                "rimarrai",
                "rimarranno",
                "rimarrebbe",
                "rimase",
                "rimasero",
                "rimasi",
                "rimasta",
                "rimaste",
                "rimasti",
                "rimasto"
            ],
            "frames":
            [
                {
                    "frame": u"Attività",
                    "FEs":
                    [
                        { "Competizione": "core" },
                        { "Squadra": "core" },
                        { "Agente": "extra" },
                        { "Durata": "extra" },
                        { "Luogo": "extra" },
                        { "Tempo": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerLeague": "Competizione" },
                        { "SoccerTournament": "Competizione" },
                        { "SoccerLeagueSeason": "Competizione" },
                        { "SoccerClub": "Squadra" },
                        { "Place": "Luogo" },
                        { "SoccerPlayer": "Agente" }
                    ]
                },
                {
                    "frame": "Stato",
                    "FEs":
                    [
                        { u"Entità": "core" },
                        { "Stato": "core" },
                        { "Durata": "extra" },
                        { "Luogo": "extra" },
                        { "Squadra": "extra" },
                        { "Tempo": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerClub": "Squadra" },
                        { "SoccerPlayer": u"Entità" },
                        { "Place": "Luogo" }
                    ]
                }
            ]
        }
    },
    {
        "lu":
        {
            "lemma": "vincere",
            "tokens":
            [
                "vincano", 
                "vinca", 
                "vincemmo", 
                "vincendoci", 
                "vincendogli", 
                "vincendola", 
                "vincendole", 
                "vincendoli", 
                "vincendolo", 
                "vincendone", 
                "vincendosi", 
                "vincendo", 
                "vincendovi", 
                "vincente", 
                "vincenti", 
                "vincerai", 
                "vinceranno", 
                u"vincerà", 
                "vincerci", 
                "vincerebbero", 
                "vincerebbe", 
                "vincerei", 
                "vinceremo", 
                "vincerete", 
                "vincere", 
                "vincergli", 
                "vincerla", 
                "vincerle", 
                "vincerli", 
                "vincerlo", 
                "vincermi", 
                "vincerne", 
                u"vincerò", 
                "vincersi", 
                "vincer", 
                "vincervi", 
                "vincessero", 
                "vincesse", 
                "vincessi", 
                "vincesti", 
                "vincete", 
                "vincevano", 
                "vinceva", 
                "vince", 
                "vincevo", 
                "vinciamo", 
                "vinciate", 
                "vinci", 
                "vincono", 
                "vinco", 
                "vinsero", 
                "vinse", 
                "vinsi", 
                "vinta", 
                "vinte", 
                "vinti", 
                "vinto"
            ],
            "frames":
            [
                {
                    "frame": "Vittoria",
                    "FEs":
                    [
                        { "Vincitore": "core" },
                        { "Perdente": "core" },
                        { "Competizione": "extra"},
                        { "Luogo": "extra" },
                        { "Tempo": "extra" },
                        { "Punteggio": "extra" },
                        { "Classifica": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerLeague": "Competizione" },
                        { "SoccerTournament": "Competizione" },
                        { "SoccerLeagueSeason": "Competizione" },
                        { "SoccerClub": ["Vincitore", "Perdente"] },
                        { "Place": "Luogo" }
                    ]
                },
                {
                    "frame": "Trofeo",
                    "FEs":
                    [
                        { "Concorrente": "core" },
                        { "Competizione": "core" },
                        { "Squadra": "extra" },
                        { "Premio": "extra" },
                        { "Luogo": "extra" },
                        { "Tempo": "extra" },
                        { "Punteggio": "extra" },
                        { "Classifica": "extra" }
                    ],
                    "DBpedia":
                    [
                        { "SoccerLeague": "Competizione" },
                        { "SoccerTournament": "Competizione" },
                        { "SoccerLeagueSeason": "Competizione" },
                        { "SoccerPlayer": "Concorrente" },
                        { "SoccerClub": "Squadra" },
                        { "Place": "Luogo" }
                    ]
                }
            ]
        }
    }
]
