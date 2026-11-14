import json, math, os
KIT = os.path.expanduser('~/workspace/makefun/btc-cent-forecast-01-kit/btc-cent-forecast-01-kit/input')

def load(i):
    d = json.load(open(f'{KIT}/p0{i}.in'))
    return d['at'], d['markets'][0]['start'], d['markets'][0]['prices']

# stitch union timeline: p00 covers 11-07 06:01 .. 11-10 06:00; p05 covers 11-08 02:01 .. 11-11 02:00
at0, s0, p0 = load(0)
at5, s5, p5 = load(5)
# verify overlap consistency: p05 price at 11-10 06:00 should equal p00 last
# p05 index of 11-10 06:00: minutes from 11-08 02:01 to 11-10 06:00 = 2*1440+239 = 3119
idx = (2*1440 + 239)
print('overlap check p05[3119] vs p00 last:', p5[idx], p0[-1], 'equal:', p5[idx]==p0[-1])
# build union: p00 full + p05 from index 3120 onward
series = list(p0) + p5[idx+1:]
print('union len', len(series), 'expected', (4*24*60 - 60) + 1 + 20*60)  # Nov7 06:01 .. Nov11 02:00
# minutes: from 2026-11-07T06:01Z, index i -> minute offset i
from datetime import datetime, timedelta, timezone
t0 = datetime(2026,11,7,6,1,tzinfo=timezone.utc)
def ts(i): return t0 + timedelta(minutes=i)
print('first', ts(0), 'last', ts(len(series)-1), series[0], series[-1])

# exact practice actuals p00..p04: target = checkpoint of next case (last price of next case)
actuals = {}
for i in range(5):
    at_next, _, p_next = load(i+1)
    actuals[f'p0{i}'] = p_next[-1]
    print(f'p0{i} checkpoint close {load(i)[2][-1]:.2f} -> actual {p_next[-1]:.2f} move {p_next[-1]-load(i)[2][-1]:+.2f}')

# persistence MAE on p00..p04
errs = [abs(actuals[f'p0{i}'] - load(i)[2][-1])*100 for i in range(5)]
print('persistence MAE cents p00-p04:', sum(errs)/5, 'per case:', [round(e,2) for e in errs])
print('reported practice baseline (6 cases incl p05): 44521.576667 -> implied p05 err:',
      round(44521.576667*6 - sum(errs), 2), 'cents')

# 4h log-return stats on union timeline (hourly checkpoints with full 72h history)
import statistics
rets = []
for ck in range(4320-1, len(series)-240, 60):  # checkpoint index, need 4320 history before it
    r = math.log(series[ck+240]/series[ck])
    rets.append(r)
print(f'\n4h log returns: n={len(rets)} mean={statistics.mean(rets)*100:.4f}% std={statistics.stdev(rets)*100:.4f}%')
# autocorrelation of 1h log returns
lr = [math.log(series[i+60]/series[i]) for i in range(0, len(series)-60, 60)]
def autocorr(x, lag):
    m = statistics.mean(x); n=len(x)
    num = sum((x[i]-m)*(x[i-lag]-m) for i in range(lag,n))
    den = sum((v-m)**2 for v in x)
    return num/den
for lag in (1,2,3,4,6,12,24):
    print(f'1h-return autocorr lag {lag}h: {autocorr(lr,lag):+.3f}')
# 4h return autocorr (non-overlapping)
r4 = [math.log(series[i+240]/series[i]) for i in range(0, len(series)-240, 240)]
for lag in (1,2,3):
    if len(r4) > lag+2: print(f'4h-return autocorr lag {lag}: {autocorr(r4,lag):+.3f}')
