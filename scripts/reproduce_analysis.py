#!/usr/bin/env python3
"""Reproduce profile summaries and threshold-classification tables from CSV."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
from collections import Counter
from statistics import mean, stdev

PROFILES=['LLL','LLH','LHL','LHH','HLL','HLH','HHL','HHH']
TRAITS=['Extraversion','Neuroticism','Openness']
THRESHOLDS={'Extraversion':3.33,'Neuroticism':2.75,'Openness':2.83}

def read_rows(path):
    with path.open(newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def write_rows(path, headers, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(headers); w.writerows(rows)
def metrics(tp,fp,fn,tn):
    p=tp/(tp+fp) if tp+fp else 0.0
    r=tp/(tp+fn) if tp+fn else 0.0
    f=2*p*r/(p+r) if p+r else 0.0
    a=(tp+tn)/(tp+fp+fn+tn)
    return p,r,f,a

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,default=Path('data/personality_assessment/trait_scores_long.csv'))
    ap.add_argument('--output-dir',type=Path,default=Path('derived'))
    args=ap.parse_args()
    rows=read_rows(args.input)
    if len(rows)!=80: raise SystemExit(f'Expected 80 profile-administration rows; found {len(rows)}')
    observed=[]
    for r in rows:
        prof=r['profile']
        vals={t:float(r[t]) for t in TRAITS}
        pred=''.join('H' if vals[t]>=THRESHOLDS[t] else 'L' for t in TRAITS)
        observed.append((prof,int(r['administration']),vals,pred))
    summary=[]
    for prof in PROFILES:
        subset=[x for x in observed if x[0]==prof]
        for t in TRAITS:
            vs=[x[2][t] for x in subset]
            summary.append((prof,t,mean(vs),stdev(vs)))
    write_rows(args.output_dir/'profile_trait_summary.csv',['profile','trait','mean','sample_sd'],summary)
    matrix=Counter((true,pred) for true,_,_,pred in observed)
    write_rows(args.output_dir/'confusion_matrix.csv',['true_profile']+PROFILES,[(p,*[matrix[(p,q)] for q in PROFILES]) for p in PROFILES])
    correct=sum(1 for true,_,_,pred in observed if true==pred)
    overall=correct/len(observed)
    cls=[]
    for p in PROFILES:
        tp=matrix[(p,p)]; fp=sum(matrix[(q,p)] for q in PROFILES if q!=p); fn=sum(matrix[(p,q)] for q in PROFILES if q!=p)
        precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0; f1=2*precision*recall/(precision+recall) if precision+recall else 0
        cls.append((p,precision,recall,f1,sum(matrix[(p,q)] for q in PROFILES)))
    write_rows(args.output_dir/'profile_metrics.csv',['profile','precision','recall','f1','n'],cls)
    tri=[]
    for j,t in enumerate(TRAITS):
        tp=fp=fn=tn=0
        for true,_,vals,pred in observed:
            actual=true[j]=='H'; guess=vals[t]>=THRESHOLDS[t]
            if actual and guess: tp+=1
            elif not actual and guess: fp+=1
            elif actual and not guess: fn+=1
            else: tn+=1
        p,r,f,a=metrics(tp,fp,fn,tn)
        tri.append((t,THRESHOLDS[t],tp,fp,fn,tn,p,r,f,a))
    write_rows(args.output_dir/'trait_metrics.csv',['trait','threshold','tp','fp','fn','tn','precision','recall','f1','accuracy'],tri)
    write_rows(args.output_dir/'individual_predictions.csv',['true_profile','administration','Extraversion','Neuroticism','Openness','predicted_profile'],[(tr,ad,vs['Extraversion'],vs['Neuroticism'],vs['Openness'],pr) for tr,ad,vs,pr in observed])
    print(f'Overall profile accuracy: {overall:.4%} ({correct}/{len(observed)})')
    print(f'Outputs written to: {args.output_dir.resolve()}')
if __name__=='__main__': main()
