// api/index.js
// Robust VNDirect price proxy for Google Sheets / Apps Script
// Supports stocks (HOSE/HNX/UPCoM) and VNINDEX

async function getJson(url, init = {}) {
  const res = await fetch(url, {
    ...init,
    headers: {
      'User-Agent': 'Mozilla/5.0 VercelProxy',
      'Accept': 'application/json',
      ...(init.headers || {}),
    },
    redirect: 'follow',
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} on ${url}`);
  const ct = res.headers.get('content-type') || '';
  if (!ct.includes('json')) {
    const text = await res.text();
    throw new Error(`Non-JSON from ${url}: ${text.slice(0, 120)}`);
  }
  return res.json();
}

// Try to pull a numeric price out of many JSON shapes
function extractPrice(obj, symbol) {
  if (!obj) return null;

  // finfo-api: { data: [ { close, matchPrice, ... } ] }
  if (obj.data && Array.isArray(obj.data) && obj.data.length) {
    const o = obj.data[0];
    for (const k of ['matchPrice', 'close', 'last', 'price', 'lastPrice', 'currentPrice'])
      if (o && o[k] != null && isFinite(o[k])) return Number(o[k]);
  }

  // prices.latest or prices.simple may return array or map
  if (Array.isArray(obj) && obj.length) {
    const o = obj[0];
    for (const k of ['matchPrice', 'mp', 'last', 'price', 'lastPrice', 'currentPrice'])
      if (o && o[k] != null && isFinite(o[k])) return Number(o[k]);
    // Sometimes nested map per symbol
    for (const v of Object.values(o)) if (typeof v === 'number' && isFinite(v)) return v;
  }

  // Object keyed by symbol
  if (obj[symbol]) {
    const o = obj[symbol];
    for (const k of ['matchPrice', 'mp', 'close', 'last', 'price', 'lastPrice', 'currentPrice'])
      if (o && o[k] != null && isFinite(o[k])) return Number(o[k]);
  }

  // Shallow scan as a last resort
  for (const k in obj) {
    const v = obj[k];
    if (typeof v === 'number' && isFinite(v)) return v;
    if (v && typeof v === 'object') {
      for (const kk of ['matchPrice', 'mp', 'close', 'last', 'price', 'lastPrice', 'currentPrice'])
        if (v[kk] != null && isFinite(v[kk])) return Number(v[kk]);
    }
  }
  return null;
}

// dchart API (very reliable daily OHLC)
async function fetchDchartClose(symbolForDchart) {
  const to = Math.floor(Date.now() / 1000);
  const from = to - 60 * 60 * 24 * 40; // last ~40 days
  const url = `https://dchart-api.vndirect.com.vn/dchart/history?symbol=${encodeURIComponent(symbolForDchart)}&resolution=1D&from=${from}&to=${to}`;
  const j = await getJson(url);
  // { s: 'ok', t:[...], c:[...], ... }
  if (j && j.s && j.s.toLowerCase() === 'ok' && Array.isArray(j.c) && j.c.length) {
    const last = j.c[j.c.length - 1];
    if (isFinite(last)) return Number(last);
  }
  return null;
}

async function fetchVnDirectPrice(rawSymbol) {
  const s = String(rawSymbol).toUpperCase().trim();

  // VNINDEX handled via dchart directly
  if (s === '^VNINDEX' || s === 'VNINDEX') {
    const px = await fetchDchartClose('VNINDEX');
    if (isFinite(px)) return { price: px, source: 'dchart' };
    throw new Error('No price for VNINDEX');
  }

  const urls = [
    // “live-ish”
    `https://prices.vndirect.com.vn/prices/latest?symbols=${encodeURIComponent(s)}`,
    `https://prices.vndirect.com.vn/prices/simple?symbols=${encodeURIComponent(s)}`,
    // daily finfo
    `https://finfo-api.vndirect.com.vn/v4/stock_prices?symbol=${encodeURIComponent(s)}&size=1&sort=tradingDate:desc`,
    `https://finfo-api.vndirect.com.vn/v4/stock_prices?symbol=${encodeURIComponent(s)}&size=1&sort=date:desc`
  ];

  for (const url of urls) {
    try {
      const j = await getJson(url);
      const price = extractPrice(j, s);
      if (isFinite(price)) return { price, source: url };
    } catch (e) {
      // try next
    }
  }

  // Fallback: dchart daily close
  const px = await fetchDchartClose(s);
  if (isFinite(px)) return { price: px, source: 'dchart' };

  throw new Error(`No price from VNDirect for ${s}`);
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
    const { symbol } = req.query;
    if (!symbol) return res.status(400).json({ error: 'Missing symbol' });

    const { price, source } = await fetchVnDirectPrice(symbol);

    res.setHeader('Cache-Control', 'public, s-maxage=30, stale-while-revalidate=60');
    return res.status(200).json({ symbol: String(symbol).toUpperCase(), price, source, ts: Date.now() });
  } catch (e) {
    return res.status(502).json({ error: e.message || String(e) });
  }
};
