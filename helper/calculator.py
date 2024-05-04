bosses = [
    # Ahn'Qiraj
    "Arygos", "Battleguard Sartura", "C'Thun", "Emperor Vek'lor", "Emperor Vek'nilash", "Eye of C'Thun", "Fankriss the Unyielding", 
        "Merithra of the Dream", "Ouro", "Princess Huhuran", "The Master's Eye", "The Prophet Skeram", "Viscidus",
        "Lord Kri", "Princess Yauj", "Vem",
        "Sartura's Royal Guard"
    # Naxxramas
    "Anub'Rekhan", "Grand Widow Faerlina", "Maexxna", "Patchwerk", "Grobbulus", "Gluth", "Thaddius", "Noth the Plaguebringer", "Heigan the Unclean", "Loatheb",
        "Instructor Razuvious", "Gothik the Harvester", "Sapphiron", "Kel'Thuzad", "Lady Blaumeux", "Thane Korth'azz", "Highlord Mograine", "Sir Zeliek",
        "Stalagg", "Feugen",
        "Unrelenting Trainee", "Unrelenting Deathknight", "Unrelenting Rider", "Spectral Trainee", "Spectral Deathknight", "Spectral Rider"
    # Zul'Gurub
    "High Priestess Jeklik", "High Priest Venoxis", "High Priestess Mar'li", "High Priest Thekal", "High Priestess Arlokk",
        "Hakkar", "Bloodlord Mandokir", "Jin'do the Hexxer", "Gahz'ranka", "Gri'lek",
    # The Molten Core
    "Baron Geddon", "Garr", "Gehennas", "Golemagg the Incinerator", "Lucifron", "Magmadar", "Shazzrah", "Sulfuron Harbinger", "Majordomo Executus", "Ragnaros",
        "Flamewaker Elite", "Flamewaker Healer", "Son of Flame", "Flamewaker Priest"
    # Blackwing Lair
    "Broodlord Lashlayer", "Chromaggus", "Ebonroc", "Firemaw", "Flamegor", "Lord Victor Nefarius", "Razorgore the Untamed", "Vaelastrasz the Corrupt", "Nefarian",
    # ES
    "Erennius", "Solnius",
    # Onyxia
    "Onyxia"
]

bosses_translator = {
    # The Molten Core
    "Flamewaker Elite": "Majordomo Executus",
    "Flamewaker Healer": "Majordomo Executus",
    "Son of Flame": "Ragnaros",
    "Flamewaker Priest": "Sulfuron Harbinger",
    # BWL
    "Lord Victor Nefarius": "Nefarian",
    # Ahn'Qiraj
    "Sartura's Royal Guard": "Battleguard Sartura",
    "Lord Kri": "Bug Trio",
    "Princess Yauj": "Bug Trio",
    "Vem": "Bug Trio",
    "Emperor Vek'lor": "Twin Emperors",
    "Emperor Vek'nilash": "Twin Emperors",
    "Eye of C'Thun": "C'Thun",
    # Naxxramas
    "Lady Blaumeux": "Four Horsemen",
    "Thane Korth'azz": "Four Horsemen",
    "Highlord Mograine": "Four Horsemen",
    "Sir Zeliek": "Four Horsemen",
    "Stalagg": "Stalagg and Feugen",
    "Feugen": "Stalagg and Feugen",
    "Unrelenting Trainee": "Gothik the Harvester",
    "Unrelenting Deathknight": "Gothik the Harvester",
    "Unrelenting Rider": "Gothik the Harvester",
    "Spectral Trainee": "Gothik the Harvester",
    "Spectral Deathknight": "Gothik the Harvester",
    "Spectral Rider": "Gothik the Harvester"
}

def CalcStuff(list_log, t_cd_section):
    # Init
    # Calc Sections
    inp_calc_sections = {
        "incombat": False,
        "t_incombat": 0,
        "section": "",
        #"attempt": {}, # attempt[Ouro] = 1
        "t_section": 0,
        "t_cd_section": t_cd_section
    }

    print("Calculate stuff...")
    for idx in range(len(list_log)):
        if (idx%1000==0) or (idx==len(list_log)-1):
            print("Line", idx+1, "/", len(list_log), end="\r")

        # Calc Sections
        CalcSections(list_log[idx], inp_calc_sections)

    print()

def CalcSections(line_log, inp):

    # incombat
    if line_log["kind"] == "DAMAGE":
        inp["incombat"] = True
        inp["t_incombat"] = line_log["timestamp"]
    if line_log["timestamp"] > inp["t_incombat"]+inp["t_cd_section"]:
        inp["incombat"] = False
    line_log["incombat"] = inp["incombat"]

    # sections (bosses)
    # -> sometimes boss is in logs without incombat (e.g. hunter's mark) -> no boss section
    # -> sometimes boss fight starts without boss being in the logs (Gothik) -> boss translator
    if (line_log["source"] in bosses) and (line_log["kind"] == "DAMAGE"):# and inp["incombat"]:
        inp["section"] = line_log["source"]
        inp["t_section"] = line_log["timestamp"]
    elif (line_log["target"] in bosses) and (line_log["kind"] == "DAMAGE"):# and inp["incombat"]:
        inp["section"] = line_log["target"]
        inp["t_section"] = line_log["timestamp"]
    if (line_log["timestamp"] > inp["t_section"]+inp["t_cd_section"]) and not inp["incombat"]:
        inp["section"] = ""

    if inp["section"] in bosses_translator:
        inp["section"] = bosses_translator[inp["section"]]

    line_log["section"] = inp["section"]