/**
 * Graph Visualization — Cytoscape.js
 * Light theme with clean, professional styling
 */

const GraphViz = (() => {
    let cy = null;
    let graphData = null;

    const COLORS = {
        tsp:      '#6366F1',
        dijkstra: '#10B981',
        astar:    '#F59E0B',
    };

    const TEMP_COLORS = {
        hot:      '#EF4444',
        moderate: '#10B981',
        cold:     '#3B82F6',
    };

    function init(data) {
        graphData = data;
        const elements = [];

        data.nodes.forEach(node => {
            elements.push({
                group: 'nodes',
                data: {
                    id: node.id,
                    label: node.name + '\n(' + node.id + ')',
                    name: node.name,
                    temp_zone: node.temp_zone,
                    capacity: node.warehouse_capacity_kg,
                },
                position: {
                    x: (node.longitude - 72) * 85 + 80,
                    y: (28 - node.latitude) * 85 + 80,
                },
            });
        });

        data.edges.forEach(edge => {
            elements.push({
                group: 'edges',
                data: {
                    id: edge.source + '-' + edge.target,
                    source: edge.source,
                    target: edge.target,
                    cost: edge.cost,
                    distance: edge.distance_km,
                    label: '₹' + (edge.cost / 1000).toFixed(1) + 'k',
                },
            });
        });

        cy = cytoscape({
            container: document.getElementById('cy'),
            elements: elements,
            style: getStylesheet(),
            layout: { name: 'preset' },
            minZoom: 0.3,
            maxZoom: 3,
            wheelSensitivity: 0.3,
        });

        cy.fit(undefined, 50);
        setupEvents();
        return cy;
    }

    function getStylesheet() {
        return [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'bottom',
                    'text-halign': 'center',
                    'text-margin-y': 8,
                    'font-family': "'Inter', sans-serif",
                    'font-size': '10px',
                    'font-weight': 500,
                    'color': '#475569',
                    'text-wrap': 'wrap',
                    'text-max-width': '80px',
                    'width': 26,
                    'height': 26,
                    'background-color': function(ele) { return TEMP_COLORS[ele.data('temp_zone')] || '#10B981'; },
                    'background-opacity': 0.9,
                    'border-width': 2.5,
                    'border-color': function(ele) { return TEMP_COLORS[ele.data('temp_zone')] || '#10B981'; },
                    'border-opacity': 0.3,
                    'overlay-opacity': 0,
                    'transition-property': 'background-color, border-color, width, height',
                    'transition-duration': '200ms',
                },
            },
            {
                selector: 'node:hover',
                style: {
                    'width': 32,
                    'height': 32,
                    'border-opacity': 0.6,
                    'font-size': '11px',
                    'color': '#1E293B',
                    'z-index': 10,
                },
            },
            {
                selector: 'node.highlighted',
                style: {
                    'width': 32,
                    'height': 32,
                    'border-width': 3,
                    'border-opacity': 0.8,
                    'background-opacity': 1,
                    'font-weight': 700,
                    'color': '#1E293B',
                    'font-size': '11px',
                    'z-index': 20,
                },
            },
            {
                selector: 'node.start-node',
                style: {
                    'width': 36,
                    'height': 36,
                    'border-width': 3.5,
                    'shape': 'diamond',
                    'z-index': 30,
                },
            },
            {
                selector: 'edge',
                style: {
                    'width': 1.2,
                    'line-color': '#CBD5E1',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-family': "'JetBrains Mono', monospace",
                    'font-size': '7px',
                    'color': '#94A3B8',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -8,
                    'overlay-opacity': 0,
                    'transition-property': 'line-color, width',
                    'transition-duration': '200ms',
                },
            },
            {
                selector: 'edge:hover',
                style: {
                    'width': 2.5,
                    'line-color': '#94A3B8',
                    'color': '#475569',
                    'z-index': 10,
                },
            },
            {
                selector: 'edge.highlighted',
                style: {
                    'width': 3,
                    'line-opacity': 1,
                    'z-index': 20,
                    'color': '#475569',
                    'font-size': '8px',
                    'font-weight': 700,
                },
            },
            {
                selector: 'edge.blocked',
                style: {
                    'width': 2,
                    'line-color': '#EF4444',
                    'line-style': 'dashed',
                    'opacity': 0.7,
                },
            },
            {
                selector: 'node.dimmed',
                style: { 'opacity': 0.2 },
            },
            {
                selector: 'edge.dimmed',
                style: { 'opacity': 0.08 },
            },
        ];
    }

    function setupEvents() {
        cy.on('tap', 'edge', function(evt) {
            var edge = evt.target;
            edge.toggleClass('blocked');
            App.updateBlockedEdges();
        });

        cy.on('tap', function(evt) {
            if (evt.target === cy) {
                // Don't clear highlights on background click
            }
        });
    }

    /** Highlight TSP route */
    function highlightTSPPath(path) {
        if (!cy || !path || path.length === 0) return;
        cy.elements().addClass('dimmed');
        path.forEach(function(nodeId, i) {
            var node = cy.getElementById(nodeId);
            if (node.length) {
                node.removeClass('dimmed').addClass('highlighted');
                node.style({ 'background-color': COLORS.tsp, 'border-color': COLORS.tsp });
                if (i === 0) node.addClass('start-node');
            }
        });
        for (var i = 0; i < path.length - 1; i++) {
            highlightEdge(path[i], path[i + 1], COLORS.tsp);
        }
    }

    /** Highlight Dijkstra segments */
    function highlightDijkstraSegments(segments) {
        if (!cy || !segments) return;
        segments.forEach(function(seg) {
            if (seg.path && seg.path.length >= 2) {
                for (var i = 0; i < seg.path.length - 1; i++) {
                    highlightEdge(seg.path[i], seg.path[i + 1], COLORS.dijkstra);
                }
            }
        });
    }

    /** Highlight A* rerouted segments */
    function highlightAStarSegments(segments) {
        if (!cy || !segments) return;
        segments.forEach(function(seg) {
            if (seg.path && seg.path.length >= 2) {
                for (var i = 0; i < seg.path.length - 1; i++) {
                    highlightEdge(seg.path[i], seg.path[i + 1], COLORS.astar);
                }
                seg.path.forEach(function(nodeId) {
                    var node = cy.getElementById(nodeId);
                    if (node.length) {
                        node.removeClass('dimmed').addClass('highlighted');
                    }
                });
            }
        });
    }

    /** Animate the pipeline step-by-step */
    async function animatePipeline(pipeline) {
        if (!cy) return;
        clearHighlights();
        cy.elements().addClass('dimmed');

        const delay = (ms) => new Promise(res => setTimeout(res, ms));

        // Animate TSP
        if (pipeline.tsp && pipeline.tsp.result && pipeline.tsp.result.path) {
            let path = pipeline.tsp.result.path;
            for (let i = 0; i < path.length; i++) {
                let node = cy.getElementById(path[i]);
                if (node.length) {
                    node.removeClass('dimmed').addClass('highlighted');
                    node.style({ 'background-color': COLORS.tsp, 'border-color': COLORS.tsp });
                    if (i === 0) node.addClass('start-node');
                }
                
                await delay(300); // Wait 300ms before drawing edge
                
                if (i < path.length - 1) {
                    highlightEdge(path[i], path[i + 1], COLORS.tsp);
                    await delay(300); // Wait 300ms before next node
                }
            }
        }

        await delay(500);

        // Animate Reroutes (A*)
        if (pipeline.astar && pipeline.astar.segments) {
            for (let seg of pipeline.astar.segments) {
                if (seg.path && seg.path.length >= 2 && seg.was_affected) {
                    for (let i = 0; i < seg.path.length - 1; i++) {
                        highlightEdge(seg.path[i], seg.path[i + 1], COLORS.astar);
                        await delay(200);
                    }
                    seg.path.forEach(function(nodeId) {
                        var node = cy.getElementById(nodeId);
                        if (node.length) {
                            node.removeClass('dimmed').addClass('highlighted');
                        }
                    });
                }
            }
        }
    }

    function highlightEdge(src, tgt, color) {
        var edge = cy.getElementById(src + '-' + tgt);
        if (!edge.length) edge = cy.getElementById(tgt + '-' + src);
        if (edge.length) {
            edge.removeClass('dimmed').addClass('highlighted');
            edge.style({ 'line-color': color });
        }
    }

    function clearHighlights() {
        if (!cy) return;
        cy.elements().removeClass('highlighted dimmed start-node');
        cy.nodes().removeStyle();
        cy.edges().removeStyle();
        // Restore blocked edge styles
        cy.edges('.blocked').style({ 'line-color': '#EF4444', 'line-style': 'dashed', 'opacity': 0.7 });
    }

    function getBlockedEdges() {
        if (!cy) return [];
        var blocked = [];
        cy.edges('.blocked').forEach(function(edge) {
            blocked.push([edge.data('source'), edge.data('target')]);
        });
        return blocked;
    }

    function clearBlockedEdges() {
        if (!cy) return;
        cy.edges('.blocked').removeClass('blocked');
    }

    function fit() { if (cy) cy.fit(undefined, 50); }

    function resize() {
        if (cy) {
            cy.resize();
            cy.fit(undefined, 50);
        }
    }

    function reset() {
        clearHighlights();
        clearBlockedEdges();
        if (cy) cy.fit(undefined, 50);
    }

    function getNodeIds() {
        if (!graphData) return [];
        return graphData.nodes.map(function(n) { return { id: n.id, name: n.name }; });
    }

    return {
        init: init,
        highlightTSPPath: highlightTSPPath,
        highlightDijkstraSegments: highlightDijkstraSegments,
        highlightAStarSegments: highlightAStarSegments,
        animatePipeline: animatePipeline,
        clearHighlights: clearHighlights,
        getBlockedEdges: getBlockedEdges,
        clearBlockedEdges: clearBlockedEdges,
        fit: fit,
        reset: reset,
        resize: resize,
        getNodeIds: getNodeIds,
    };
})();
