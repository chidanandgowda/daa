/**
 * API Client — Cold-Chain Logistics Optimizer
 */

const API = (() => {
    const BASE_URL = 'http://localhost:8000/api';

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
                throw new Error(errData.detail || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Cannot connect to backend. Start it with: uvicorn app.main:app --reload');
            }
            throw error;
        }
    }

    return {
        getGraph()              { return request('/graph'); },
        generateGraph(numCities) { return request('/graph/generate', { method: 'POST', body: JSON.stringify({ num_cities: numCities }) }); },
        getCargoItems()         { return request('/cargo'); },

        /** Run the full optimization pipeline */
        runPipeline(params) {
            return request('/optimize', {
                method: 'POST',
                body: JSON.stringify(params),
            });
        },

        /** Individual endpoints for standalone use */
        runHeldKarp(start) {
            return request('/tsp', { method: 'POST', body: JSON.stringify({ start }) });
        },
        runNearestNeighbour(start) {
            return request('/nearest-neighbour', { method: 'POST', body: JSON.stringify({ start }) });
        },
        runDijkstra(source, destination, tempPenalty = true) {
            return request('/dijkstra', { method: 'POST', body: JSON.stringify({ source, destination, temp_penalty: tempPenalty }) });
        },
        runAStar(source, destination, blockedEdges = null) {
            return request('/astar', { method: 'POST', body: JSON.stringify({ source, destination, blocked_edges: blockedEdges }) });
        },
        runKnapsack(capacity, items = null) {
            const body = { capacity };
            if (items) body.items = items;
            return request('/knapsack', { method: 'POST', body: JSON.stringify(body) });
        },

        async healthCheck() {
            try {
                const res = await fetch('http://localhost:8000/', { method: 'GET' });
                return res.ok;
            } catch { return false; }
        },
    };
})();
