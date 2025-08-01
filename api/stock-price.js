export default async function handler(req, res) {
  const symbol = req.query.symbol;
  if (!symbol) {
    return res.status(400).json({ error: "Missing symbol" });
  }

  const url = `https://api.vdsc.com.vn/stock/${symbol}`;
  try {
    const response = await fetch(url);
    const data = await response.json();
    res.status(200).json({ price: data.matchPrice });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch price" });
  }
}
