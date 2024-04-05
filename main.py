
# known issues: eheal for "Necropolis Acolyte gains 113 health from Qurv's Pain Spike.#529" is wrong (keeps value from previous eheal for whatever reason)


import pandas as pd
import os
from pathlib import Path

from helper.parsers import *
from helper.patterns import *
from helper.syncer import *
from helper.calculator import *
from helper.visualiser import *

print("ToDo: Get Players and Hunter Pets from SavedVariables\n\
      Boss fight starts when fight starts\n\
      add incombat to SavedVariables")
# folder = r"240330_MC"
folder = r"240404_Nax"
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
    dungeon = filename.split("_")[2]
    file = open(filepath, 'r')
    lines = file.readlines()
    for idx, line in enumerate(lines):
        if (idx%1000==0) or (idx==len(lines)-1):
            print("Parsing line "+str(idx+1)+"/"+str(len(lines)), end='\r')
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
    dungeon = filename.split("_")[2]
    file = open(filepath, 'r')
    string = file.read()
    ParseKikilogs(data_source, string, dict_log, players)


######################
# SYNC AND SORT LOGS #
######################
list_log = SyncDictLogMaster(dict_log, t_delta_max)
print("Sort list by timestamp...")
list_log = sorted(list_log, key=lambda x: x["timestamp"])
timestamp_0 = list_log[0]["timestamp"]
for idx in range(len(list_log)):
    list_log[idx]["timestamp"] -= timestamp_0

###################
# CALCULATE STUFF #
###################
CalcStuff(list_log, t_cd_section)


###############
# EXPORT DATA #
###############
df = pd.DataFrame(list_log)
# df["timestamp"] = df["timestamp"]-df.loc[0,"timestamp"]
# print(df[df["source"]=="Kikidora"]["eheal"].sum())
# print(df[(df["source"]=="Kikidora") & (df["section"]!="")]["eheal"].sum())
# df.to_excel("Test2.xlsx")
Visualise(df, players)

# df[(df["subkind"]=="HEAL") ].to_excel("Test5.xlsx")