// api/index.js
// VNDirect price proxy for Vercel (robust + debug)
// Supports stocks (HOSE/HNX/UPCoM) and ^VNINDEX via dchart.
// Try multiple sources, accept text/plain JSON, add Referer to bypass filters.

async function getJsonLoose(url, init = {}) {
  const res = await fetch(url, {
    ...init,
    headers: {
      'User-Agent': 'Mozilla/5.0 (VercelProxy)',
      'Accept': 'application/json,text/plain,*/*',
      'Referer': 'https://dchart.vndirect.com.vn/',   // dchart likes a referer
      ...(init.headers || {}),
    },
    redirect: 'follow',
    cache: 'no-store',
  });
  const status = res.status;
  const text = await res.text();
  let json = null;
  try { json = JSON.parse(text); } catch (e) { /* leave as null */ }
  return { status, text, json };
}

function pickPrice(obj, symbol) {
  if (!obj) return null;

  // finfo-api: { data: [ { close, matchPrice, ... } ] }
  if (obj.data && Array.isArray(obj.data) && obj.data.length) {
    const o = obj.data[0];
    const keys = ['matchPrice','close','last','price','lastPrice','currentPrice'];
    for (const k of keys) if (o && o[k] != null && isFinite(o[k])) return Number(o[k]);
  }

  // prices.latest / prices.simple : array or object
  if (Array.isArray(obj) && obj.length) {
    const o = obj[0];
    const keys = ['matchPrice','mp','last','price','lastPrice','currentPrice'];
    for (const k of keys) if (o && o[k] != null && isFinite(o[k])) return Number(o[k]);
    for (const v of Object.values(o)) if (typeof v === 'number' && isFinite(v)) return Number(v);
  }

  // map by symbol
  if (obj[symbol]) {
    const o = obj[symbol];
    const keys = ['matchPrice','mp','close','last','price','lastPrice','currentPrice'];
    for (const k of keys) if (o && o[k] != null && isFinite(o[k])) return Number(o[k]);
  }

  // shallow scan
  for (const k in obj) {
    const v = obj[k];
    if (typeof v === 'number' && isFinite(v)) return Number(v);
    if (v && typeof v === 'object') {
      for (const kk of ['matchPrice','mp','close','last','price','lastPrice','currentPrice'])
        if (v[kk] != null && isFinite(v[kk])) return Number(v[kk]);
    }
  }
  return null;
}

async function fetchDchartClose(symbol) {
  const to = Math.floor(Date.now() / 1000);
  const from = to - 60 * 60 * 24 * 45; // last ~45 days
  const url = `https://dchart-api.vndirect.com.vn/dchart/history?symbol=${encodeURIComponent(symbol)}&resolution=1D&from=${from}&to=${to}`;
  const { status, text, json } = await getJsonLoose(url);
  if (json && json.s && json.s.toLowerCase() === 'ok' && Array.isArray(json.c) && json.c.length) {
    const last = json.c[json.c.length - 1];
    if (isFinite(last)) return { price: Number(last), source: url, raw: { status, body: text.slice(0, 200) } };
  }
  return { price: null, source: url, raw: { status, body: text.slice(0, 200) } };
}

async function fetchVNPrice(symbol) {
  const s = String(symbol).toUpperCase().trim();

  // VNINDEX via dchart
  if (s === '^VNINDEX' || s === 'VNINDEX') {
    return await fetchDchartClose('VNINDEX');
  }

  // try multiple endpoints
  const urls = [
    `https://prices.vndirect.com.vn/prices/latest?symbols=${encodeURIComponent(s)}`,
    `https://prices.vndirect.com.vn/prices/simple?symbols=${encodeURIComponent(s)}`,
    `https://finfo-api.vndirect.com.vn/v4/stock_prices?symbol=${encodeURIComponent(s)}&size=1&sort=tradingDate:desc`,
    `https://finfo-api.vndirect.com.vn/v4/stock_prices?symbol=${encodeURIComponent(s)}&size=1&sort=date:desc`
  ];

  const attempts = [];
  for (const url of urls) {
    try {
      const { status, text, json } = await getJsonLoose(url);
      const price = pickPrice(json, s);
      attempts.push({ url, status, sample: text.slice(0, 200), parsed: !!json, price });
      if (isFinite(price)) return { price: Number(price), source: url, attempts };
    } catch (e) {
      attempts.push({ url, error: String(e) });
    }
  }

  // fallback dchart
  const dc = await fetchDchartClose(s);
  if (isFinite(dc.price)) return { price: dc.price, source: dc.source, attempts };

  return { price: null, source: null, attempts: attempts.concat([dc]) };
}

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(204).send('');

  try {
    const { symbol, debug } = req.query;
    if (!symbol) return res.status(400).json({ error: 'Missing symbol' });

    const result = await fetchVNPrice(symbol);
    if (isFinite(result.price)) {
      res.setHeader('Cache-Control', 'public, s-maxage=30, stale-while-revalidate=60');
      return res.status(200).json({
        symbol: String(symbol).toUpperCase(),
        price: result.price,
        source: result.source,
        ts: Date.now(),
        ...(debug ? { debug: result.attempts } : {})
      });
    }
    return res.status(502).json({
      error: `No price from VNDirect for ${String(symbol).toUpperCase()}`,
      ...(debug ? { debug: result.attempts } : {})
    });
  } catch (e) {
    return res.status(500).json({ error: String(e) });
  }
};
