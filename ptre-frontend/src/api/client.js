const API_URL = import.meta.env.VITE_API_URL || '';

/**
 * Fetches the signal data for a given ticker.
 * @param {string} ticker 
 * @returns {Promise<Object>} The signal data.
 * @throws {Error} If the fetch fails.
 */
export async function fetchSignal(ticker) {
  if (!ticker) return null;
  
  try {
    const response = await fetch(`${API_URL}/api/signal/${ticker}`);
    
    if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch signal:", error);
    throw error;
  }
}
