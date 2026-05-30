/**
 * App Controller — Pipeline-based Cold-Chain Optimizer
 * Runs all algorithms as a unified pipeline:
 *   Knapsack → TSP → Dijkstra → A*
 */

const App = (() => {

    async function init() {
        UI.cacheElements();
        UI.initEvents();

        // Check API
        var apiOk = await API.healthCheck();
        UI.setApiStatus(apiOk);

        if (!apiOk) {
            UI.showError('Backend server is not running. Start it with: <code>uvicorn app.main:app --reload</code> in the backend/ directory.');
            return;
        }

        // Load graph
        try {
            var graphData = await API.getGraph();
            GraphViz.init(graphData);
            UI.updateGraphInfo(graphData.node_count, graphData.edge_count);
            UI.populateDropdowns(GraphViz.getNodeIds());
        } catch (err) {
            UI.showError('Failed to load graph: ' + err.message);
            return;
        }

        // Run button
        document.getElementById('btn-run').addEventListener('click', runPipeline);

        // Toolbar
        document.getElementById('btn-fit').addEventListener('click', function() { GraphViz.fit(); });
        document.getElementById('btn-reset').addEventListener('click', function() {
            GraphViz.reset();
            UI.updateBlockedEdgesUI([]);
        });
        document.getElementById('btn-generate').addEventListener('click', generateNewGraph);

        console.log('Cold-Chain Logistics Optimizer initialized');
    }

    async function generateNewGraph() {
        UI.startSimulationPhase();
        UI.updateHud('Generating Network...', 'Building random graph with real Indian cities.');
        try {
            var numCities = parseInt(document.getElementById('gen-cities-count').value) || 15;
            var graphData = await API.generateGraph(numCities);
            GraphViz.init(graphData);
            UI.updateGraphInfo(graphData.node_count, graphData.edge_count);
            UI.populateDropdowns(GraphViz.getNodeIds());
            UI.resetToSetupPhase();
        } catch (err) {
            UI.showError('Failed to generate graph: ' + err.message);
        }
    }

    async function runPipeline() {
        UI.startSimulationPhase();
        GraphViz.clearHighlights();

        try {
            // Gather parameters
            var start = document.getElementById('tsp-start').value;
            var capacity = parseFloat(document.getElementById('knapsack-capacity').value) || 2000;
            var tspMethod = document.querySelector('input[name="tsp-method"]:checked').value;
            var blocked = GraphViz.getBlockedEdges();

            var params = {
                start: start,
                capacity: capacity,
                tsp_method: tspMethod,
                temp_penalty: true
            };
            if (blocked.length > 0) {
                params.blocked_edges = blocked;
            }

            // Phase 2: Simulation / HUD Updates
            UI.updateHud('Phase 1: Knapsack', 'Packing optimal cargo payload...');
            
            // Artificial delay to make it feel like a simulation
            const delay = (ms) => new Promise(res => setTimeout(res, ms));
            await delay(800);

            UI.updateHud('Phase 2: TSP & Dijkstra', 'Calculating exact shortest paths...');

            // Call pipeline
            var data = await API.runPipeline(params);

            // Phase 2.5: Animation
            UI.updateHud('Visualizing Route', 'Drawing calculated paths on map...');
            var pipeline = data.pipeline;
            await GraphViz.animatePipeline(pipeline);

            // Phase 3: Display Results Panel
            UI.showPipelineResults(data);
            UI.showResultsPhase();

        } catch (err) {
            UI.showError(err.message);
        }
    }

    function updateBlockedEdges() {
        var blocked = GraphViz.getBlockedEdges();
        UI.updateBlockedEdgesUI(blocked);
    }

    return {
        init: init,
        updateBlockedEdges: updateBlockedEdges,
    };
})();

document.addEventListener('DOMContentLoaded', App.init);
