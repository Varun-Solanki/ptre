const API_BASE = import.meta.env.VITE_API_URL;

export async function fetchSignal(ticker) {
  const res = await fetch(`${API_BASE}/api/signal/${ticker}`);
  if (!res.ok) {
    throw new Error("Failed to fetch signal");
  }
  return res.json();
}

export async function fetchTickers() {
  const res = await fetch(`${API_BASE}/api/tickers`);
  if (!res.ok) {
    throw new Error("Failed to fetch tickers");
  }
  return res.json();
}
