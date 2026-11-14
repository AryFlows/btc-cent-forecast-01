import json, math, os, statistics
KIT = os.path.expanduser('~/workspace/makefun/btc-cent-forecast-01-kit/btc-cent-forecast-01-kit/input')
def load(i):
    d = json.load(open(f'{KIT}/p0{i}.in'))
    return d['markets'][0]['prices']
p = [load(i) for i in range(6)]
series = list(p[0]) + p[5][3120:]
N = len(series)
CKS = list(range(4319, N-240, 30))
h1, h2 = CKS[:16], CKS[16:]

def slope_lp(lp, w):
    y = lp[-w:]; n=len(y); mx=(n-1)/2; my=sum(y)/n
    sxx=sum((i-mx)**2 for i in range(n)); sxy=sum((i-mx)*(y[i]-my) for i in range(n))
    return sxy/sxx

def wslope_lp(lp, w, half_life):
    """Exponentially time-weighted OLS slope over the last w closes.
    Weight of the oldest point = 0.5 ** (w / half_life). Recent minutes
    count more, which adapts faster to a regime change while still using
    the long window's data."""
    y = lp[-w:]; n=len(y)
    decay = 0.5 ** (1.0 / half_life)
    ws = [decay ** (n - 1 - i) for i in range(n)]
    sw = sum(ws)
    mx = sum(w * i for w, i in zip(ws, range(n))) / sw
    my = sum(w * v for w, v in zip(ws, y)) / sw
    sxx = sum(w * (i - mx) ** 2 for w, i in zip(ws, range(n)))
    sxy = sum(w * (i - mx) * (v - my) for w, i, v in zip(ws, range(n), y))
    return sxy / sxx if sxx else 0

def forecast(hist, kind):
    P = hist[-1]; lp = [math.log(x) for x in hist]
    if kind == 'persist': return P
    if kind.startswith('trend:'):
        w,d = kind.split(':')[1].split(','); w=int(w); d=float(d)
        return P*math.exp(slope_lp(lp,w)*240*d)
    if kind.startswith('blend48_24:'):
        d = float(kind.split(':')[1])
        s = (slope_lp(lp,2880)+slope_lp(lp,1440))/2
        return P*math.exp(s*240*d)
    if kind.startswith('blend48_72:'):
        d = float(kind.split(':')[1])
        s = (slope_lp(lp,2880)+slope_lp(lp,4320))/2
        return P*math.exp(s*240*d)
    if kind.startswith('blend48_60:'):
        d = float(kind.split(':')[1])
        s = (slope_lp(lp,2880)+slope_lp(lp,3600))/2
        return P*math.exp(s*240*d)
    if kind.startswith('wslope:'):
        w,hl,d = kind.split(':')[1].split(','); w=int(w); hl=float(hl); d=float(d)
        return P*math.exp(wslope_lp(lp,w,hl)*240*d)
    if kind.startswith('trendfade48:'):
        d,a = kind.split(':')[1].split(','); d=float(d); a=float(a)
        return P*math.exp(slope_lp(lp,2880)*240*d - a*(lp[-1]-lp[-241]))
    if kind.startswith('anchor:'):
        # Anchor the forecast on the OLS fitted value at the last minute
        # instead of the noisy last close: guess = exp(yhat_last + slope*240*d).
        w,d = kind.split(':')[1].split(','); w=int(w); d=float(d)
        y = lp[-w:]; n=len(y); mx=(n-1)/2; my=sum(y)/n
        sxx=sum((i-mx)**2 for i in range(n)); sxy=sum((i-mx)*(y[i]-my) for i in range(n))
        slope = sxy/sxx
        yhat_last = my + slope*((n-1)-mx)
        return math.exp(yhat_last + slope*240*d)
    raise ValueError(kind)

def mae(c, cks):
    return statistics.mean(abs(forecast(series[ck-4319:ck+1], c)-series[ck+240])*100 for ck in cks)
def mae_off(c):
    return statistics.mean(abs(forecast(p[i], c)-p[i+1][-1])*100 for i in range(5))
def per_case(c):
    return [round(abs(forecast(p[i], c)-p[i+1][-1])*100, 1) for i in range(5)]

cands = ['persist',
 'trend:2880,1.0',
 'trend:2880,1.05',
 'trend:2880,1.1',
 'blend48_24:1.0',
 'blend48_24:0.9',
 'blend48_72:1.05',
 'blend48_60:1.0',
 'wslope:4320,1440,1.0',
 'wslope:4320,720,1.0',
 'wslope:2880,1440,1.0',
 'trendfade48:1.0,0.05',
 'trendfade48:1.0,0.1',
 'trendfade48:1.0,0.025',
 'anchor:2880,1.0',
 'anchor:2880,1.05']
print(f'{"model":22s} {"all33":>9s} {"1st16":>9s} {"2nd17":>9s} {"off5":>9s}  per-case off5')
for c in cands:
    print(f'{c:22s} {mae(c,CKS):9.1f} {mae(c,h1):9.1f} {mae(c,h2):9.1f} {mae_off(c):9.1f}  {per_case(c)}')
