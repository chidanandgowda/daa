/**
 * Graph Visualization — Cytoscape.js Renderer
 * Manages the interactive graph with node/edge rendering,
 * path highlighting, and user interactions.
 */

const GraphViz = (() => {
    let cy = null;
    let graphData = null;

    // Algorithm-specific colors for path highlighting
    const ALGO_COLORS = {
        'held-karp':          '#06d6a0',
        'nearest-neighbour':  '#f77f00',
        'dijkstra':           '#118ab2',
        'astar':              '#7c3aed',
        'knapsack':           '#ef476f',
    };

    // Temperature zone → node color
    const TEMP_COLORS = {
        'hot':      '#ef476f',
        'moderate': '#06d6a0',
        'cold':     '#118ab2',
    };

    /**
     * Initialize Cytoscape instance with the graph data.
     * @param {Object} data - { nodes: [...], edges: [...] }
     */
    function init(data) {
        graphData = data;

        const elements = [];

        // Add nodes
        data.nodes.forEach(node => {
            elements.push({
                group: 'nodes',
                data: {
                    id: node.id,
                    label: `${node.name}\n(${node.id})`,
                    name: node.name,
                    temp_zone: node.temp_zone,
                    capacity: node.warehouse_capacity_kg,
                    lat: node.latitude,
                    lng: node.longitude,
                },
                position: {
                    // Map lat/lng to screen coordinates (approximate)
                    x: (node.longitude - 72) * 80 + 100,
                    y: (28 - node.latitude) * 80 + 100,
                },
            });
        });

        // Add edges
        data.edges.forEach(edge => {
            elements.push({
                group: 'edges',
                data: {
                    id: `${edge.source}-${edge.target}`,
                    source: edge.source,
                    target: edge.target,
                    cost: edge.cost,
                    distance: edge.distance_km,
                    label: `₹${(edge.cost / 1000).toFixed(1)}k`,
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

        // Fit graph into view with padding
        cy.fit(undefined, 50);

        // Add event listeners
        setupEvents();

        return cy;
    }

    /**
     * Get the Cytoscape stylesheet with all visual rules.
     */
    function getStylesheet() {
        return [
            // ── Node Styles ────────────────────────────────────────
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
                    'color': '#94a3b8',
                    'text-wrap': 'wrap',
                    'text-max-width': '80px',
                    'width': 28,
                    'height': 28,
                    'background-color': (ele) => TEMP_COLORS[ele.data('temp_zone')] || '#06d6a0',
                    'background-opacity': 0.85,
                    'border-width': 2,
                    'border-color': (ele) => TEMP_COLORS[ele.data('temp_zone')] || '#06d6a0',
                    'border-opacity': 0.4,
                    'overlay-opacity': 0,
                    'transition-property': 'background-color, border-color, width, height, background-opacity',
                    'transition-duration': '200ms',
                },
            },
            {
                selector: 'node:hover',
                style: {
                    'width': 34,
                    'height': 34,
                    'border-width': 3,
                    'border-opacity': 0.7,
                    'font-size': '11px',
                    'color': '#f1f5f9',
                    'z-index': 10,
                },
            },
            {
                selector: 'node.highlighted',
                style: {
                    'width': 36,
                    'height': 36,
                    'border-width': 3,
                    'border-opacity': 0.9,
                    'background-opacity': 1,
                    'font-weight': 700,
                    'color': '#f1f5f9',
                    'font-size': '11px',
                    'z-index': 20,
                },
            },
            {
                selector: 'node.start-node',
                style: {
                    'width': 40,
                    'height': 40,
                    'border-width': 4,
                    'shape': 'diamond',
                    'z-index': 30,
                },
            },

            // ── Edge Styles ────────────────────────────────────────
            {
                selector: 'edge',
                style: {
                    'width': 1.5,
                    'line-color': 'rgba(255, 255, 255, 0.1)',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-family': "'JetBrains Mono', monospace",
                    'font-size': '8px',
                    'color': 'rgba(255, 255, 255, 0.25)',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -8,
                    'overlay-opacity': 0,
                    'transition-property': 'line-color, width, opacity',
                    'transition-duration': '200ms',
                },
            },
            {
                selector: 'edge:hover',
                style: {
                    'width': 2.5,
                    'line-color': 'rgba(255, 255, 255, 0.3)',
                    'color': 'rgba(255, 255, 255, 0.5)',
                    'z-index': 10,
                },
            },
            {
                selector: 'edge.highlighted',
                style: {
                    'width': 3.5,
                    'line-opacity': 1,
                    'z-index': 20,
                    'color': 'rgba(255, 255, 255, 0.7)',
                    'font-size': '9px',
                    'font-weight': 700,
                },
            },
            {
                selector: 'edge.blocked',
                style: {
                    'width': 2,
                    'line-color': '#ef476f',
                    'line-style': 'dashed',
                    'opacity': 0.6,
                },
            },

            // ── Dimmed elements (non-highlighted) ──────────────────
            {
                selector: 'node.dimmed',
                style: {
                    'opacity': 0.25,
                },
            },
            {
                selector: 'edge.dimmed',
                style: {
                    'opacity': 0.08,
                },
            },
        ];
    }

    /**
     * Set up click and hover events on the graph.
     */
    function setupEvents() {
        // Node click — show info tooltip
        cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            const data = node.data();
            UI.showNodeInfo(data);
        });

        // Edge click — toggle blocked status (for A*)
        cy.on('tap', 'edge', (evt) => {
            const edge = evt.target;
            if (App.getCurrentAlgo() === 'astar') {
                edge.toggleClass('blocked');
                App.updateBlockedEdges();
            }
        });

        // Background click — deselect
        cy.on('tap', (evt) => {
            if (evt.target === cy) {
                clearHighlights();
            }
        });
    }

    /**
     * Highlight a path on the graph with algorithm-specific color.
     * @param {string[]} path - Array of node IDs forming the path
     * @param {string} algoKey - Algorithm identifier for color selection
     */
    function highlightPath(path, algoKey) {
        if (!cy || !path || path.length === 0) return;

        const color = ALGO_COLORS[algoKey] || '#06d6a0';

        // Dim everything first
        cy.elements().addClass('dimmed');

        // Highlight path nodes
        path.forEach((nodeId, index) => {
            const node = cy.getElementById(nodeId);
            if (node.length) {
                node.removeClass('dimmed').addClass('highlighted');
                node.style({
                    'background-color': color,
                    'border-color': color,
                });
                if (index === 0) {
                    node.addClass('start-node');
                }
            }
        });

        // Highlight path edges
        for (let i = 0; i < path.length - 1; i++) {
            const src = path[i];
            const tgt = path[i + 1];
            // Try both edge ID formats
            let edge = cy.getElementById(`${src}-${tgt}`);
            if (!edge.length) {
                edge = cy.getElementById(`${tgt}-${src}`);
            }
            if (edge.length) {
                edge.removeClass('dimmed').addClass('highlighted');
                edge.style({
                    'line-color': color,
                    'target-arrow-color': color,
                });
            }
        }
    }

    /**
     * Clear all path highlights and reset to default state.
     */
    function clearHighlights() {
        if (!cy) return;
        cy.elements().removeClass('highlighted dimmed start-node');
        // Reset styles
        cy.nodes().removeStyle();
        cy.edges().removeStyle();
        cy.edges('.blocked').style({
            'line-color': '#ef476f',
            'line-style': 'dashed',
            'opacity': 0.6,
        });
    }

    /**
     * Get all currently blocked edges.
     * @returns {Array<[string, string]>} Array of [source, target] pairs
     */
    function getBlockedEdges() {
        if (!cy) return [];
        const blocked = [];
        cy.edges('.blocked').forEach(edge => {
            blocked.push([edge.data('source'), edge.data('target')]);
        });
        return blocked;
    }

    /**
     * Clear all blocked edges.
     */
    function clearBlockedEdges() {
        if (!cy) return;
        cy.edges('.blocked').removeClass('blocked');
    }

    /**
     * Fit graph to viewport.
     */
    function fit() {
        if (cy) cy.fit(undefined, 50);
    }

    /**
     * Reset graph view and clear highlights.
     */
    function reset() {
        clearHighlights();
        clearBlockedEdges();
        if (cy) cy.fit(undefined, 50);
    }

    /**
     * Get all node IDs for populating dropdowns.
     */
    function getNodeIds() {
        if (!graphData) return [];
        return graphData.nodes.map(n => ({ id: n.id, name: n.name }));
    }

    return {
        init,
        highlightPath,
        clearHighlights,
        getBlockedEdges,
        clearBlockedEdges,
        fit,
        reset,
        getNodeIds,
        getColor: (key) => ALGO_COLORS[key] || '#06d6a0',
    };
})();
