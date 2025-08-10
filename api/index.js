// Vercel Serverless – Proxy giá VNDirect
// Hỗ trợ: cổ phiếu VN (HOSE/HNX/UPCoM). (VNINDEX có thể thêm sau nếu cần)

// Util: fetch JSON an toàn
async function getJson(url, init = {}) {
  const res = await fetch(url, {
    ...init,
    // Một số endpoint cần UA để tránh chặn
    headers: {
      'User-Agent': 'Mozilla/5.0 VercelProxy',
      'Accept': 'application/json',
      ...(init.headers || {}),
    },
    redirect: 'follow',
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} on ${url}`);
  return res.json();
}

// Cố gắng rút giá từ nhiều kiểu JSON khác nhau
function extractPrice(obj) {
  if (!obj) return null;

  // finfo-api: { data: [ { close, matchPrice, ... } ] }
  if (obj.data && Array.isArray(obj.data) && obj.data.length) {
    const o = obj.data[0];
    for (const k of ['close', 'matchPrice', 'last', 'price', 'lastPrice', 'currentPrice'])
      if (o != null && o[k] != null && isFinite(o[k])) return Number(o[k]);
  }

  // prices.simple: [ { symbol, matchPrice/mp/... } ] – nhiều biến thể
  if (Array.isArray(obj) && obj.length) {
    const o = obj[0];
    for (const k of ['matchPrice', 'mp', 'last', 'price', 'lastPrice', 'currentPrice'])
      if (o != null && o[k] != null && isFinite(o[k])) return Number(o[k]);
    // một số trả về object con theo mã
    const vals = Object.values(o).filter(v => typeof v === 'number');
    if (vals.length) return Number(vals[0]);
  }

  // Đối tượng map theo mã
  for (const key in obj) {
    const v = obj[key];
    if (typeof v === 'number' && isFinite(v)) return Number(v);
    if (v && typeof v === 'object') {
      for (const k of ['close', 'matchPrice', 'mp', 'last', 'price', 'lastPrice', 'currentPrice'])
        if (v[k] != null && isFinite(v[k])) return Number(v[k]);
    }
  }
  return null;
}

// Thử lần lượt nhiều endpoint VNDirect (server-side không bị chặn DNS như Apps Script)
async function fetchVnDirectPrice(symbol) {
  const s = symbol.toUpperCase().trim();

  const urls = [
    // finfo – giá gần nhất (đóng cửa/khớp cuối)
    `https://finfo-api.vndirect.com.vn/v4/stock_prices?symbol=${encodeURIComponent(s)}&size=1&sort=tradingDate:desc`,
    `https://finfo-api.vndirect.com.vn/v4/stock_prices?symbols=${encodeURIComponent(s)}&size=1`,
    // prices – luồng realtime/đơn giản
    `https://prices.vndirect.com.vn/prices/simple?symbols=${encodeURIComponent(s)}`
  ];

  for (const url of urls) {
    try {
      const json = await getJson(url);
      const price = extractPrice(json);
      if (isFinite(price)) return { price, source: url };
    } catch (e) {
      // thử URL kế tiếp
    }
  }
  throw new Error('No price from VNDirect for ' + s);
}

// CORS helper
function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*'); // có thể thay bằng docs.google.com nếu muốn siết
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') {
    return res.status(204).send('');
  }

  try {
    const { symbol } = req.query;
    if (!symbol) return res.status(400).json({ error: 'Missing symbol' });

    const { price, source } = await fetchVnDirectPrice(symbol);

    // Cache 30s trên edge để giảm số request
    res.setHeader('Cache-Control', 'public, s-maxage=30, stale-while-revalidate=60');

    return res.status(200).json({
      symbol: String(symbol).toUpperCase(),
      price,
      source,
      ts: Date.now()
    });
  } catch (e) {
    return res.status(502).json({ error: e.message || String(e) });
  }
};
