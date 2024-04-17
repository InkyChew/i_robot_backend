import json
import pandas as pd

def get_rank():
    try:
        rank = pd.read_csv('Rank/Rank.csv')
        tmp = []
        for i in range(len(rank)):
            tmp.append((rank['name'].iloc[i], round(rank['profit'].iloc[i], 3)))

        tmp = sorted(tmp, key=lambda x:x[1], reverse=True)
        rank_json = []
        for i in range(len(tmp)):
            rank_json.append({'name':tmp[i][0],
                            'rate':tmp[i][1]})
        # convert into JSON:
        print(json.dumps(rank_json))
        return json.dumps(rank_json)
    except Exception:
        return "{}"
