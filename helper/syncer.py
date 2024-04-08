
import statistics
import numpy as np

def SyncTimeOffsets(dict_log):
    master = ""
    timestamps_delta = {}
    for line_mod in dict_log:

        # Sort timestamps by data_source
        timestamps_line = {}
        for idx in range(len(dict_log[line_mod]["timestamp"])):
            data_source = dict_log[line_mod]["data_source"][idx]
            if not master: # if master doesnt exist, make first encountered data_source to master
                master = data_source
                print("Using", master, "as master for SyncTimeOffsets")
            timestamp = dict_log[line_mod]["timestamp"][idx]
            if data_source in timestamps_line: # group timestamps for line_mod by data_source
                timestamps_line[data_source].append(timestamp)
            else:
                timestamps_line[data_source] = [timestamp]

        # calculate time offset if same number of entries are found in master
        if master in timestamps_line:
            for data_source in timestamps_line:
                if len(timestamps_line[data_source]) == len(timestamps_line[master]):
                    for idx in range(len(timestamps_line[data_source])):
                        delta = timestamps_line[master][idx] - timestamps_line[data_source][idx]
                        if data_source in timestamps_delta:
                            timestamps_delta[data_source].append(delta)
                        else:
                            timestamps_delta[data_source] = [delta]
    
    # get stats from timestamps_delta for each data_source
    data_source_offset = {}
    for data_source in timestamps_delta:
        # if len(timestamps_delta[data_source])>depth: # only use data_source if certain amount of similar entries found
        data_source_offset[data_source] = statistics.median(timestamps_delta[data_source]) # median probably more accurate than mean (because of outliers)
        print(data_source + " sync lines: " + str(len(timestamps_delta[data_source])) + ", median: " + str(data_source_offset[data_source]) +
                ", min: " + str(min(timestamps_delta[data_source])) + ", max: " + str(max(timestamps_delta[data_source])) +
                ", mean: " + str(statistics.mean(timestamps_delta[data_source])))
    
    # add offset to timestamps
    for line_mod in dict_log:
        for idx in range(len(dict_log[line_mod]["timestamp"])):
            data_source = dict_log[line_mod]["data_source"][idx]
            dict_log[line_mod]["timestamp"][idx] = dict_log[line_mod]["timestamp"][idx] + data_source_offset[data_source]

def DictToList(dict_log):
    list_log = []
    for line_mod in dict_log:
        for idx in range(len(dict_log[line_mod]["timestamp"])):
            if dict_log[line_mod]["valid"][idx]:
                dict_line = dict_log[line_mod].copy()
                dict_line["data_source"] =  dict_log[line_mod]["data_source"][idx]
                dict_line["timestamp"] = dict_log[line_mod]["timestamp"][idx]
                dict_line["valid"] = dict_log[line_mod]["valid"][idx]
                dict_line["eheal"] = dict_log[line_mod]["eheal"][idx]
                dict_line["oheal"] = dict_log[line_mod]["oheal"][idx]
                list_log.append(dict_line)
    print("Sort list by timestamp and remove offset...")
    list_log = sorted(list_log, key=lambda x: x["timestamp"])
    timestamp_0 = list_log[0]["timestamp"]
    for idx in range(len(list_log)):
        list_log[idx]["timestamp"] -= timestamp_0
    return list_log

def SyncDictLogMaster(dict_log, t_delta_max):
    print("Calculating time offsets...")
    SyncTimeOffsets(dict_log)
    print("Detecting duplicates...")
    # set duplicates to invalid
    for idx_p, line_mod in enumerate(dict_log):
        idxs_s = np.array(dict_log[line_mod]["timestamp"]).argsort() # sort by timestamp so loop can be cancelled as soon as t_cmp-t > t_max
        if (idx_p%1000==0) or (idx_p==len(dict_log)-1):
            print("Line", idx_p+1, "/", len(dict_log), end="\r")
        if len(idxs_s)>1: # if more than 1 entry of line_mod was found (otherwise it can be left as valid)
            for idx, idx_s in enumerate(idxs_s):
                data_source = dict_log[line_mod]["data_source"][idx_s]
                timestamp = dict_log[line_mod]["timestamp"][idx_s]
                valid = dict_log[line_mod]["valid"][idx_s]
                if valid:
                    for idx_cmp in idxs_s[idx+1:]:
                        data_source_cmp = dict_log[line_mod]["data_source"][idx_cmp]
                        timestamp_cmp = dict_log[line_mod]["timestamp"][idx_cmp]
                        if timestamp_cmp-timestamp > t_delta_max:
                            break
                        elif data_source != data_source_cmp:
                            if (dict_log[line_mod]["eheal"][idx_cmp] is not None) and (dict_log[line_mod]["eheal"][idx_s] is None): # prioritise entries from Kikilogs (with eheal data))
                                dict_log[line_mod]["valid"][idx_s] = False
                                break
                            else:
                                dict_log[line_mod]["valid"][idx_cmp] = False

    print()
    print("Preparing dict_log...")
    dict_log_df = DictToList(dict_log)
    return dict_log_df