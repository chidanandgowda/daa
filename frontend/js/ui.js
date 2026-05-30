/**
 * UI Controller — Pipeline-based result display
 */

const UI = (() => {
    const els = {};

    function cacheElements() {
        els.appMain          = document.getElementById('app-main');
        els.sidebar          = document.getElementById('sidebar');
        els.resultsPanel     = document.getElementById('results-panel');
        els.resultsContainer = document.getElementById('results-container');
        els.statusHud        = document.getElementById('status-hud');
        els.hudTitle         = document.getElementById('hud-title');
        els.hudDesc          = document.getElementById('hud-desc');
        els.btnRun           = document.getElementById('btn-run');
        els.btnResetSim      = document.getElementById('btn-reset-sim');
        els.tspStart         = document.getElementById('tsp-start');
        els.knapsackCap      = document.getElementById('knapsack-capacity');
        els.blockedList      = document.getElementById('blocked-edges-list');
        els.clearBlocked     = document.getElementById('clear-blocked');
        els.apiStatus        = document.getElementById('api-status');
        els.infoNodes        = document.getElementById('info-nodes');
        els.infoEdges        = document.getElementById('info-edges');
        els.pipeSteps        = document.querySelectorAll('.pipe-step');
    }

    function populateDropdowns(nodes) {
        var options = nodes.map(function(n) {
            return '<option value="' + n.id + '">' + n.name + ' (' + n.id + ')</option>';
        }).join('');
        els.tspStart.innerHTML = options;
    }

    /** Show full pipeline results */
    function showPipelineResults(data) {
        var pipeline = data.pipeline;
        var html = '';

        // Total time banner
        html += '<div class="total-time-banner">';
        html += '  <span class="total-time-label">Pipeline Complete</span>';
        html += '  <span class="total-time-value">' + data.total_execution_time_ms.toFixed(2) + ' ms</span>';
        html += '</div>';

        // Step 1: Knapsack
        if (pipeline.knapsack && !pipeline.knapsack.error) {
            var ks = pipeline.knapsack;
            var ksr = ks.result;
            html += buildResultStep(
                1, 'Cargo Load Balancing', ks.algorithm, '#EF4444', ks.execution_time_ms,
                '<div class="stats-grid">' +
                '  <div class="stat-box"><div class="stat-label">Total Value</div><div class="stat-value green">₹' + ksr.total_value.toLocaleString() + '</div></div>' +
                '  <div class="stat-box"><div class="stat-label">Weight</div><div class="stat-value">' + ksr.total_weight.toLocaleString() + ' kg</div></div>' +
                '  <div class="stat-box"><div class="stat-label">Utilization</div><div class="stat-value indigo">' + ksr.utilization_pct + '%</div></div>' +
                '  <div class="stat-box"><div class="stat-label">Items Selected</div><div class="stat-value">' + ksr.selected_items.length + '</div></div>' +
                '</div>' +
                buildCargoTable(ksr.selected_items) +
                buildComplexity(ksr.complexity)
            );
        }

        // Step 2: TSP
        if (pipeline.tsp && !pipeline.tsp.error) {
            var tsp = pipeline.tsp;
            var tspr = tsp.result;
            html += buildResultStep(
                2, 'Route Planning', tsp.algorithm, '#6366F1', tsp.execution_time_ms,
                '<div class="stats-grid">' +
                '  <div class="stat-box"><div class="stat-label">Total Cost</div><div class="stat-value indigo">₹' + tspr.total_cost.toLocaleString() + '</div></div>' +
                '  <div class="stat-box"><div class="stat-label">Stops</div><div class="stat-value">' + tspr.path.length + '</div></div>' +
                (tspr.dp_states_computed !== undefined ? '  <div class="stat-box"><div class="stat-label">DP States</div><div class="stat-value">' + tspr.dp_states_computed.toLocaleString() + '</div></div>' : '') +
                '</div>' +
                buildPathDisplay(tspr.path, '#6366F1') +
                buildComplexity(tspr.complexity)
            );
        }

        // Step 3: Dijkstra segments
        if (pipeline.dijkstra) {
            var dj = pipeline.dijkstra;
            html += buildResultStep(
                3, 'Shortest Safe Path', dj.algorithm, '#10B981', dj.execution_time_ms,
                '<div class="stats-grid">' +
                '  <div class="stat-box"><div class="stat-label">Total Segment Cost</div><div class="stat-value green">₹' + dj.total_segment_cost.toLocaleString() + '</div></div>' +
                '  <div class="stat-box"><div class="stat-label">Segments</div><div class="stat-value">' + dj.segments.length + '</div></div>' +
                '</div>' +
                buildSegmentList(dj.segments, '#10B981')
            );
        }

        // Step 4: A* (only if blocked edges were used)
        if (pipeline.astar) {
            var as = pipeline.astar;
            html += buildResultStep(
                4, 'Dynamic Rerouting', as.algorithm, '#F59E0B', as.execution_time_ms,
                '<p style="font-size:0.75rem; color:#475569; margin-bottom:8px;">Rerouted around ' + as.blocked_edges.length + ' blocked edge(s)</p>' +
                buildSegmentList(as.segments, '#F59E0B')
            );
        }

        els.resultsContainer.innerHTML = html;

        // Highlight active steps in pipeline flow
        els.pipeSteps.forEach(function(step) {
            var n = parseInt(step.dataset.step);
            if ((n === 1 && pipeline.knapsack) ||
                (n === 2 && pipeline.tsp) ||
                (n === 3 && pipeline.dijkstra) ||
                (n === 4 && pipeline.astar)) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }

    function buildResultStep(num, purpose, algoName, color, timeMs, bodyHTML) {
        return '<div class="result-step">' +
            '<div class="result-step-header">' +
            '  <div class="result-step-left">' +
            '    <div class="result-step-num" style="background:' + color + '">' + num + '</div>' +
            '    <div>' +
            '      <div class="result-step-name">' + purpose + '</div>' +
            '      <div style="font-size:0.68rem; color:#94A3B8; font-family:var(--font-mono)">' + algoName + '</div>' +
            '    </div>' +
            '  </div>' +
            '  <span class="result-step-time">⏱ ' + timeMs.toFixed(2) + ' ms</span>' +
            '</div>' +
            '<div class="result-step-body">' + bodyHTML + '</div>' +
            '</div>';
    }

    function buildPathDisplay(path, color) {
        if (!path || path.length === 0) return '';
        var nodes = path.map(function(n, i) {
            var arrow = (i < path.length - 1) ? '<span class="path-arrow">→</span>' : '';
            return '<span class="path-node" style="background:' + color + '14; color:' + color + '; border:1px solid ' + color + '33">' + n + '</span>' + arrow;
        }).join('');
        return '<div class="path-display"><div class="path-label">Route</div><div class="path-sequence">' + nodes + '</div></div>';
    }

    function buildComplexity(complexity) {
        if (!complexity) return '';
        return '<div class="complexity-box"><strong>Time:</strong> ' + complexity.time + '<br><strong>Space:</strong> ' + complexity.space + '</div>';
    }

    function buildCargoTable(items) {
        if (!items || items.length === 0) return '';
        var html = '<table class="cargo-table"><thead><tr><th>Item</th><th>Weight</th><th>Value</th></tr></thead><tbody>';
        items.forEach(function(item) {
            html += '<tr class="selected"><td>' + item.name + '</td><td>' + item.weight_kg + ' kg</td><td>₹' + item.value.toLocaleString() + '</td></tr>';
        });
        html += '</tbody></table>';
        return html;
    }

    function buildSegmentList(segments, color) {
        if (!segments || segments.length === 0) return '';
        var html = '<div class="segment-list">';
        segments.forEach(function(seg) {
            if (seg.error) {
                html += '<div class="segment-item" style="border-left:3px solid #EF4444"><span class="segment-route">' + seg.from + ' → ' + seg.to + '</span><span style="color:#EF4444; font-size:0.7rem">No path</span></div>';
            } else {
                html += '<div class="segment-item" style="border-left:3px solid ' + color + '"><span class="segment-route">' + seg.from + ' → ' + seg.to + '</span><span class="segment-cost">₹' + seg.cost.toLocaleString() + '</span></div>';
            }
        });
        html += '</div>';
        return html;
    }

    function updateBlockedEdgesUI(edges) {
        if (edges.length === 0) {
            els.blockedList.innerHTML = '<span class="empty-blocked">No blocked edges</span>';
            return;
        }
        els.blockedList.innerHTML = edges.map(function(e) {
            return '<span class="blocked-chip">' + e[0] + '↔' + e[1] + ' <span class="remove-blocked" data-src="' + e[0] + '" data-tgt="' + e[1] + '">✕</span></span>';
        }).join('');
    }

    function startSimulationPhase() {
        els.sidebar.classList.add('hidden-slide');
        els.resultsPanel.classList.add('hidden-slide');
        els.statusHud.classList.remove('hidden');
        els.appMain.classList.remove('sidebar-open');
        updateHud('Initializing Simulation...', 'Connecting to backend cluster...');
        setTimeout(function() { GraphViz.resize(); }, 400);
    }

    function showResultsPhase() {
        els.statusHud.classList.add('hidden');
        els.resultsPanel.classList.remove('hidden-slide');
        els.appMain.classList.add('sidebar-open');
        setTimeout(function() { GraphViz.resize(); }, 400);
    }

    function resetToSetupPhase() {
        els.resultsPanel.classList.add('hidden-slide');
        els.statusHud.classList.add('hidden');
        els.sidebar.classList.remove('hidden-slide');
        els.appMain.classList.add('sidebar-open');
        els.resultsContainer.innerHTML = '';
        GraphViz.reset();
        updateBlockedEdgesUI([]);
        setTimeout(function() { GraphViz.resize(); }, 400);
    }

    function updateHud(title, desc) {
        els.hudTitle.textContent = title;
        els.hudDesc.textContent = desc;
    }

    function showError(msg) {
        els.statusHud.classList.add('hidden');
        els.resultsPanel.classList.remove('hidden-slide');
        els.appMain.classList.add('sidebar-open');
        els.resultsContainer.innerHTML = '<div class="error-msg">⚠ ' + msg + '</div>';
        setTimeout(function() { GraphViz.resize(); }, 400);
    }

    function setApiStatus(connected) {
        if (connected) {
            els.apiStatus.textContent = '● Connected';
            els.apiStatus.classList.remove('offline');
        } else {
            els.apiStatus.textContent = '○ Offline';
            els.apiStatus.classList.add('offline');
        }
    }

    function updateGraphInfo(nodeCount, edgeCount) {
        els.infoNodes.textContent = nodeCount + ' nodes';
        els.infoEdges.textContent = edgeCount + ' edges';
    }

    function showResultsContainer(htmlContent) {
        els.resultsContainer.innerHTML = htmlContent;
    }

    function initEvents() {
        els.clearBlocked.addEventListener('click', function() {
            GraphViz.clearBlockedEdges();
            updateBlockedEdgesUI([]);
        });
        
        if (els.btnResetSim) {
            els.btnResetSim.addEventListener('click', resetToSetupPhase);
        }

        // Accordion logic for setup panels
        document.querySelectorAll('#sidebar .step-header').forEach(function(header) {
            header.addEventListener('click', function() {
                var panel = header.closest('.panel');
                
                // If it's already open, do nothing (or close it, depending on preference. Usually better to keep at least one open).
                // Let's make it toggleable, but collapse others.
                var wasCollapsed = panel.classList.contains('collapsed');
                
                // Collapse all
                document.querySelectorAll('#sidebar .panel').forEach(function(p) {
                    if (p.querySelector('.panel-body')) {
                        p.classList.add('collapsed');
                    }
                });
                
                // If it was collapsed, open it
                if (wasCollapsed) {
                    panel.classList.remove('collapsed');
                }
            });
        });
    }

    return {
        cacheElements: cacheElements,
        populateDropdowns: populateDropdowns,
        showPipelineResults: showPipelineResults,
        showResultsContainer: showResultsContainer,
        updateBlockedEdgesUI: updateBlockedEdgesUI,
        startSimulationPhase: startSimulationPhase,
        showResultsPhase: showResultsPhase,
        resetToSetupPhase: resetToSetupPhase,
        updateHud: updateHud,
        showError: showError,
        setApiStatus: setApiStatus,
        updateGraphInfo: updateGraphInfo,
        initEvents: initEvents,
    };
})();
