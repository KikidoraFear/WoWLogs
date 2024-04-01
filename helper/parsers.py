import re
import datetime
import time

def PrepareLine(line, data_source):
    #  Replace You with data_source
    if (not "'s " in line) and (not " your " in line): # special case: "You gain %d health from %s." all other "..health from.." have either "'s" or "your" in them
        line = line.replace("health from", "health from "+data_source+"'s")
    line = line.replace("You gain", data_source+" gains")
    line = line.replace("You hit", data_source+" hits")
    line = line.replace("You lose", data_source+" loses")
    line = line.replace("You crit", data_source+" crits")
    line = line.replace("You reflect", data_source+" reflects")
    line = line.replace("You begin", data_source+" begins")
    line = line.replace("You fail", data_source+" fails")
    line = line.replace("You are", data_source+" is")
    line = line.replace("You suffer", data_source+" suffers")
    line = line.replace("You die", data_source+" dies")
    line = line.replace("You absorb", data_source+" absorbs")
    line = line.replace("You cast", data_source+" casts")
    line = line.replace("You fall and lose", data_source+" falls and loses")
    line = line.replace("You have slain", data_source+" has slain")
    line = line.replace("You attack", data_source+" attacks")
    line = line.replace("You dodge", data_source+" dodges")
    line = line.replace("You miss", data_source+" misses")
    line = line.replace("Your", data_source+"'s")
    line = line.replace("your", data_source+"'s")
    line = line.replace("you", data_source)
    return line

def ParseTimeStamp(line):
    pattern = r"(\d+)/(\d+) (\d+):(\d+):(\d+).(\d+)  (.*)"
    match = re.search(pattern, line)
    year = 2024
    month = int(match.group(1))
    day = int(match.group(2))
    hour = int(match.group(3))
    minute = int(match.group(4))
    second = int(match.group(5))
    millisecond = int(match.group(6))
    rem = match.group(7)
    date_time = datetime.datetime(year,month,day,hour,minute,second)
    timestamp = time.mktime(date_time.timetuple())+millisecond/1000
    
    return rem, timestamp

def ParseLine(line_mod, timestamp, patterns_base, data_source):
    dict_line = {
        "line_mod": line_mod,
        "data_source": [data_source],
        "timestamp": [timestamp],
        "valid": [True],
        "line_name": "",
        "pattern": "",
        "source": "",
        "target": "",
        "spell": "",
        "school": "",
        "value": None,
        "kind": "",
        "subkind": "",
        "eheal": [None],
        "oheal": [None]        
    }
    pattern_found = False
    for pattern_base in patterns_base:
        pattern = pattern_base[1]
        match = re.search(pattern, line_mod)
        if match:
            dict_line["line_name"] = pattern_base[0]
            dict_line["pattern"] = pattern_base[1]
            for idx, kind in enumerate(pattern_base[2]):
                if kind == "value":
                    dict_line[kind] = int(match.group(idx+1))
                else:
                    dict_line[kind] = match.group(idx+1)
            dict_line["kind"] = pattern_base[3]
            dict_line["subkind"] = pattern_base[4]
            pattern_found = True
            break
    if not pattern_found:
        print("Pattern not found:", line_mod)
    return dict_line

def ParseCombatLog(data_source, line, patterns_base, dict_log): # add dict_line_cache
    line, timestamp = ParseTimeStamp(line)
    line_mod = PrepareLine(line, data_source)
    if line_mod in dict_log:
        dict_log[line_mod]["data_source"].append(data_source)
        dict_log[line_mod]["timestamp"].append(timestamp)
        dict_log[line_mod]["valid"].append(True)
        dict_log[line_mod]["eheal"].append(None)
        dict_log[line_mod]["oheal"].append(None)
    else:
        dict_line = ParseLine(line_mod, timestamp, patterns_base, data_source)
        dict_log[line_mod] = dict_line

def ParseKikilogs(data_source, string, dict_log, player_names):
    re_result = re.search('Kikilogs_data_heal = "(.*)"\n', string)
    data_heal = re_result.group(1)
    lines = data_heal.split("$")
    for idx, line in enumerate(lines):
        if (idx%1000==0) or (idx==len(lines)-1):
            print("Parsing line "+str(idx+1)+"/"+str(len(lines)), end='\r')
        data_heal_list = line.split("#")
        if len(data_heal_list) == 4:
            timestamp = float(data_heal_list[0])
            line_mod = PrepareLine(data_heal_list[1], data_source)
            eheal = int(data_heal_list[2])
            oheal = int(data_heal_list[3])
            if line_mod in dict_log:
                dict_log[line_mod]["data_source"].append(data_source + "_Kikilogs")
                dict_log[line_mod]["timestamp"].append(timestamp)
                dict_log[line_mod]["valid"].append(True)
                dict_log[line_mod]["eheal"].append(eheal)
                dict_log[line_mod]["oheal"].append(oheal)
    print()
    re_result = re.search('Kikilogs_data_players = "(.*)"\n', string)
    data_players = re_result.group(1)
    lines = data_players.split("$")
    for idx, line in enumerate(lines):
        data_players_list = line.split("#")
        if data_players_list[0]:
            player_names.append(data_players_list[0])