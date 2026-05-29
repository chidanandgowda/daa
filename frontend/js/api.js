/**
 * API Client — Cold-Chain Logistics Optimizer
 * Handles all communication with the FastAPI backend.
 */

const API = (() => {
    const BASE_URL = 'http://localhost:8000/api';

    /**
     * Generic fetch wrapper with error handling and timeout.
     */
    async function request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        const config = {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Cannot connect to backend. Is the server running on port 8000?');
            }
            throw error;
        }
    }

    return {
        /**
         * Fetch the complete graph data (nodes + edges).
         */
        async getGraph() {
            return request('/graph');
        },

        /**
         * Fetch available cargo items.
         */
        async getCargoItems() {
            return request('/cargo');
        },

        /**
         * Run Held-Karp exact TSP.
         * @param {string} start - Starting city node ID
         */
        async runHeldKarp(start) {
            return request('/tsp', {
                method: 'POST',
                body: JSON.stringify({ start }),
            });
        },

        /**
         * Run Nearest Neighbour TSP heuristic.
         * @param {string} start - Starting city node ID
         */
        async runNearestNeighbour(start) {
            return request('/nearest-neighbour', {
                method: 'POST',
                body: JSON.stringify({ start }),
            });
        },

        /**
         * Run Dijkstra's shortest path.
         * @param {string} source - Source city
         * @param {string} destination - Target city
         * @param {boolean} tempPenalty - Apply temperature penalty
         */
        async runDijkstra(source, destination, tempPenalty = true) {
            return request('/dijkstra', {
                method: 'POST',
                body: JSON.stringify({
                    source,
                    destination,
                    temp_penalty: tempPenalty,
                }),
            });
        },

        /**
         * Run A* search with optional blocked edges.
         * @param {string} source - Source city
         * @param {string} destination - Target city
         * @param {Array} blockedEdges - [[src, tgt], ...]
         */
        async runAStar(source, destination, blockedEdges = null) {
            return request('/astar', {
                method: 'POST',
                body: JSON.stringify({
                    source,
                    destination,
                    blocked_edges: blockedEdges,
                }),
            });
        },

        /**
         * Run 0/1 Knapsack optimization.
         * @param {number} capacity - Truck capacity in kg
         * @param {Array|null} items - Custom items or null for default
         */
        async runKnapsack(capacity, items = null) {
            const body = { capacity };
            if (items) body.items = items;
            return request('/knapsack', {
                method: 'POST',
                body: JSON.stringify(body),
            });
        },

        /**
         * Check if the API is reachable.
         */
        async healthCheck() {
            try {
                const res = await fetch('http://localhost:8000/', { method: 'GET' });
                return res.ok;
            } catch {
                return false;
            }
        },
    };
})();
