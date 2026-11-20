#!/usr/bin/env python3
"""Score a 120-item IPIP-NEO questionnaire using the study's Maples-adapted key.

Input responses are in questionnaire order, one-based item IDs 1..120, with
integer Likert responses 1..5. Reverse-keyed items are recoded as 6 - response.
The function returns the mean of the 24 keyed items for each Big Five domain.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

FACETS = {
    "Neuroticism": {
        "N1 Anxiety": [1,31,61,91], "N2 Anger": [6,36,66,96],
        "N3 Depression": [11,41,71,101], "N4 Self-consciousness": [16,46,76,106],
        "N5 Immoderation": [21,51,81,111], "N6 Vulnerability": [26,56,86,116],
    },
    "Extraversion": {
        "E1 Friendliness": [2,32,62,92], "E2 Gregariousness": [7,37,67,97],
        "E3 Assertiveness": [12,42,72,102], "E4 Activity level": [17,47,77,107],
        "E5 Excitement seeking": [22,52,82,112], "E6 Cheerfulness": [27,57,87,117],
    },
    "Openness": {
        "O1 Imagination": [3,33,63,93], "O2 Artistic interests": [8,38,68,98],
        "O3 Emotionality": [13,43,73,103], "O4 Adventurousness": [18,48,78,108],
        "O5 Intellect": [23,53,83,113], "O6 Liberalism": [28,58,88,118],
    },
    "Agreeableness": {
        "A1 Trust": [4,34,64,94], "A2 Morality": [9,39,69,99],
        "A3 Altruism": [14,44,74,104], "A4 Cooperation": [19,49,79,109],
        "A5 Modesty": [24,54,84,114], "A6 Sympathy": [29,59,89,119],
    },
    "Conscientiousness": {
        "C1 Self-efficacy": [5,35,65,95], "C2 Orderliness": [10,40,70,100],
        "C3 Dutifulness": [15,45,75,105], "C4 Achievement striving": [20,50,80,110],
        "C5 Self-discipline": [25,55,85,115], "C6 Cautiousness": [30,60,90,120],
    },
}
REVERSE = {
    "Neuroticism": {56,76,81,86,96,106,111,116},
    "Extraversion": {67,97,102},
    "Openness": {18,23,38,43,48,53,58,68,73,78,83,88,98,103,108,113,118},
    "Agreeableness": {9,19,24,34,39,49,54,64,69,79,84,94,99,104,109,114,119},
    "Conscientiousness": {30,40,45,55,60,70,75,85,90,100,105,110,115,120},
}

def score_responses(responses: list[int]) -> dict[str, float]:
    if len(responses) != 120:
        raise ValueError(f"Expected 120 responses; received {len(responses)}")
    vals=[]
    for i, raw in enumerate(responses, start=1):
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or int(raw) != raw or not 1 <= int(raw) <= 5:
            raise ValueError(f"Item {i}: response must be an integer from 1 to 5; got {raw!r}")
        vals.append(int(raw))
    out={}
    for domain, facets in FACETS.items():
        item_ids=[item for ids in facets.values() for item in ids]
        if len(item_ids) != 24 or len(set(item_ids)) != 24:
            raise RuntimeError(f"Invalid item map for {domain}")
        keyed=[]
        for item in item_ids:
            v=vals[item-1]
            keyed.append(6-v if item in REVERSE[domain] else v)
        out[domain]=sum(keyed)/24
    return out

def score_facets(responses: list[int]) -> dict[str, dict[str, float]]:
    domains=score_responses(responses)
    vals=[int(x) for x in responses]
    result={}
    for domain, facets in FACETS.items():
        result[domain]={}
        for facet, items in facets.items():
            keyed=[6-vals[i-1] if i in REVERSE[domain] else vals[i-1] for i in items]
            result[domain][facet]=sum(keyed)/4
    return result

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input_json',type=Path,help='JSON file containing {"responses": [120 integers]}')
    ap.add_argument('--output',type=Path,default=None)
    args=ap.parse_args()
    payload=json.loads(args.input_json.read_text(encoding='utf-8'))
    result={"domain_mean_scores":score_responses(payload["responses"]),"facet_mean_scores":score_facets(payload["responses"])}
    out=json.dumps(result,indent=2)
    if args.output: args.output.write_text(out,encoding='utf-8')
    else: print(out)
