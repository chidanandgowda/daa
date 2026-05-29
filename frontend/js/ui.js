/**
 * UI Controller — Manages sidebar interactions, result display,
 * parameter panels, and the knapsack modal.
 */

const UI = (() => {
    // Cached DOM elements
    const els = {};

    /**
     * Cache all frequently accessed DOM elements.
     */
    function cacheElements() {
        els.algoGrid     = document.getElementById('algo-grid');
        els.paramsTsp    = document.getElementById('params-tsp');
        els.paramsPath   = document.getElementById('params-path');
        els.paramsBlocked = document.getElementById('params-blocked');
        els.paramsTemp   = document.getElementById('params-temp');
        els.paramsKnapsack = document.getElementById('params-knapsack');
        els.resultsContainer = document.getElementById('results-container');
        els.loadingOverlay = document.getElementById('loading-overlay');
        els.btnRun       = document.getElementById('btn-run');
        els.tspStart     = document.getElementById('tsp-start');
        els.pathSource   = document.getElementById('path-source');
        els.pathDest     = document.getElementById('path-dest');
        els.tempPenalty  = document.getElementById('temp-penalty');
        els.knapsackCap  = document.getElementById('knapsack-capacity');
        els.blockedList  = document.getElementById('blocked-edges-list');
        els.clearBlocked = document.getElementById('clear-blocked');
        els.apiStatus    = document.getElementById('api-status');
        els.knapsackModal = document.getElementById('knapsack-modal');
        els.knapsackResults = document.getElementById('knapsack-results');
        els.modalClose   = document.getElementById('modal-close');
        els.infoNodes    = document.getElementById('info-nodes');
        els.infoEdges    = document.getElementById('info-edges');
    }

    /**
     * Populate city dropdowns with node data.
     * @param {Array} nodes - [{id, name}, ...]
     */
    function populateDropdowns(nodes) {
        const options = nodes.map(n =>
            `<option value="${n.id}">${n.name} (${n.id})</option>`
        ).join('');

        els.tspStart.innerHTML = options;
        els.pathSource.innerHTML = options;
        els.pathDest.innerHTML = options;

        // Set different defaults for source/dest
        if (nodes.length >= 3) {
            els.pathDest.value = nodes[2].id;
        }
    }

    /**
     * Show/hide parameter panels based on selected algorithm.
     * @param {string} algo - Algorithm key
     */
    function showParamsFor(algo) {
        // Hide all param groups
        els.paramsTsp.classList.add('hidden');
        els.paramsPath.classList.add('hidden');
        els.paramsBlocked.classList.add('hidden');
        els.paramsTemp.classList.add('hidden');
        els.paramsKnapsack.classList.add('hidden');

        switch (algo) {
            case 'held-karp':
            case 'nearest-neighbour':
                els.paramsTsp.classList.remove('hidden');
                break;
            case 'dijkstra':
                els.paramsPath.classList.remove('hidden');
                els.paramsTemp.classList.remove('hidden');
                break;
            case 'astar':
                els.paramsPath.classList.remove('hidden');
                els.paramsBlocked.classList.remove('hidden');
                break;
            case 'knapsack':
                els.paramsKnapsack.classList.remove('hidden');
                break;
        }
    }

    /**
     * Display algorithm results in the sidebar.
     * @param {Object} response - API response { algorithm, result, execution_time_ms }
     * @param {string} algoKey - Algorithm identifier
     */
    function showResults(response, algoKey) {
        const { algorithm, result, execution_time_ms } = response;
        const color = GraphViz.getColor(algoKey);

        if (algoKey === 'knapsack') {
            showKnapsackResults(response);
            return;
        }

        const hasError = result.error;
        const path = result.path || [];
        const totalCost = result.total_cost || 0;

        let html = `<div class="result-card">`;

        // Header
        html += `
            <div class="result-header">
                <span class="result-algo-name" style="color:${color}">${algorithm}</span>
                <span class="result-time">⏱ ${execution_time_ms.toFixed(2)} ms</span>
            </div>
        `;

        if (hasError) {
            html += `<p style="color: var(--accent-pink); font-size: 0.82rem;">⚠ ${result.error}</p>`;
        }

        // Stats grid
        html += `<div class="result-stats">`;
        html += `
            <div class="stat-item">
                <div class="stat-label">Total Cost</div>
                <div class="stat-value cost">₹${totalCost >= 0 ? totalCost.toLocaleString() : 'N/A'}</div>
            </div>
        `;

        if (result.nodes_explored !== undefined) {
            html += `
                <div class="stat-item">
                    <div class="stat-label">Nodes Explored</div>
                    <div class="stat-value">${result.nodes_explored}</div>
                </div>
            `;
        }

        if (result.dp_states_computed !== undefined) {
            html += `
                <div class="stat-item">
                    <div class="stat-label">DP States</div>
                    <div class="stat-value">${result.dp_states_computed.toLocaleString()}</div>
                </div>
            `;
        }

        html += `
            <div class="stat-item">
                <div class="stat-label">Path Length</div>
                <div class="stat-value">${path.length} stops</div>
            </div>
        `;
        html += `</div>`;

        // Path sequence
        if (path.length > 0) {
            html += `
                <div class="result-path">
                    <div class="result-path-label">Route</div>
                    <div class="path-sequence">
                        ${path.map((node, i) => `
                            <span class="path-node" style="border-color:${color}; color:${color}; background:${color}15">${node}</span>
                            ${i < path.length - 1 ? '<span class="path-arrow">→</span>' : ''}
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Complexity
        if (result.complexity) {
            html += `
                <div class="result-complexity">
                    <div class="complexity-label">Complexity</div>
                    <div class="complexity-value">
                        <strong>Time:</strong> ${result.complexity.time}<br>
                        <strong>Space:</strong> ${result.complexity.space}
                    </div>
                </div>
            `;
        }

        html += `</div>`;
        els.resultsContainer.innerHTML = html;
    }

    /**
     * Show knapsack results in a modal.
     */
    function showKnapsackResults(response) {
        const { result, execution_time_ms } = response;
        const selected = result.selected_items || [];

        let html = `
            <div class="knapsack-summary">
                <div class="knapsack-stat">
                    <div class="stat-label">Total Value</div>
                    <div class="stat-value cost">₹${result.total_value.toLocaleString()}</div>
                </div>
                <div class="knapsack-stat">
                    <div class="stat-label">Total Weight</div>
                    <div class="stat-value">${result.total_weight.toLocaleString()} kg</div>
                </div>
                <div class="knapsack-stat">
                    <div class="stat-label">Utilization</div>
                    <div class="stat-value time">${result.utilization_pct}%</div>
                </div>
            </div>
            <div style="margin-bottom:10px;">
                <span class="result-time">⏱ ${execution_time_ms.toFixed(2)} ms</span>
            </div>
        `;

        if (result.complexity) {
            html += `
                <div class="result-complexity" style="margin-bottom:14px;">
                    <div class="complexity-label">Complexity</div>
                    <div class="complexity-value">
                        <strong>Time:</strong> ${result.complexity.time}<br>
                        <strong>Space:</strong> ${result.complexity.space}
                    </div>
                </div>
            `;
        }

        // Build table of all items, marking selected ones
        html += `
            <table class="knapsack-table">
                <thead>
                    <tr>
                        <th>Cargo Item</th>
                        <th>Weight (kg)</th>
                        <th>Value (₹)</th>
                        <th>Temp</th>
                        <th>Priority</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // We need the original items list — if available from API or global
        const selectedIds = new Set(selected.map(i => i.id));

        selected.forEach(item => {
            html += `
                <tr class="selected">
                    <td>${item.name}</td>
                    <td>${item.weight_kg}</td>
                    <td>₹${item.value.toLocaleString()}</td>
                    <td>${item.temp_req || '-'}</td>
                    <td>${item.priority || '-'}</td>
                </tr>
            `;
        });

        html += `</tbody></table>`;

        els.knapsackResults.innerHTML = html;

        // Also update sidebar results
        els.resultsContainer.innerHTML = `
            <div class="result-card">
                <div class="result-header">
                    <span class="result-algo-name" style="color:var(--color-knapsack)">0/1 Knapsack</span>
                    <span class="result-time">⏱ ${execution_time_ms.toFixed(2)} ms</span>
                </div>
                <div class="result-stats">
                    <div class="stat-item">
                        <div class="stat-label">Value</div>
                        <div class="stat-value cost">₹${result.total_value.toLocaleString()}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Weight</div>
                        <div class="stat-value">${result.total_weight.toLocaleString()} kg</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Items</div>
                        <div class="stat-value">${selected.length}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Utilization</div>
                        <div class="stat-value time">${result.utilization_pct}%</div>
                    </div>
                </div>
            </div>
        `;

        // Show modal
        els.knapsackModal.classList.remove('hidden');
    }

    /**
     * Update the blocked edges display in the sidebar.
     * @param {Array<[string, string]>} edges
     */
    function updateBlockedEdgesUI(edges) {
        if (edges.length === 0) {
            els.blockedList.innerHTML = '<span style="color:var(--text-muted); font-size:0.72rem;">No blocked edges</span>';
            return;
        }
        els.blockedList.innerHTML = edges.map(([s, t]) => `
            <span class="blocked-chip">
                ${s}↔${t}
                <span class="remove-blocked" data-src="${s}" data-tgt="${t}">✕</span>
            </span>
        `).join('');
    }

    /**
     * Show a node's info (triggered by clicking a node on the graph).
     */
    function showNodeInfo(data) {
        // Brief tooltip-style display in the results panel doesn't interfere with results
        console.log(`Node: ${data.name} (${data.id}), Zone: ${data.temp_zone}, Capacity: ${data.capacity}kg`);
    }

    /**
     * Set loading state.
     */
    function setLoading(loading) {
        if (loading) {
            els.loadingOverlay.classList.remove('hidden');
            els.btnRun.classList.add('loading');
            els.btnRun.innerHTML = '<span class="spinner" style="width:18px;height:18px;border-width:2px;"></span> Computing...';
        } else {
            els.loadingOverlay.classList.add('hidden');
            els.btnRun.classList.remove('loading');
            els.btnRun.innerHTML = '<span class="btn-run-icon">▶</span> Run Algorithm';
        }
    }

    /**
     * Show error in results panel.
     */
    function showError(message) {
        els.resultsContainer.innerHTML = `
            <div class="result-card">
                <p style="color: var(--accent-pink); font-size: 0.85rem;">
                    ⚠ <strong>Error:</strong> ${message}
                </p>
            </div>
        `;
    }

    /**
     * Update the API connection status badge.
     */
    function setApiStatus(connected) {
        if (connected) {
            els.apiStatus.textContent = '● API Connected';
            els.apiStatus.className = 'badge badge-green';
        } else {
            els.apiStatus.textContent = '○ API Offline';
            els.apiStatus.className = 'badge badge-red';
        }
    }

    /**
     * Update graph info chips.
     */
    function updateGraphInfo(nodeCount, edgeCount) {
        els.infoNodes.textContent = `${nodeCount} nodes`;
        els.infoEdges.textContent = `${edgeCount} edges`;
    }

    /**
     * Initialize UI event handlers.
     */
    function initEvents() {
        // Modal close
        els.modalClose.addEventListener('click', () => {
            els.knapsackModal.classList.add('hidden');
        });

        els.knapsackModal.addEventListener('click', (e) => {
            if (e.target === els.knapsackModal) {
                els.knapsackModal.classList.add('hidden');
            }
        });

        // Clear blocked edges
        els.clearBlocked.addEventListener('click', () => {
            GraphViz.clearBlockedEdges();
            updateBlockedEdgesUI([]);
        });

        // Blocked edge removal from chips
        els.blockedList.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-blocked')) {
                const src = e.target.dataset.src;
                const tgt = e.target.dataset.tgt;
                // Find and unblock the edge in Cytoscape
                // This is handled via App.updateBlockedEdges
                e.target.parentElement.remove();
            }
        });
    }

    return {
        cacheElements,
        populateDropdowns,
        showParamsFor,
        showResults,
        updateBlockedEdgesUI,
        showNodeInfo,
        setLoading,
        showError,
        setApiStatus,
        updateGraphInfo,
        initEvents,
    };
})();
