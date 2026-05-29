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

        console.log('Cold-Chain Logistics Optimizer initialized');
    }

    async function runPipeline() {
        UI.setLoading(true);
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
            };
            if (blocked.length > 0) {
                params.blocked_edges = blocked;
            }

            // Call pipeline
            var data = await API.runPipeline(params);

            // Display results
            UI.showPipelineResults(data);

            // Highlight on graph
            var pipeline = data.pipeline;

            // TSP route (primary)
            if (pipeline.tsp && pipeline.tsp.result && pipeline.tsp.result.path) {
                GraphViz.highlightTSPPath(pipeline.tsp.result.path);
            }

            // If A* was used, show rerouted segments
            if (pipeline.astar && pipeline.astar.segments) {
                GraphViz.highlightAStarSegments(pipeline.astar.segments);
            }

        } catch (err) {
            UI.showError(err.message);
        } finally {
            UI.setLoading(false);
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
