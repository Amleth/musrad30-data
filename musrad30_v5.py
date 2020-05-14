from pprint import pprint
import json, uuid, re, time, datetime, os
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD, OWL, FOAF, RDFS
from collections import defaultdict

# initialisation du graphe et des URL
IREMUS = Namespace("http://data-iremus.huma-num.fr/id/")
MUSRAD30 = Namespace("http://data-iremus.huma-num.fr/ns/musrad30/")
SCHEMA = Namespace("http://schema.org/")

g = Graph()
g.bind("skos", SKOS)
g.bind("xsd", XSD)
g.bind("foaf", FOAF)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("dcterms", DCTERMS)
g.bind("musrad30", MUSRAD30)
g.bind("schema", SCHEMA)

is_a = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

current_file_path = __file__
current_file_dir = os.path.dirname(__file__)
wiki_file_path = os.path.join(current_file_dir, "wikipedia-links-registry.json")
other_file_path = os.path.join(current_file_dir, "db_radio.json")

#chargement des liens wikipédias dans un dictionnaire
if wiki_file_path :
    with open(wiki_file_path, 'r') as f:
        lienswiki = json.load(f)

# fonctions outils
def initConceptScheme(uriConcept, nom):
    # declaration comme ConceptScheme
    g.add(
        (
            URIRef(uriConcept),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/2004/02/skos/core#ConceptScheme"),
        )
    )
    # association au litteral lui servant de titre
    g.add((URIRef(uriConcept), URIRef(DCTERMS.title), Literal(nom)))


def genUriIremus():
    return (str(uuid.uuid4()))


# Gestion des categories et sous-categories

# creation des conceptSchemes relatifs aux catégories
noeudCatCompositeur = str(uuid.uuid4())
noeudCatInterprete = str(uuid.uuid4())

# Variables relatives a l'initialisation des catégories et sous-catégories
initConceptScheme(noeudCatCompositeur, "Catégorie de compositeur")
initConceptScheme(noeudCatInterprete, "Catégorie d'interprète")

uriCatComp = dict()
uriCatInt = dict()
uriSousCat = dict()

# Fonction relative a l'initialisation des catégories et sous-catégories
def initCategoriesSousCategories():
    for key, value in data["db_radio"].items():
        if key == "categorie":
            print("Initialisation des Catégories")
            for x in value:
                uri = genUriIremus()
                g.add((URIRef(uri), URIRef(is_a), URIRef(SKOS.Concept),))
                g.add((URIRef(uri), URIRef(SKOS.prefLabel), Literal(x["nomcat"]),))
                if x["statutcat"] == "compositeur":
                    uriCatComp[x["IDcat"]] = uri
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SKOS.inScheme),
                            URIRef(noeudCatCompositeur),
                        )
                    )
                    g.add(
                        (
                            URIRef(noeudCatCompositeur),
                            URIRef(SKOS.hasTopConcept),
                            URIRef(uri),
                        )
                    )
                elif x["statutcat"] == "interprète":
                    uriCatInt[x["IDcat"]] = uri
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SKOS.inScheme),
                            URIRef(noeudCatInterprete),
                        )
                    )
                    g.add(
                        (
                            URIRef(noeudCatInterprete),
                            URIRef(SKOS.hasTopConcept),
                            URIRef(uri),
                        )
                    )
        elif key == "souscategorie":
            print("Initialisation des Sous-Catégories")
            for x in value:
                uri = genUriIremus()
                uriSousCat[x["IDsscat"]] = uri
                # creation des noeuds sousCategorie
                if x["catID"] in list(uriCatComp):
                    uriMere = uriCatComp[x["catID"]]
                    g.add
                    ((URIRef(uri), URIRef(is_a), URIRef(SKOS.Concept),))
                    # on lie la ssClasse au ConceptScheme de sa classe
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SKOS.inScheme),
                            URIRef(noeudCatCompositeur),
                        )
                    )
                    g.add((URIRef(uri), URIRef(SKOS.broader), URIRef(uriMere),))
                    g.add((URIRef(uriMere), URIRef(SKOS.narrower), URIRef(uri),))
                    g.add(
                        (URIRef(uri), URIRef(SKOS.prefLabel), Literal(x["nomsscat"]),)
                    )
                elif x["catID"] in list(uriCatInt):
                    uriMere = uriCatInt[x["catID"]]
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SKOS.inScheme),
                            URIRef(noeudCatInterprete),
                        )
                    )
                    g.add((URIRef(uri), URIRef(SKOS.broader), URIRef(uriMere),))
                    g.add((URIRef(uriMere), URIRef(SKOS.narrower), URIRef(uri),))
                    g.add(
                        (URIRef(uri), URIRef(SKOS.prefLabel), Literal(x["nomsscat"]),)
                    )


# Variables relatives aux programmes

noeudTitreProgrammes = genUriIremus()
initConceptScheme(noeudTitreProgrammes, "Titre de programme")
noeudTypeProgramme = genUriIremus()
initConceptScheme(noeudTypeProgramme, "Type de programme")
noeudFormatDiffusion = genUriIremus()
initConceptScheme(noeudFormatDiffusion, "Format de diffusion")
noeudStationsRadio = genUriIremus()

uriProgrammes = dict()
uriTypesProgrammes = dict()
uriFormatDiff = dict()
uriTitreProgrammes = dict()

# Fonctions relatives aux programmes


def initStationsRadio():
    # Asocie a chaque radio une URI, les injecte dans le graph sous forme de concept et renvoie un dico liant nom de radio a son URI
    dicoRadios = {"LL": genUriIremus(), "RC": genUriIremus(), "RP": genUriIremus()}
    # ajout des radios comme concepts du graphe
    g.add(
        (
            URIRef(dicoRadios['LL']),
            URIRef(SCHEMA["sameAs"]),
            URIRef(dicoRadios['RC']),
        )
    )
    g.add(
        (
            URIRef(dicoRadios['RC']),
            URIRef(SCHEMA["sameAs"]),
            URIRef(dicoRadios['LL']),     
        )
    )
    for cleRadio in dicoRadios.keys():
        g.add(
            (
                URIRef(dicoRadios[cleRadio]),
                URIRef(is_a),
                URIRef(SCHEMA["BroadcastService"]),
            )
        )
        if cleRadio == "RP":
            g.add(
                (
                    URIRef(dicoRadios[cleRadio]),
                    URIRef(SCHEMA["name"]),
                    Literal("Radio Paris"),
                )
            )
        elif cleRadio == "RC":
            g.add(
                (
                    URIRef(dicoRadios[cleRadio]),
                    URIRef(SCHEMA["name"]),
                    Literal("Radio Cité"),
                )
            )
        
        else :
            g.add(
                (
                    URIRef(dicoRadios[cleRadio]),
                    URIRef(SCHEMA["name"]),
                    Literal("Radio LL"),
                )
            )
        
    return dicoRadios


def extractTypeProgEtFormatDiff():
    print("Extraction des types de programmes et des formats de diffusion")
    listeTypeProgrammes = []
    listeFormatDiff = []
    for key, value in data["db_radio"].items():
        if key == "programmes":
            for x in value:
                if x["type_prog"] not in listeTypeProgrammes:
                    listeTypeProgrammes.append(x["type_prog"])
                if x["format_dif"] not in listeFormatDiff:
                    listeFormatDiff.append(x["format_dif"])
    return listeTypeProgrammes, listeFormatDiff


def initTypeProgEtFormatDiff():
    print("Initialisation des types de programmes et des formats de diffusion")
    listeTypesProgrammes, listeFormatDiff = extractTypeProgEtFormatDiff()
    for typeProgramme in listeTypesProgrammes:
        uriTypesProgrammes[typeProgramme] = genUriIremus()
        g.add(
            (
                URIRef(uriTypesProgrammes[typeProgramme]),
                URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                URIRef("http://www.w3.org/2004/02/skos/core#Concept"),
            )
        )
        
        g.add(
            (
                URIRef(uriTypesProgrammes[typeProgramme]),
                URIRef(SKOS.prefLabel),
                Literal(typeProgramme),
            )
        )
        g.add(
            (
                URIRef(uriTypesProgrammes[typeProgramme]),
                URIRef(SKOS.inScheme),
                URIRef(noeudTypeProgramme),
            )
        )
        g.add(
            (
                URIRef(noeudTypeProgramme),
                URIRef(SKOS.hasTopConcept),
                URIRef(uriTypesProgrammes[typeProgramme]),
            )
        )
    for formatDiff in listeFormatDiff:
        uriFormatDiff[formatDiff] = genUriIremus()
        g.add(
            (
                URIRef(uriFormatDiff[formatDiff]),
                URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                URIRef(SKOS.Concept),
            )
        )
        
        g.add(
            (
                URIRef(uriFormatDiff[formatDiff]),
                URIRef(SKOS.prefLabel),
                Literal(formatDiff),
            )
        )
        g.add(
            (
                URIRef(uriFormatDiff[formatDiff]),
                URIRef(SKOS.inScheme),
                URIRef(noeudFormatDiffusion),
            )
        )
        g.add(
            (
                URIRef(noeudFormatDiffusion),
                URIRef(SKOS.hasTopConcept),
                URIRef(uriFormatDiff[formatDiff]),
            )
        )
    return uriTypesProgrammes, uriFormatDiff


def moisToNum(mois):
    # prend un mois en lettre et retourne son équivalent numérique pour coller avec le dataType DateTime
    return {
        "janvier": "01",
        "février": "02",
        "mars": "03",
        "avril": "04",
        "mai": "05",
        "juin": "06",
        "juillet": "07",
        "août": "08",
        "septembre": "09",
        "octobre": "10",
        "novembre": "11",
        "décembre": "12",
    }[mois]


def extractJourDateHeure(horaire):
    # prend un horaire (debut, fin) et renvoie sa decomposition jour, date, heure
    p = re.compile(
        "([a-zA-Z]+) ([0-9]{1,2})-([a-zA-Z]+)-([0-9]{1,2}) ([0-9]{1,2}):([0-9]{1,2})"
    )
    if p.match(horaire) is not None:
        res = p.match(horaire).groups()

        nom_jour, numero_jour, nom_mois, annee, heure, minutes = res
        return (nom_jour, numero_jour, nom_mois, annee, heure, minutes)

def HeuretoDuration(heure):
    heure = str(heure)
    p = re.compile(
        "([0-9]{1,2}):([0-9]{1,2}):00"
    )
    if p.match(heure) is not None:
        res = p.match(heure).groups()
        heure, minutes = res
        duration = "PT" + heure + "H" + minutes +"M"
        return duration

def initHorairesDifProgrammes(horaire):
    if extractJourDateHeure(horaire):
        nom_jour, numero_jour, nom_mois, annee, heure, minutes = extractJourDateHeure(
            horaire
        )
        numero_mois = moisToNum(nom_mois)
        chaineJour = str(numero_jour)
        if int(numero_jour) < 10:
            chaineJour = "0" + chaineJour
        chaineDate = "19" + annee + "-" + numero_mois + "-" + chaineJour
        chaineHeureAbs = heure + ":" + minutes + ":00"
        chaineHeure = heure + ":" + minutes + ":00" + "+01"  # prise en compte UTC+1
        return nom_jour, chaineHeure, chaineDate, chaineHeureAbs


def initProgrammes(dictionnaireUri, noeudTitreProgrammes):
    print("Initialisation des radios")
    uriRadio = initStationsRadio()
    uriTypesProgrammes, uriFormatDiff = initTypeProgEtFormatDiff()
    print("Initialisation des programmes de diffusion")
    for key, value in data["db_radio"].items():
        if key == "programmes":
            for x in value:
                # Chaque programme est ajouté au graphe en tant que chose
                dictionnaireUri[x["IDprog"]] = genUriIremus()
                uri = dictionnaireUri[x["IDprog"]]
                g.add(
                    (
                        URIRef(dictionnaireUri[x["IDprog"]]),
                        URIRef(is_a),
                        URIRef(SCHEMA["BroadcastEvent"]),
                    )
                )
                if x["titre_prog"] in uriTitreProgrammes.keys():
                    g.add(
                        (
                            URIRef(noeudTitreProgrammes),
                            URIRef(SKOS.hasTopConcept),
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                        )
                    )
                    g.add(
                        (
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                            URIRef(SKOS.inScheme),
                            URIRef(noeudTitreProgrammes),
                        )
                    )
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["has_title"]),
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                        )
                    )
                    
                else:
                    uriTitreProgrammes[x["titre_prog"]] = genUriIremus()
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["has_title"]),
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                        )
                    )
                    g.add(
                        (
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                            URIRef(is_a),
                            URIRef(SKOS.Concept),
                        )
                    )
                    g.add(
                        (
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                            URIRef(SKOS.inScheme),
                            URIRef(noeudTitreProgrammes),
                        )
                    )
                    g.add(
                        (
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                            URIRef(SKOS.prefLabel),
                            Literal(x["titre_prog"]),
                        )
                    )
                    g.add(
                        (
                            URIRef(noeudTitreProgrammes),
                            URIRef(SKOS.hasTopConcept),
                            URIRef(uriTitreProgrammes[x["titre_prog"]]),
                        )
                    )
                # On ajoute le lien station de radio diffuse programme
                g.add(
                    (
                        URIRef(dictionnaireUri[x["IDprog"]]),
                        URIRef(SCHEMA["publishedOn"]),
                        URIRef(uriRadio[x["nom_station"]]),
                    )
                )
                # ajout des liens vers type_prog et format_prog
                g.add(
                    (
                        URIRef(uri),
                        URIRef(MUSRAD30["has_type"]),
                        URIRef(uriTypesProgrammes[x["type_prog"]]),
                    )
                )
                
                g.add(
                    (
                        URIRef(uri),
                        URIRef(MUSRAD30["has_format"]),
                        URIRef(uriFormatDiff[x["format_dif"]]),
                    )
                )
                # ajoutHorairesDiffusion
                hDeb = 0,
                hFin = 0
                if initHorairesDifProgrammes(x["horaire_debut_dif"]):
                    jDeb, hDeb, dDeb, hAbsDeb = initHorairesDifProgrammes(x["horaire_debut_dif"])
                    dateTime = dDeb + "T" + hDeb
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["jour_debut_diffusion"]),
                            Literal(jDeb),
                        )
                    )
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SCHEMA["startDate"]),
                            Literal(dateTime, datatype=XSD.DateTime),
                        )
                    )

                if initHorairesDifProgrammes(x["horaire_fin_dif"]):
                    jFin, hFin, dFin, hAbsFin = initHorairesDifProgrammes(x["horaire_fin_dif"])
                    dateTime = dFin + "T" + hFin
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["jour_fin_diffusion"]),
                            Literal(jFin),
                        )
                    )
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SCHEMA["endDate"]),
                            Literal(dateTime, datatype=XSD.DateTime),
                        )
                    )
                if hAbsDeb != 0 and hAbsFin != 0:
                    # Convert str to strptime
                    a_time = datetime.datetime.strptime(hAbsDeb, "%H:%M:%S")
                    b_time = datetime.datetime.strptime(hAbsFin, "%H:%M:%S")

                    # Convert to timedelta
                    a_delta = datetime.timedelta(hours = a_time.hour,minutes=a_time.minute)
                    b_delta = datetime.timedelta(hours = b_time.hour,minutes=b_time.minute)
                    duration = (b_delta - a_delta)
                    duration = HeuretoDuration(duration)
                    if duration:
                    #ajouter la duree si celle-ci ok
                        g.add(
                            (
                                URIRef(uri),
                                URIRef(SCHEMA["duration"]),
                                Literal(duration, datatype=XSD.duration),
                            )
                        )
                    
                g.add(
                    (
                        URIRef(uri),
                        URIRef(SCHEMA["description"]),
                        Literal(x["details_prog"], lang="fr"),
                    )
                )


# Varibles relatives aux Musiciens
noeudMusiciens = genUriIremus()
noeudNationalites = genUriIremus()
noeudStyle = genUriIremus()
noeudSpecialite = genUriIremus()
noeudStatutMusicien = genUriIremus()

# initConceptScheme(noeudMusiciens, "Musiciens")
initConceptScheme(noeudNationalites, "Nationalités")
initConceptScheme(noeudStyle, "Style du Musicien")
initConceptScheme(noeudSpecialite, "Spécialité du Musicien")
initConceptScheme(noeudStatutMusicien, "Statut du Musicien")

uriMusiciens = dict()
uriNationalites = dict()
uriStyle = dict()
uriSpecialite = dict()

# Fonctions relatives aux Musiciens
def checkAnnee(date):
    if date is not None:
        p = re.compile("([0-9]{4})")
        res = p.match(str(date))
        if res:
            return res.group(1)


def initStatutMusicien():
    print("Initialisation des statuts de Musiciens")
    dicoStatut = {"compositeur": genUriIremus(), "interprète": genUriIremus()}
    for cleStatut in dicoStatut.keys():
        g.add((URIRef(dicoStatut[cleStatut]), URIRef(is_a), URIRef(SKOS.Concept),))
        g.add(
            (
                URIRef(dicoStatut[cleStatut]),
                URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
                Literal(cleStatut),
            )
        )
        g.add(
            (
                URIRef(noeudStatutMusicien),
                URIRef(SKOS.hasTopConcept),
                URIRef(dicoStatut[cleStatut]),
            )
        )
        g.add(
            (
                URIRef(dicoStatut[cleStatut]),
                URIRef(SKOS.inScheme),
                URIRef(noeudStatutMusicien),
            )
        )
    return dicoStatut


uriStatut = initStatutMusicien()


def initNationalite(x):
    if x.get("nationalite_musicien", "") != "":
        nationalite = x["nationalite_musicien"]
        if isinstance(nationalite, str):
            if nationalite not in list(uriNationalites.keys()):
                uriNat = uriNationalites[str(nationalite)] = genUriIremus()

                g.add((URIRef(uriNat), URIRef(is_a), URIRef(SKOS.Concept),))
                g.add((URIRef(uriNat), URIRef(is_a), URIRef(SCHEMA["Country"])))
                g.add((URIRef(uriNat), URIRef(SKOS.prefLabel), Literal(nationalite),))
                g.add(
                    (URIRef(uriNat), URIRef(SKOS.inScheme), URIRef(noeudNationalites),)
                )
                g.add(
                    (
                        URIRef(noeudNationalites),
                        URIRef(SKOS.hasTopConcept),
                        URIRef(uriNat),
                    )
                )
            # On lie le Musicien à sa nationalite
            uriNat = uriNationalites[nationalite]
            g.add(
                (
                    URIRef(uriMusiciens[x["IDmusiciens"]]),
                    URIRef(SCHEMA["nationality"]),
                    URIRef(uriNat),
                )
            )



def initSpecialite(x):
    if x.get("specialite", "") != "":
        specialite = x["specialite"]
        if isinstance(specialite, str):
            if specialite not in list(uriSpecialite.keys()):
                uriSpecialite[specialite] = genUriIremus()
                uriSpe = uriSpecialite[specialite]
                g.add((URIRef(uriSpe), URIRef(is_a), URIRef(SKOS.Concept),))
                g.add((URIRef(uriSpe), URIRef(SKOS.prefLabel), Literal(specialite),))
                g.add((URIRef(uriSpe), URIRef(SKOS.inScheme), URIRef(noeudSpecialite),))
                g.add(
                    (
                        URIRef(noeudSpecialite),
                        URIRef(SKOS.hasTopConcept),
                        URIRef(uriSpe),
                    )
                )
            uriSpe = uriSpecialite[specialite]
            g.add(
                (
                    URIRef(uriMusiciens[x["IDmusiciens"]]),
                    URIRef(MUSRAD30["has_speciality"]),
                    URIRef(uriSpe),
                )
            )



def initStyle(x):
    if x.get("style", "") != "":
        style = x["style"]
        if isinstance(style, str):
            if style not in list(uriStyle.keys()):
                uriStyle[style] = genUriIremus()
                uriSty = uriStyle[style]
                g.add((URIRef(uriSty), URIRef(is_a), URIRef(SKOS.Concept),))
                g.add((URIRef(uriSty), URIRef(SKOS.prefLabel), Literal(style),))
                g.add((URIRef(uriSty), URIRef(SKOS.inScheme), URIRef(noeudStyle),))
                g.add((URIRef(noeudStyle), URIRef(SKOS.hasTopConcept), URIRef(uriSty),))
                # On lie le Musicien à sa specialite
            uriSty = uriStyle[style]
            g.add(
                (
                    URIRef(uriMusiciens[x["IDmusiciens"]]),
                    URIRef(MUSRAD30["has_style"]),
                    URIRef(uriSty),
                )
            )
            


def initMusiciens():
    print("Initialisation des Musiciens")
    for key, value in data["db_radio"].items():
        if key == "musiciens":
            for x in value:
                uriMusiciens[x["IDmusiciens"]] = genUriIremus()
                uri = uriMusiciens[x["IDmusiciens"]]
                g.add((URIRef(uri), URIRef(is_a), URIRef(SCHEMA["Person"])))
                g.add((URIRef(uri), URIRef(MUSRAD30["id"]), Literal(x["IDmusiciens"])))

                if x["IDmusiciens"] in lienswiki:
                    g.add((URIRef(uri), URIRef(RDFS.seeAlso), Literal(lienswiki[x["IDmusiciens"]])))
                
                initNationalite(x)
                initSpecialite(x)
                initStyle(x)

                prenom = x.get("prenom_musiciens", "")
                if prenom:
                    Label = str(prenom) + " " + str(x["nom_musiciens"])
                    g.add((URIRef(uri), URIRef(FOAF.givenName), Literal(prenom),))
                    g.add((URIRef(uri), URIRef(FOAF.firstName), Literal(prenom),))
                else:
                    Label = str(x["nom_musiciens"])

                g.add(
                    (URIRef(uri), URIRef(FOAF.familyName), Literal(x["nom_musiciens"]),)
                )
                g.add(
                    (URIRef(uri), URIRef(FOAF.surname), Literal(x["nom_musiciens"]),)
                )
                g.add((URIRef(uri), URIRef(FOAF.name), Literal(Label),))
                
                chaineDatesRdfs = ""
                
                if checkAnnee(x.get("naissance_musiciens", "N/A")):
                    annee = checkAnnee(x["naissance_musiciens"])
                    g.add((URIRef(uri), URIRef(SCHEMA["birthDate"]), Literal(annee),))
                    chaineDatesRdfs = "(" + annee + "-"
                else:
                    chaineDatesRdfs = "(????-"
                if checkAnnee(x.get("deces_musiciens", "N/A")):
                    annee = checkAnnee(x["deces_musiciens"])
                    g.add((URIRef(uri), URIRef(SCHEMA["deathDate"]), Literal(annee),))
                    chaineDatesRdfs += annee + ")"
                else:
                    chaineDatesRdfs += "????)"
                
                if prenom:
                    g.add(
                        (
                            URIRef(uri), URIRef(RDFS.label), Literal(str(x["nom_musiciens"]) + ", " + prenom + " " + chaineDatesRdfs)
                        )
                    )
                else :
                    g.add(
                        (
                            URIRef(uri), URIRef(RDFS.label), Literal(str(x["nom_musiciens"]) + ", " + " " + chaineDatesRdfs)
                        )
                    )
                # infosMusicien
                if x["infos_musiciens"] != "":
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SCHEMA["description"]),
                            Literal(x["infos_musiciens"]),
                        )
                    )
                # statutMusicien
                if x["statut"] == "compositeur":
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["has_status"]),
                            URIRef(uriStatut["compositeur"]),
                        )
                    )

                elif x["statut"] == "interprète":
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["has_status"]),
                            URIRef(uriStatut["interprète"]),
                        )
                    )

                elif x["statut"] == "Compositeur - Interprète":
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["has_status"]),
                            URIRef(uriStatut["compositeur"]),
                        )
                    )

                    g.add(
                        (
                            URIRef(uri),
                            URIRef(MUSRAD30["has_status"]),
                            URIRef(uriStatut["interprète"]),
                        )
                    )



def initMusiciensCat():
    print("Initialisation des relations entre Musiciens et sous-catégories")
    for key, value in data["db_radio"].items():
        if key == "musicienscat":
            for x in value:
                if (x["IDcatmusiciens"] in uriMusiciens.keys()) and (
                    x["IDmusicienssscat"] in uriSousCat.keys()
                ):
                    g.add(
                        (
                            URIRef(uriMusiciens[x["IDcatmusiciens"]]),
                            URIRef(MUSRAD30["a_pour_sous_categorie_musicale"]),
                            URIRef(uriSousCat[x["IDmusicienssscat"]]),
                        )
                    )



# Gestion des diffusions

# Variables relatives aux diffusions
dicoPM = defaultdict(
    list
)  # programme -> a chaque programme associe des triplets titre oeuvre, id musicien, statut musicien
oeuvresTitreesParCompositeur = dict()

uriOeuvresCnT = {}
uriOeuvreCT = {}
uriOeuvres_nCT = {}
uriPlages = {}
uriPerfs = {}

# Fonctions relatives aux diffusions
def initDicoProgOeuvresComposees():
    # initialise le dictionnaire associant a chaque prog id la liste des triplets d'une diffusion
    for key, value in data["db_radio"].items():
        if key == "diffusion":
            for x in value:
                dicoPM[x["progID"]].append(
                    (x["titre_oeuvre"], x["musiciensID"], x["statutdif"])
                )


def getNbComp(listeMusiciens):
    nbComp = 0
    listecomp = []
    for x in listeMusiciens:
        if x[2] == "compositeur":
            nbComp += 1
            listecomp.append(x[1])
    return nbComp, listecomp


def getCompositeur(prog_id, titre_oeuvre):
    # retourne la liste des id des compositeurs apparaissant dans le programme
    lCompositeurs = []
    for musicien in dicoPM[prog_id]:
        if musicien[0] == titre_oeuvre and musicien[2] == "compositeur":
            lCompositeurs.append(musicien[1])
    return lCompositeurs


def initOEuvresTitreesParCompositeur():
    for diffusion in data["db_radio"]["diffusion"]:
        if diffusion["statutdif"] == "compositeur" and diffusion["titre_oeuvre"] != "":
            if diffusion["musiciensID"] not in oeuvresTitreesParCompositeur:
                oeuvresTitreesParCompositeur[diffusion["musiciensID"]] = []
            if (
                diffusion["titre_oeuvre"]
                not in oeuvresTitreesParCompositeur[diffusion["musiciensID"]]
            ):
                oeuvresTitreesParCompositeur[diffusion["musiciensID"]].append(
                    diffusion["titre_oeuvre"]
                )


def assoOeuvreComp(prog_id):
    # renvoie un dico contenant pour clé un nom d'oeuvre et pour valeur la liste des compositeurs associés
    liste = dicoPM.get(prog_id)
    dicoOeuvreComp = defaultdict(list)
    for d in liste:
        if d[2] == "compositeur":
            dicoOeuvreComp[d[0]].append(d[1])
    return dicoOeuvreComp


def nbOeuvresProgrammes(prog_id):
    # retourne le nombre de titre d'oeuvres differents diffusees dans un programme
    liste = dicoPM.get(prog_id)
    oeuvres_dif = []
    for l in liste:
        if l[0] not in oeuvres_dif:
            oeuvres_dif.append(l[0])
    nbOeuvresDiffusees = len(oeuvres_dif)
    return nbOeuvresDiffusees


def titreOeuvresProgrammes(prog_id):
    # retourne le nombre de titre d'oeuvres differents diffusees dans un programme
    liste = dicoPM.get(prog_id)
    oeuvres_dif = []
    for l in liste:
        if l[0] not in oeuvres_dif:
            oeuvres_dif.append(l[0])
    return oeuvres_dif


def initDiffusions():
    print("Initialisation des diffusions")
    for prog_id, diffusions in dicoPM.items():
        CT = []
        CnT = []
        nCT = []
        nCnT = []
        dicoOeuvresCompositeurs = assoOeuvreComp(prog_id)
        for d in diffusions:

            if d[2] == "compositeur" and d[0] != "":
                CT.append(d)
            elif d[2] == "compositeur" and d[0] == "":
                CnT.append(d)
            elif d[2] == "interprète" and d[0] != "":
                nCT.append(d)
            elif d[2] == "interprète" and d[0] == "":
                nCnT.append(d)

        for d in CT:
            if (d[0], d[1]) not in uriOeuvreCT:
                if len(dicoOeuvresCompositeurs[d[0]]) == 1:
                    # Dans le programme, un seul compositeur associe au titre de l'oeuvre
                    uriOeuvre = uriOeuvreCT[(d[0], d[1])] = genUriIremus()
                    g.add(
                        (
                        URIRef(uriOeuvre),
                        URIRef(is_a),
                        URIRef(SCHEMA["MusicComposition"]),
                        )
                    )
                    g.add(
                        (
                            URIRef(uriOeuvre),
                            URIRef(SCHEMA["composer"]),
                            URIRef(uriMusiciens[d[1]]),
                        )
                    )
                    g.add((URIRef(uriOeuvre), URIRef(SCHEMA["name"]), Literal(d[0]),))
                else:
                    # plus d'un compositeur associe a l'oeuvre, on va chercher si (titre_oeuvre, id_autre_compositeur) n'a pas deja une uri
                    uriExistante = None
                    for idMus in dicoOeuvresCompositeurs[d[0]]:
                        if (d[0], idMus) in uriOeuvreCT.keys():
                            uriExistante = uriOeuvreCT[(d[0], idMus)]
                    if uriExistante:
                        uriOeuvreCT[(d[0], d[1])] = uriExistante
                        uriOeuvre = uriOeuvreCT[(d[0], d[1])]
                        g.add(
                            (
                                URIRef(uriOeuvre),
                                URIRef(SCHEMA["composer"]),
                                URIRef(uriMusiciens[d[1]]),
                            )
                        )
                        
                    else:
                        uriOeuvreCT[(d[0], d[1])] = genUriIremus()
                        uriOeuvre = uriOeuvreCT[(d[0], d[1])]
                        g.add(
                            (
                            URIRef(uriOeuvre),
                            URIRef(is_a),
                            URIRef(SCHEMA["MusicComposition"]),
                            )
                        )
                        g.add(
                            (
                                URIRef(uriOeuvre),
                                URIRef(SCHEMA["composer"]),
                                URIRef(uriMusiciens[d[1]]),
                            )
                        )
                        
                        g.add(
                            (URIRef(uriOeuvre), URIRef(SCHEMA["name"]), Literal(d[0]),)
                        )

            uriOeuvre = uriOeuvreCT[(d[0], d[1])]
            uriPlage = uriPlages[(prog_id, uriOeuvre)] = genUriIremus()
            uriPerf = uriPerfs[(prog_id, uriOeuvre)] = genUriIremus()
            g.add(
                (
                    URIRef(uriPerf),
                    URIRef(is_a),
                    URIRef(SCHEMA["MusicEvent"]),
                )
            )
            g.add(
                (
                    URIRef(uriPerf),
                    URIRef(SCHEMA["workPerformed"]),
                    URIRef(uriOeuvre),
                )
            )
            
            g.add((URIRef(uriPlage), URIRef(is_a), URIRef(SCHEMA["BroadcastEvent"]),))
            g.add(
                (
                    URIRef(uriPlage),
                    URIRef(SCHEMA["superEvent"]),
                    URIRef(uriProgrammes[prog_id]),
                )
            )
            g.add(
                (
                    URIRef(uriProgrammes[prog_id]),
                    URIRef(SCHEMA["subEvent"]),
                    URIRef(uriPlage),
                )
            )
            g.add(
                (
                    URIRef(uriPlage),
                    URIRef(SCHEMA["broadcastOfEvent"]),
                    URIRef(uriPerf),
                )
            )

        for d in CnT:
            if (prog_id, d[1]) not in uriOeuvresCnT:
                uriOeuvre = uriOeuvresCnT[(prog_id, d[1])] = genUriIremus()
                g.add(
                    (
                        URIRef(uriOeuvre),
                        URIRef(SCHEMA["composer"]),
                        URIRef(uriMusiciens[d[1]]),
                    )
                )
                g.add(
                    (
                        URIRef(uriOeuvre),
                        URIRef(is_a),
                        URIRef(SCHEMA["MusicComposition"]),
                    )
                )
                

            uriOeuvre = uriOeuvresCnT[(prog_id, d[1])]
            uriPlage = uriPlages[(prog_id, uriOeuvre)] = genUriIremus()
            uriPerf = uriPerfs[(prog_id, uriOeuvre)] = genUriIremus()
            g.add(
                (
                    URIRef(uriPerf),
                    URIRef(is_a),
                    URIRef(SCHEMA["MusicEvent"]),
                )
            )
            g.add(
                (
                    URIRef(uriPerf),
                    URIRef(SCHEMA["workPerformed"]),
                    URIRef(uriOeuvre),
                )
            )
            
            g.add((URIRef(uriPlage), URIRef(is_a), URIRef(SCHEMA["BroadcastEvent"]),))
            g.add(
                (
                    URIRef(uriPlage),
                    URIRef(SCHEMA["superEvent"]),
                    URIRef(uriProgrammes[prog_id]),
                )
            )
            g.add(
                (
                    URIRef(uriProgrammes[prog_id]),
                    URIRef(SCHEMA["subEvent"]),
                    URIRef(uriPlage),
                )
            )
            g.add(
                (
                    URIRef(uriPlage),
                    URIRef(SCHEMA["broadcastOfEvent"]),
                    URIRef(uriPerf),
                )
            )

        # Gestion de nCT
        dicoTitres = {}
        dicoTitrePerf = {}
        dicoTitrePlage = {}
        for d in nCT:
            if d[0] in [_[0] for _ in CT]:
                lcompositeur = getCompositeur(prog_id, d[0])
                if lcompositeur:
                    compositeur = lcompositeur[0]
                    uri = uriPerfs[(prog_id, uriOeuvreCT[(d[0], compositeur)])]
                    g.add(
                        (
                            URIRef(uri),
                            URIRef(SCHEMA["performer"]),
                            URIRef(uriMusiciens[d[1]]),
                        )
                    )
            else:
                if d[0] in dicoTitres:
                    g.add(
                        (
                            
                            URIRef(dicoTitrePerf[dicoTitres[d[0]]]),
                            URIRef(SCHEMA["performer"]),
                            URIRef(uriMusiciens[d[1]]),
                        )
                    )
                    
                else:
                    dicoTitres[d[0]] = genUriIremus()
                    dicoTitrePerf[dicoTitres[d[0]]] = genUriIremus()
                    dicoTitrePlage[dicoTitres[d[0]]] = genUriIremus()
                    g.add((URIRef(dicoTitres[d[0]]), URIRef(is_a), URIRef(SCHEMA["MusicComposition"]),))
                    g.add(
                        (
                            URIRef(dicoTitrePerf[dicoTitres[d[0]]]),
                            URIRef(is_a),
                            URIRef(SCHEMA["MusicEvent"]),
                        )
                    )
                    g.add(
                        (
                            URIRef(dicoTitrePlage[dicoTitres[d[0]]]),
                            URIRef(is_a),
                            URIRef(SCHEMA["BroadcastEvent"]),
                        )
                    )
                    g.add(
                        (
                            URIRef(dicoTitres[d[0]]),
                            URIRef(SCHEMA["name"]),
                            Literal(d[0]),
                        )
                    )
                    g.add(
                        (
                            URIRef(dicoTitrePerf[dicoTitres[d[0]]]),
                            URIRef(SCHEMA["workPerformed"]),
                            URIRef(dicoTitres[d[0]]),
                        )
                    )
                    g.add(
                        (
                            URIRef(dicoTitrePlage[dicoTitres[d[0]]]),
                            URIRef(SCHEMA["superEvent"]),
                            URIRef(uriProgrammes[prog_id]),
                        )
                    )
                    g.add(
                        (
                            URIRef(uriProgrammes[prog_id]),
                            URIRef(SCHEMA["subEvent"]),
                            URIRef(dicoTitrePlage[dicoTitres[d[0]]]),
                        )
                    )
                    g.add(
                        (
                            
                            URIRef(dicoTitrePerf[dicoTitres[d[0]]]),
                            URIRef(SCHEMA["performer"]),
                            URIRef(uriMusiciens[d[1]]),
                        )
                    )
                    g.add(
                        (
                            URIRef(dicoTitrePlage[dicoTitres[d[0]]]),
                            URIRef(SCHEMA["broadcastOfEvent"]),
                            URIRef(dicoTitrePerf[dicoTitres[d[0]]]),
                        )
                    )
        # gestion nCnT
        if CnT:
            for x in CnT:
                uriOeuvre = uriOeuvresCnT[(prog_id, x[1])]
                uriPlage = uriPlages[(prog_id, uriOeuvre)]
                uriPerf = uriPerfs[(prog_id, uriOeuvre)]
                for y in nCnT:
                    g.add(
                        (
                            URIRef(uriPerf),
                            URIRef(SCHEMA["performer"]),
                            URIRef(uriMusiciens[y[1]]),
                            
                        )
                    )

        else:
            uriOeuvre = genUriIremus()
            uriPlage = genUriIremus()
            uriPerf = genUriIremus()
            g.add((URIRef(uriOeuvre), URIRef(is_a), URIRef(SCHEMA["MusicComposition"]),))
 
            g.add(
                (
                URIRef(uriPerf),
                URIRef(is_a),
                URIRef(SCHEMA["MusicEvent"]),
                )
            )
            g.add((URIRef(uriPlage), URIRef(is_a), URIRef(SCHEMA["BroadcastEvent"]),))
            g.add(
                (
                    URIRef(uriPerf),
                    URIRef(SCHEMA["workPerformed"]),
                    URIRef(uriOeuvre),
                )
            )
            g.add(
                (
                    URIRef(uriPlage),
                    URIRef(SCHEMA["broadcastOfEvent"]),
                    URIRef(uriPerf),
                )
            )
            g.add(
                (
                    URIRef(uriPlage),
                    URIRef(SCHEMA["superEvent"]),
                    URIRef(uriProgrammes[prog_id]),
                )
            )
            g.add(
                (
                    URIRef(uriProgrammes[prog_id]),
                    URIRef(SCHEMA["subEvent"]),
                    URIRef(uriPlage),
                )
            )
        for d in nCnT:
            g.add(
                (
                    URIRef(uriPerf),
                    URIRef(SCHEMA["performer"]),
                    URIRef(uriMusiciens[d[1]]),
                )
            )
            

# Début du programme

with open(other_file_path) as json_file:
    data = json.load(json_file)
    initCategoriesSousCategories()
    initProgrammes(uriProgrammes, noeudTitreProgrammes)
    initMusiciens()
    initMusiciensCat()

    # Traitement des diffusions
    initOEuvresTitreesParCompositeur()
    initDicoProgOeuvresComposees()
    initDiffusions()

# ecriture de la serialisation dans un fichier .ttl
print("Ecriture du fichier")
with open("musrad30.ttl", "w") as f:
    output = f"@base <{IREMUS}> .\n" + \
        g.serialize(format="turtle").decode("utf-8")
    f.write(output)

print("fin du script")

