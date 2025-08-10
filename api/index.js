// Minimal VNDirect proxy via dchart (daily close) + debug
function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}
async function getJson(url) {
  const r = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (VercelProxy)',
      'Accept': 'application/json,text/plain,*/*',
      'Referer': 'https://dchart.vndirect.com.vn/'
    },
    redirect: 'follow',
    cache: 'no-store'
  });
  const text = await r.text();
  let json = null; try { json = JSON.parse(text); } catch (e) {}
  return { status: r.status, text, json };
}
module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(204).send('');
  try {
    const { symbol, debug } = req.query;
    if (!symbol) return res.status(400).json({ error: 'Missing symbol' });

    const s = String(symbol).toUpperCase().trim();
    const sym = (s === 'VNINDEX' || s === '^VNINDEX') ? 'VNINDEX' : s;

    const to = Math.floor(Date.now() / 1000);
    const from = to - 60 * 60 * 24 * 45; // ~45 ngày
    const url = `https://dchart-api.vndirect.com.vn/dchart/history?symbol=${encodeURIComponent(sym)}&resolution=1D&from=${from}&to=${to}`;

    const { status, text, json } = await getJson(url);
    if (json && json.s && json.s.toLowerCase() === 'ok' && Array.isArray(json.c) && json.c.length) {
      const price = Number(json.c[json.c.length - 1]);
      res.setHeader('Cache-Control', 'public, s-maxage=30, stale-while-revalidate=60');
      return res.status(200).json({
        symbol: s,
        price,
        source: 'dchart',
        ts: Date.now(),
        ...(debug ? { debug: { status, sample: text.slice(0, 200) } } : {})
      });
    }
    return res.status(502).json({
      error: `No price from dchart for ${s}`,
      ...(debug ? { debug: { status, sample: text.slice(0, 200) } } : {})
    });
  } catch (e) {
    return res.status(500).json({ error: String(e) });
  }
};
