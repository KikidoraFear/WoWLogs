
# known issues: eheal for "Necropolis Acolyte gains 113 health from Qurv's Pain Spike.#529" is wrong (keeps value from previous eheal for whatever reason)


import pandas as pd
import os
from pathlib import Path

from helper.parsers import *
from helper.patterns import *
from helper.syncer import *
from helper.calculator import *
from helper.visualiser import *

folder = r"Logfiles/240411_Nax_ACL"
t_delta_max = 1 # if the same entry is spotted from another source within this time interval, it's discarded
t_cd_section = 10 # Cooldown of section (last time boss appeared in combat log)

###################
# PARSE COMBATLOG #
###################
patterns_base = PreparePatterns(patterns_base)
filepaths = [os.path.join(folder, f) for f in os.listdir(folder) if "WoWCombatLog" in f]
dict_log = {}
for filepath in filepaths:
    print("Reading ", filepath)
    filename = Path(filepath).stem
    data_kind = filename.split("_")[0]
    data_source = filename.split("_")[1]
    file = open(filepath, 'r', encoding='utf-8') # utf-8 better than charmap (default)
    lines = file.readlines()
    for idx, line in enumerate(lines):
        if (idx%1000==0) or (idx==len(lines)-1):
            print("Parsing line "+str(idx+1)+"/"+str(len(lines)), end='\r')
        if (not "COMBATANT_INFO:" in line) & (not "CONSOLIDATED:" in line): # skip advanced combat log shenanigans (adds that kind of stuff)
            ParseCombatLog(data_source, line, patterns_base, dict_log)
    print()

#################
# PARSE KIKILOG #
#################
filepaths = [os.path.join(folder, f) for f in os.listdir(folder) if "Kikilogs" in f]
players = {}
for filepath in filepaths:
    print("Reading ", filepath)
    filename = Path(filepath).stem
    data_kind = filename.split("_")[0]
    data_source = filename.split("_")[1]
    file = open(filepath, 'r')
    string = file.read()
    ParseKikilogs(data_source, string, dict_log, players)


######################
# SYNC AND SORT LOGS #
######################
list_log = SyncDictLogMaster(dict_log, t_delta_max)

###################
# CALCULATE STUFF #
###################
CalcStuff(list_log, t_cd_section)

###########################
# VISUALISE & EXPORT DATA #
###########################
df = pd.DataFrame(list_log)
Visualise(df, players, folder)

# df[(df["subkind"]=="HEAL") ].to_excel("Test5.xlsx")