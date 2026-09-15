const API = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* keep status text */
    }
    throw new Error(detail);
  }
  return response.json();
}

export const health = () => request("/health");
export const meta = () => request("/meta");
export const journeys = () => request("/journeys");
export const hubs = () => request("/hubs?limit=8");
export const searchNeurons = (q, limit = 12) =>
  request(`/neurons?q=${encodeURIComponent(q)}&limit=${limit}`);
export const neighbors = (id) => request(`/neurons/${encodeURIComponent(id)}/neighbors`);
export const branch = (neuron_id, limit = 12) =>
  request("/branch", {
    method: "POST",
    body: JSON.stringify({ neuron_id, limit }),
  });

export function findPaths(source, destination, max_paths = 5) {
  return request("/paths/find", {
    method: "POST",
    body: JSON.stringify({ source, destination, max_paths }),
  });
}

export function comparePaths(path_a, path_b) {
  return request("/paths/compare", {
    method: "POST",
    body: JSON.stringify({ path_a, path_b }),
  });
}

export function spec(kind, value) {
  return { kind, value: value.trim() };
}
