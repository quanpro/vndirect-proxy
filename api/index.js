export default async function handler(req, res) {
  const symbol = req.query.symbol?.toUpperCase();
  if (!symbol) return res.status(400).json({ error: "No symbol provided" });

  try {
    const apiUrl = `https://finfo-api.vndirect.com.vn/v4/stock_prices?sort=date:desc&size=1&page=1&symbol=${symbol}`;
    const response = await fetch(apiUrl);
    const data = await response.json();

    if (!data.data || !data.data[0]) return res.status(404).json({ error: "No data found" });

    const price = parseFloat(data.data[0].close);
    res.setHeader('Cache-Control', 'no-store');
    res.status(200).json({ symbol, price });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
