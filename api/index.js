export default async function handler(req, res) {
  const symbol = req.query.symbol;
  if (!symbol) return res.status(400).json({ error: "Missing symbol" });
  const apiUrl = `https://finfo-api.vndirect.com.vn/v4/stock_prices?...&symbol=${symbol.toUpperCase()}`;
  const r = await fetch(apiUrl);
  const j = await r.json();
  const price = parseFloat(j.data[0].close);
  res.status(200).json({ symbol, price });
}
