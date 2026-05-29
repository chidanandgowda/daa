/**
 * App Controller — Cold-Chain Logistics Optimizer
 * Main application logic: initialization, algorithm execution,
 * and event orchestration between API, Graph, and UI modules.
 */

const App = (() => {
    let currentAlgo = 'held-karp';

    /**
     * Initialize the application.
     */
    async function init() {
        // 1. Cache DOM elements & set up UI events
        UI.cacheElements();
        UI.initEvents();

        // 2. Check API connectivity
        const apiOk = await API.healthCheck();
        UI.setApiStatus(apiOk);

        if (!apiOk) {
            UI.showError('Backend server is not running. Start it with: <code>uvicorn app.main:app --reload</code> in the backend/ directory.');
            return;
        }

        // 3. Load graph data
        try {
            const graphData = await API.getGraph();
            GraphViz.init(graphData);
            UI.updateGraphInfo(graphData.node_count, graphData.edge_count);

            // Populate dropdowns
            const nodes = GraphViz.getNodeIds();
            UI.populateDropdowns(nodes);
        } catch (err) {
            UI.showError(`Failed to load graph: ${err.message}`);
            return;
        }

        // 4. Set up algorithm selection
        setupAlgoSelection();

        // 5. Set up Run button
        document.getElementById('btn-run').addEventListener('click', runAlgorithm);

        // 6. Set up toolbar buttons
        document.getElementById('btn-fit').addEventListener('click', () => GraphViz.fit());
        document.getElementById('btn-reset').addEventListener('click', () => {
            GraphViz.reset();
            UI.updateBlockedEdgesUI([]);
        });

        // 7. Show default params
        UI.showParamsFor(currentAlgo);

        console.log('🧊 Cold-Chain Logistics Optimizer initialized successfully');
    }

    /**
     * Set up algorithm selector button events.
     */
    function setupAlgoSelection() {
        const buttons = document.querySelectorAll('.algo-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                currentAlgo = btn.dataset.algo;
                UI.showParamsFor(currentAlgo);

                // Clear highlights when switching algorithms
                GraphViz.clearHighlights();
            });
        });
    }

    /**
     * Execute the currently selected algorithm.
     */
    async function runAlgorithm() {
        UI.setLoading(true);
        GraphViz.clearHighlights();

        try {
            let response;

            switch (currentAlgo) {
                case 'held-karp': {
                    const start = document.getElementById('tsp-start').value;
                    response = await API.runHeldKarp(start);
                    break;
                }
                case 'nearest-neighbour': {
                    const start = document.getElementById('tsp-start').value;
                    response = await API.runNearestNeighbour(start);
                    break;
                }
                case 'dijkstra': {
                    const source = document.getElementById('path-source').value;
                    const dest = document.getElementById('path-dest').value;
                    const tempPenalty = document.getElementById('temp-penalty').checked;

                    if (source === dest) {
                        UI.showError('Source and destination must be different.');
                        UI.setLoading(false);
                        return;
                    }

                    response = await API.runDijkstra(source, dest, tempPenalty);
                    break;
                }
                case 'astar': {
                    const source = document.getElementById('path-source').value;
                    const dest = document.getElementById('path-dest').value;
                    const blocked = GraphViz.getBlockedEdges();

                    if (source === dest) {
                        UI.showError('Source and destination must be different.');
                        UI.setLoading(false);
                        return;
                    }

                    response = await API.runAStar(source, dest, blocked.length > 0 ? blocked : null);
                    break;
                }
                case 'knapsack': {
                    const capacity = parseFloat(document.getElementById('knapsack-capacity').value);
                    if (isNaN(capacity) || capacity <= 0) {
                        UI.showError('Please enter a valid capacity > 0.');
                        UI.setLoading(false);
                        return;
                    }
                    response = await API.runKnapsack(capacity);
                    break;
                }
                default:
                    UI.showError(`Unknown algorithm: ${currentAlgo}`);
                    UI.setLoading(false);
                    return;
            }

            // Display results
            UI.showResults(response, currentAlgo);

            // Highlight path on graph (if applicable)
            if (response.result && response.result.path && response.result.path.length > 0) {
                GraphViz.highlightPath(response.result.path, currentAlgo);
            }

        } catch (err) {
            UI.showError(err.message);
        } finally {
            UI.setLoading(false);
        }
    }

    /**
     * Get the currently selected algorithm key.
     */
    function getCurrentAlgo() {
        return currentAlgo;
    }

    /**
     * Update blocked edges in the UI after toggling on the graph.
     */
    function updateBlockedEdges() {
        const blocked = GraphViz.getBlockedEdges();
        UI.updateBlockedEdgesUI(blocked);
    }

    return {
        init,
        getCurrentAlgo,
        updateBlockedEdges,
    };
})();

// ── Bootstrap ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', App.init);
