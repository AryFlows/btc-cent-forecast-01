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

def ema_last(prices, span):
    k = 2/(span+1); e = prices[0]
    for x in prices[1:]: e = e + k*(x-e)
    return e

def forecast(hist, kind):
    P = hist[-1]; lp = [math.log(x) for x in hist]
    if kind == 'persist': return P
    if kind.startswith('trend:'):
        w,d = kind.split(':')[1].split(','); w=int(w); d=float(d)
        return P*math.exp(slope_lp(lp,w)*240*d)
    if kind.startswith('trendfade:'):
        # trend over w with damping d, plus fade of last 4h return with coef a
        w,d,a = kind.split(':')[1].split(','); w=int(w); d=float(d); a=float(a)
        return P*math.exp(slope_lp(lp,w)*240*d - a*(lp[-1]-lp[-241]))
    if kind.startswith('ret:'):
        # simple return over last w minutes, damped: forecast = P*exp(d * r_w * 240/w)
        w,d = kind.split(':')[1].split(','); w=int(w); d=float(d)
        return P*math.exp(d*(lp[-1]-lp[max(0,len(lp)-1-w)])*240/w)
    if kind.startswith('emamom:'):
        # EMA fast-slow momentum: log(EMA60/EMA1440) * d
        d = float(kind.split(':')[1])
        ef = ema_last(hist[-180:],60); es = ema_last(hist[-4320:],1440)
        return P*math.exp(d*(math.log(ef)-math.log(es)))
    raise ValueError(kind)

def mae(c, cks):
    return statistics.mean(abs(forecast(series[ck-4319:ck+1], c)-series[ck+240])*100 for ck in cks)
def mae_off(c):
    return statistics.mean(abs(forecast(p[i], c)-p[i+1][-1])*100 for i in range(5))

cands = ['persist',
 'trend:720,0.5','trend:720,1.0','trend:1440,0.5','trend:1440,1.0','trend:2880,0.5','trend:2880,1.0',
 'trend:4320,0.25','trend:4320,0.5','trend:4320,0.75','trend:4320,1.0',
 'ret:720,0.25','ret:1440,0.25','ret:1440,0.5','ret:2880,0.25','ret:4320,0.25',
 'trendfade:4320,0.5,0.1','trendfade:4320,0.5,0.15','trendfade:1440,0.5,0.1','trendfade:4320,0.75,0.1',
 'emamom:0.5','emamom:1.0','emamom:2.0']
print(f'{"model":26s} {"all33":>9s} {"1st16":>9s} {"2nd17":>9s} {"off5":>9s}')
for c in cands:
    print(f'{c:26s} {mae(c,CKS):9.1f} {mae(c,h1):9.1f} {mae(c,h2):9.1f} {mae_off(c):9.1f}')

print('\nrefinements:')
def forecast2(hist, kind):
    P = hist[-1]; lp = [math.log(x) for x in hist]
    if kind.startswith('blend2880_4320:'):
        d = float(kind.split(':')[1])
        s = (slope_lp(lp,2880)+slope_lp(lp,4320))/2
        return P*math.exp(s*240*d)
    if kind.startswith('trend:'):
        w,d = kind.split(':')[1].split(','); w=int(w); d=float(d)
        return P*math.exp(slope_lp(lp,w)*240*d)
    raise ValueError(kind)
def mae2(c, cks):
    return statistics.mean(abs(forecast2(series[ck-4319:ck+1], c)-series[ck+240])*100 for ck in cks)
def mae_off2(c):
    return statistics.mean(abs(forecast2(p[i], c)-p[i+1][-1])*100 for i in range(5))
for c in ['blend2880_4320:1.0','blend2880_4320:0.9','trend:3600,1.0','trend:2880,0.9','trend:4320,0.9','trend:2880,1.1']:
    print(f'{c:26s} {mae2(c,CKS):9.1f} {mae2(c,h1):9.1f} {mae2(c,h2):9.1f} {mae_off2(c):9.1f}')
