#!/usr/bin/env python3
"""
Visualize RAG search results as interactive graphs
"""

import argparse
import json
from collections import defaultdict
import webbrowser
import os
import sys

# Import RAG search functionality
from rag_search import EULegislationRAG


def load_results(results_file: str):
    """Load search results from JSON file."""
    with open(results_file, 'r') as f:
        return json.load(f)


def run_search(query: str, index_endpoint: str, deployed_index_id: str, 
               project_id: str = "nimble-granite-478311-u2",
               location: str = "europe-west1",
               top_k: int = 20,
               use_cache: bool = True,
               system_prompt: str = None):
    """Run RAG search and return results.
    
    Args:
        query: Search query
        index_endpoint: Index endpoint name
        deployed_index_id: Deployed index ID
        project_id: GCP project ID
        location: GCP region
        top_k: Number of results
        use_cache: Whether to use cached results if available (deprecated, always False)
        system_prompt: Optional custom system prompt for LLM analysis
        
    Returns:
        Search results dictionary
    """
    print(f"\n{'='*80}")
    print(f"Running RAG Search")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"Top-K: {top_k}")
    
    # Initialize RAG system
    rag = EULegislationRAG(
        project_id=project_id,
        location=location,
        index_endpoint_name=index_endpoint,
        deployed_index_id=deployed_index_id,
        metadata_file='metadata_store_production.pkl'
    )
    
    # Execute query with LLM to get summaries
    result = rag.query(
        user_query=query,
        top_k=top_k,
        analyze_with_llm=True,  # Enable LLM to generate summaries
        use_query_expansion=False
    )
    
    print(f"\n✅ Search complete: {result['num_results']} results")
    
    return result, rag


def create_network_graph(result: dict, rag, output_file: str = "regulation_graph.html"):
    """Create interactive network graph from search results using custom HTML/CSS/JS.
    
    Args:
        result: Search result dictionary
        rag: RAG instance for LLM formatting
        output_file: Output HTML file path
    """
    print(f"\n{'='*80}")
    print(f"Creating Custom Network Graph Visualization")
    print(f"{'='*80}")
    
    # Group regulations by name
    regulation_groups = defaultdict(list)
    for chunk in result['top_chunks']:
        reg_name = chunk['metadata'].get('regulation_name', 'Unknown')
        regulation_groups[reg_name].append(chunk)
    
    print(f"Found {len(regulation_groups)} unique regulations")
    
    # Prepare data for visualization
    nodes_data = []
    edges_data = []
    
    # Add query node
    query_text = result['query']
    # Calculate size based on query length (roughly 8-10 chars per line for circular wrapping)
    chars_per_line = 12
    estimated_lines = max(2, len(query_text) / chars_per_line)
    query_size = max(45, min(80, 35 + (len(query_text) * 0.5)))  # Scale between 45-80 based on text length
    
    nodes_data.append({
        'id': 'query',
        'label': query_text,
        'type': 'query',
        'size': query_size
    })
    
    # Helper to normalize document type
    def normalize_doc_type(doc_type):
        """Normalize document type to main categories for consistent coloring."""
        if not doc_type:
            return 'Unknown'
        doc_type_lower = doc_type.lower()
        if 'regulation' in doc_type_lower:
            return 'Regulation'
        elif 'directive' in doc_type_lower:
            return 'Directive'
        elif 'decision' in doc_type_lower:
            return 'Decision'
        elif 'guideline' in doc_type_lower:
            return 'Guidelines'
        elif 'implementing' in doc_type_lower:
            return 'Implementing'
        elif 'delegated' in doc_type_lower:
            return 'Delegated'
        elif 'commission' in doc_type_lower:
            return 'Commission'
        return 'Unknown'
    
    # Color mapping
    type_colors = {
        'Regulation': {'bg': '#f0fdf4', 'border': '#22c55e', 'edge': 'rgba(34, 197, 94, 0.35)'},
        'Directive': {'bg': '#eff6ff', 'border': '#3b82f6', 'edge': 'rgba(59, 130, 246, 0.35)'},
        'Decision': {'bg': '#fef3c7', 'border': '#f59e0b', 'edge': 'rgba(245, 158, 11, 0.35)'},
        'Guidelines': {'bg': '#faf5ff', 'border': '#a855f7', 'edge': 'rgba(168, 85, 247, 0.35)'},
        'Commission': {'bg': '#fef3c7', 'border': '#f59e0b', 'edge': 'rgba(245, 158, 11, 0.35)'},
        'Implementing': {'bg': '#fff7ed', 'border': '#fb923c', 'edge': 'rgba(251, 146, 60, 0.35)'},
        'Delegated': {'bg': '#fef2f2', 'border': '#ef4444', 'edge': 'rgba(239, 68, 68, 0.35)'},
        'Unknown': {'bg': '#f9fafb', 'border': '#9ca3af', 'edge': 'rgba(156, 163, 175, 0.3)'}
    }
    
    # Use LLM to format regulation names consistently
    def format_regulation_names_with_llm(regulation_names, rag_instance):
        """Use LLM to format regulation names to a consistent, concise format for both node and tooltip."""
        if not regulation_names or not hasattr(rag_instance, 'chat_model') or not rag_instance.chat_model:
            # Fallback to simple formatting if LLM not available
            return {name: {'short': name[:30], 'full': name} for name in regulation_names}
        
        names_list = '\n'.join([f"{i+1}. {name}" for i, name in enumerate(regulation_names)])
        
        prompt = f"""You are a regulation name formatter. For each regulation, provide TWO versions:
1. SHORT version (for node display): Maximum 25 characters, concise
2. FULL version (for tooltip): Clean, readable, professional - remove verbose text but keep essential information

FORMAT YOUR RESPONSE EXACTLY AS:
SHORT: [short name]
FULL: [full name]

RULES for SHORT name:
- Maximum 25 characters
- Format as: "Type YEAR/NUMBER" (e.g., "Regulation 2013/575", "Directive 2013/36")
- If Commission/Implementing/Delegated, use abbreviation: "Comm Dec 2019/123", "Impl Reg 2020/456"

RULES for FULL name:
- Remove "of the European Parliament and of the Council"
- Remove specific dates like "of 26 June 2013"
- Keep the regulation type and number
- Keep "on [topic]" if it helps identify the regulation (but make it concise)
- Maximum 80 characters
- Format professionally: "Regulation (EU) No 575/2013 on prudential requirements"

INPUT REGULATIONS:
{names_list}

OUTPUT (for each regulation, provide SHORT and FULL on separate lines):"""
        
        try:
            response = rag_instance.chat_model.generate_content(prompt)
            lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            
            # Parse response - expect pairs of SHORT/FULL lines
            result = {}
            current_short = None
            
            for i, orig_name in enumerate(regulation_names):
                # Find the SHORT and FULL lines for this regulation
                short_name = None
                full_name = None
                
                # Look for lines starting with SHORT: and FULL:
                for line in lines:
                    if line.startswith('SHORT:'):
                        short_name = line.replace('SHORT:', '').strip().lstrip('0123456789. ')
                    elif line.startswith('FULL:') and short_name:
                        full_name = line.replace('FULL:', '').strip().lstrip('0123456789. ')
                        # Store the pair
                        if i < len(regulation_names):
                            result[regulation_names[min(len(result), i)]] = {
                                'short': short_name if short_name else orig_name[:25],
                                'full': full_name if full_name else orig_name
                            }
                        short_name = None
                        full_name = None
                
                # Fallback if parsing failed for this regulation
                if orig_name not in result:
                    result[orig_name] = {
                        'short': orig_name[:25],
                        'full': orig_name[:80]
                    }
            
            return result
        except Exception as e:
            print(f"Warning: LLM formatting failed ({e}), using fallback")
            return {name: {'short': name[:30], 'full': name} for name in regulation_names}
    
    # Get formatted names for all regulations
    formatted_names = format_regulation_names_with_llm(list(regulation_groups.keys()), rag)
    
    node_idx = 1
    for reg_name, chunks in regulation_groups.items():
        max_score = max(c['score'] for c in chunks)
        meta = chunks[0]['metadata']
        doc_type = meta.get('doc_type', 'Unknown')
        
        # Generate a summary from the most relevant chunk
        summary_text = chunks[0]['metadata'].get('full_text', '')
        # Truncate to first sentence or ~150 chars for tooltip
        if '. ' in summary_text[:200]:
            summary = summary_text[:summary_text[:200].index('. ') + 1]
        else:
            summary = summary_text[:150] + '...' if len(summary_text) > 150 else summary_text
        
        # Node size based on relevance - make them larger
        base_size = 35  # Increased from 15
        size_variation = min(len(chunks) * 4, 25)  # Increased variation
        node_size = base_size + size_variation
        
        # Get formatted names from LLM (short for node, full for tooltip)
        formatted = formatted_names.get(reg_name, {'short': reg_name[:25], 'full': reg_name})
        formatted_name = formatted['short']
        formatted_full_name = formatted['full']
        
        # Extract year and type from formatted short name (format: "Type YEAR/NUMBER")
        import re
        year_match = re.search(r'(\d{4})', formatted_name)
        year = year_match.group(1) if year_match else meta.get('year', 'N/A')
        
        # Extract type from formatted name for accuracy
        extracted_type = 'Unknown'
        name_lower = formatted_name.lower()
        if name_lower.startswith('regulation') or name_lower.startswith('reg '):
            extracted_type = 'Regulation'
        elif name_lower.startswith('directive') or name_lower.startswith('dir '):
            extracted_type = 'Directive'
        elif name_lower.startswith('decision') or name_lower.startswith('dec '):
            extracted_type = 'Decision'
        elif name_lower.startswith('comm'):
            extracted_type = 'Commission'
        elif name_lower.startswith('impl'):
            extracted_type = 'Implementing'
        elif name_lower.startswith('del'):
            extracted_type = 'Delegated'
        elif 'guideline' in name_lower:
            extracted_type = 'Guidelines'
        else:
            extracted_type = doc_type  # Fallback to metadata
        
        # Normalize doc_type for consistent coloring
        normalized_type = normalize_doc_type(extracted_type)
        colors = type_colors.get(normalized_type, type_colors['Unknown'])
        
        nodes_data.append({
            'id': f'node_{node_idx}',
            'label': formatted_name,  # Use short formatted name for display on node
            'fullName': formatted_full_name,  # Use formatted full name for tooltip
            'originalName': reg_name,  # Keep original for reference
            'type': extracted_type,  # Use extracted type instead of metadata
            'year': year,
            'matches': len(chunks),
            'relevance': max_score,
            'summary': summary,  # Add summary for tooltip
            'size': node_size,
            'color': colors['border'],
            'bgColor': colors['bg']
        })
        
        # Add edge
        edges_data.append({
            'from': 'query',
            'to': f'node_{node_idx}',
            'weight': max_score,
            'color': colors['edge'],
            'matches': len(chunks)
        })
        
        node_idx += 1
    
    # Generate custom HTML
    html_content = generate_custom_html(result['query'], result['num_results'], nodes_data, edges_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Custom network graph saved to: {output_file}")
    return output_file


def generate_custom_html(query: str, total_results: int, nodes: list, edges: list) -> str:
    """Generate custom HTML with inline CSS and JavaScript for the network graph."""
    
    import json
    
    nodes_json = json.dumps(nodes, indent=2)
    edges_json = json.dumps(edges, indent=2)
    
    # Get unique types present in the graph (excluding query node)
    present_types = set()
    for node in nodes:
        if node['type'] != 'query':
            normalized_type = node['type']
            # Normalize to main categories
            if 'regulation' in normalized_type.lower():
                present_types.add('Regulation')
            elif 'directive' in normalized_type.lower():
                present_types.add('Directive')
            elif 'decision' in normalized_type.lower():
                present_types.add('Decision')
            elif 'guideline' in normalized_type.lower():
                present_types.add('Guidelines')
            elif 'implementing' in normalized_type.lower():
                present_types.add('Implementing')
            elif 'delegated' in normalized_type.lower():
                present_types.add('Delegated')
            elif 'commission' in normalized_type.lower():
                present_types.add('Commission')
    
    # Build legend HTML only for present types
    legend_items = []
    type_legend_config = {
        'Regulation': {'bg': '#f0fdf4', 'border': '#22c55e'},
        'Directive': {'bg': '#eff6ff', 'border': '#3b82f6'},
        'Decision': {'bg': '#fef3c7', 'border': '#f59e0b'},
        'Guidelines': {'bg': '#faf5ff', 'border': '#a855f7'},
        'Implementing': {'bg': '#fff7ed', 'border': '#fb923c'},
        'Delegated': {'bg': '#fef2f2', 'border': '#ef4444'},
        'Commission': {'bg': '#fef3c7', 'border': '#f59e0b'}
    }
    
    for type_name in sorted(present_types):
        if type_name in type_legend_config:
            config = type_legend_config[type_name]
            legend_items.append(f'''
                <div class="legend-item">
                    <div class="legend-dot" style="background: {config['bg']}; border-color: {config['border']};"></div>
                    <span>{type_name}</span>
                </div>''')
    
    legend_html = ''.join(legend_items)
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EU Regulation Search - {query}</title>
    <style>
        :root {{
            --background: oklch(0.985 0 0);
            --foreground: oklch(0.145 0 0);
            --primary: #1e50be;
            --primary-hover: #1a45a8;
            --muted-foreground: oklch(0.708 0 0);
            --border: rgba(0, 0, 0, 0.08);
            --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            --radius: 0.75rem;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--background);
            color: var(--foreground);
            padding: 2rem;
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 2rem;
        }}
        
        h1 {{
            font-size: 1.875rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--foreground);
        }}
        
        .subtitle {{
            color: var(--muted-foreground);
            font-size: 0.875rem;
        }}
        
        .graph-container {{
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border);
            padding: 2rem;
            position: relative;
            overflow: hidden;
        }}
        
        #canvas {{
            width: 100%;
            height: 700px;
            cursor: grab;
            position: relative;
        }}
        
        #canvas:active {{
            cursor: grabbing;
        }}
        
        .node {{
            position: absolute;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 0.7rem;
            font-weight: 500;
            transition: all 0.2s ease;
            cursor: move;
            user-select: none;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
            padding: 0.5rem;
            line-height: 1.2;
            word-wrap: break-word;
            overflow: visible;
        }}
        
        .node:hover {{
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            z-index: 100;
        }}
        
        .node.dragging {{
            opacity: 0.8;
            cursor: grabbing;
            z-index: 1000;
        }}
        
        .node.query {{
            background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
            color: #1e3a8a;
            border: 3px solid #3b82f6;
            font-weight: 600;
            z-index: 5;
            font-size: 0.7rem;
            padding: 0.85rem;
            line-height: 1.25;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }}
        
        .edge {{
            position: absolute;
            height: 2px;
            transform-origin: 0 50%;
            transition: opacity 0.2s ease;
            pointer-events: none;
        }}
        
        .tooltip {{
            position: fixed;
            background: white;
            border-radius: var(--radius);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(0, 0, 0, 0.05);
            padding: 1rem;
            max-width: 320px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
            z-index: 1000;
        }}
        
        .tooltip.visible {{
            opacity: 1;
        }}
        
        .tooltip-title {{
            font-size: 0.9375rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: var(--foreground);
            line-height: 1.4;
        }}
        
        .tooltip-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.8125rem;
        }}
        
        .tooltip-label {{
            color: var(--muted-foreground);
            font-weight: 500;
        }}
        
        .tooltip-value {{
            color: var(--foreground);
        }}
        
        .tooltip-value.highlight {{
            color: var(--primary);
            font-weight: 600;
        }}
        
        .tooltip-divider {{
            margin: 0.75rem 0;
            border-top: 1px solid rgba(0, 0, 0, 0.06);
        }}
        
        .tooltip-summary {{
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(0, 0, 0, 0.06);
            font-size: 0.8125rem;
            line-height: 1.5;
            color: oklch(0.439 0 0);
            font-style: italic;
        }}
        
        .controls {{
            margin-top: 1.5rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border);
            background: white;
            color: var(--foreground);
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .btn:hover {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}
        
        .legend {{
            margin-top: 1.5rem;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.02);
            border-radius: 0.5rem;
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8125rem;
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 1.5px solid;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>EU Regulation Search</h1>
            <p class="subtitle">Query: {query}</p>
        </header>
        
        <div class="graph-container">
            <div id="canvas"></div>
            
            <div class="controls">
                <button class="btn" onclick="resetView()">Reset View</button>
            </div>
            
            <div class="legend">
                {legend_html}
            </div>
        </div>
        
        <div class="tooltip" id="tooltip"></div>
    </div>
    
    <script>
        const nodes = {nodes_json};
        const edges = {edges_json};
        
        const canvas = document.getElementById('canvas');
        const tooltip = document.getElementById('tooltip');
        
        let isDragging = false;
        let draggedNode = null;
        let offset = {{ x: 0, y: 0 }};
        let connectedNodes = new Set();
        
        // Physics simulation variables
        let animationId = null;
        const damping = 0.88; // Damping for smooth movement
        const linkStrength = 0.03; // Strength of connection between nodes
        const linkDistance = 150; // Desired distance between connected nodes
        
        // Store original positions and velocities
        nodes.forEach(node => {{
            node.vx = 0;
            node.vy = 0;
            node.originalX = 0;
            node.originalY = 0;
            node.isDragged = false;
        }});
        
        // Initialize node positions (circular layout around center)
        function initializePositions() {{
            const centerX = canvas.offsetWidth / 2;
            const centerY = canvas.offsetHeight / 2;
            const radius = Math.min(centerX, centerY) * 0.6;
            
            nodes.forEach((node, i) => {{
                if (node.type === 'query') {{
                    node.x = centerX;
                    node.y = centerY;
                    node.originalX = centerX;
                    node.originalY = centerY;
                }} else {{
                    const angle = (i / (nodes.length - 1)) * 2 * Math.PI;
                    node.x = centerX + radius * Math.cos(angle);
                    node.y = centerY + radius * Math.sin(angle);
                    node.originalX = node.x;
                    node.originalY = node.y;
                }}
                node.vx = 0;
                node.vy = 0;
            }});
        }}
        
        // Render edges
        function renderEdges() {{
            const existingEdges = canvas.querySelectorAll('.edge');
            existingEdges.forEach(e => e.remove());
            
            edges.forEach(edge => {{
                const fromNode = nodes.find(n => n.id === edge.from);
                const toNode = nodes.find(n => n.id === edge.to);
                
                if (!fromNode || !toNode) return;
                
                const dx = toNode.x - fromNode.x;
                const dy = toNode.y - fromNode.y;
                const length = Math.sqrt(dx * dx + dy * dy);
                const angle = Math.atan2(dy, dx) * 180 / Math.PI;
                
                const edgeEl = document.createElement('div');
                edgeEl.className = 'edge';
                edgeEl.style.width = length + 'px';
                edgeEl.style.left = fromNode.x + 'px';
                edgeEl.style.top = fromNode.y + 'px';
                edgeEl.style.transform = `rotate(${{angle}}deg)`;
                edgeEl.style.background = edge.color;
                edgeEl.style.opacity = '0.5';
                
                canvas.appendChild(edgeEl);
            }});
        }}
        
        // Render nodes
        function renderNodes() {{
            const existingNodes = canvas.querySelectorAll('.node');
            existingNodes.forEach(n => n.remove());
            
            nodes.forEach(node => {{
                const nodeEl = document.createElement('div');
                nodeEl.className = 'node' + (node.type === 'query' ? ' query' : '');
                nodeEl.style.width = node.size * 2 + 'px';
                nodeEl.style.height = node.size * 2 + 'px';
                nodeEl.style.left = (node.x - node.size) + 'px';
                nodeEl.style.top = (node.y - node.size) + 'px';
                
                if (node.type !== 'query') {{
                    nodeEl.style.background = node.bgColor;
                    nodeEl.style.border = '2px solid ' + node.color;
                    nodeEl.style.color = 'oklch(0.145 0 0)';
                    nodeEl.style.padding = '0.5rem';
                    nodeEl.style.fontSize = '0.7rem';
                    // Display full label - the node is sized to fit it
                    nodeEl.textContent = node.label;
                }} else {{
                    // Query node - show full text with wrapping
                    nodeEl.textContent = node.label;
                    nodeEl.style.whiteSpace = 'normal';
                    nodeEl.style.wordBreak = 'break-word';
                }}
                
                nodeEl.dataset.nodeId = node.id;
                
                // Tooltip on hover
                nodeEl.addEventListener('mouseenter', (e) => {{
                    if (node.type === 'query') {{
                        showTooltip(e, `
                            <div class="tooltip-title">${{node.label}}</div>
                            <div class="tooltip-row">
                                <span class="tooltip-label">Total Results:</span>
                                <span class="tooltip-value">{total_results}</span>
                            </div>
                        `);
                    }} else {{
                        showTooltip(e, `
                            <div class="tooltip-title">${{node.fullName}}</div>
                            <div class="tooltip-row">
                                <span class="tooltip-label">Type:</span>
                                <span class="tooltip-value">${{node.type}}</span>
                            </div>
                            <div class="tooltip-row">
                                <span class="tooltip-label">Year:</span>
                                <span class="tooltip-value">${{node.year}}</span>
                            </div>
                            <div class="tooltip-row">
                                <span class="tooltip-label">Matches:</span>
                                <span class="tooltip-value">${{node.matches}}</span>
                            </div>
                            <div class="tooltip-row">
                                <span class="tooltip-label">Relevance:</span>
                                <span class="tooltip-value highlight">${{(node.relevance * 100).toFixed(1)}}%</span>
                            </div>
                            ${{node.summary ? `<div class="tooltip-summary">${{node.summary}}</div>` : ''}}
                        `);
                    }}
                }});
                
                nodeEl.addEventListener('mouseleave', hideTooltip);
                
                // Dragging - allow all nodes to be dragged
                nodeEl.addEventListener('mousedown', (e) => {{
                    const canvasRect = canvas.getBoundingClientRect();
                    isDragging = true;
                    draggedNode = node;
                    node.isDragged = true;
                    node.vx = 0;
                    node.vy = 0;
                    nodeEl.classList.add('dragging');
                    offset = {{
                        x: e.clientX - canvasRect.left - node.x,
                        y: e.clientY - canvasRect.top - node.y
                    }};
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Start physics simulation
                    startPhysics();
                }});
                
                canvas.appendChild(nodeEl);
            }});
        }}
        
        function showTooltip(e, content) {{
            tooltip.innerHTML = content;
            tooltip.style.left = e.pageX + 2 + 'px';
            tooltip.style.top = e.pageY + 2 + 'px';
            tooltip.classList.add('visible');
        }}
        
        function hideTooltip() {{
            tooltip.classList.remove('visible');
        }}
        
        // Get connected nodes for a given node
        function getConnectedNodes(node) {{
            const connected = new Set();
            edges.forEach(edge => {{
                if (edge.from === node.id) {{
                    const connectedNode = nodes.find(n => n.id === edge.to);
                    if (connectedNode) connected.add(connectedNode);
                }}
                if (edge.to === node.id) {{
                    const connectedNode = nodes.find(n => n.id === edge.from);
                    if (connectedNode) connected.add(connectedNode);
                }}
            }});
            return connected;
        }}
        
        // Physics simulation - nodes follow dragged nodes
        function applyPhysics() {{
            let hasMovement = false;
            
            // Apply link forces between connected nodes
            edges.forEach(edge => {{
                const fromNode = nodes.find(n => n.id === edge.from);
                const toNode = nodes.find(n => n.id === edge.to);
                
                if (!fromNode || !toNode) return;
                
                // Calculate distance and direction
                const dx = toNode.x - fromNode.x;
                const dy = toNode.y - fromNode.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance === 0) return;
                
                // Apply spring force to maintain desired distance
                const force = (distance - linkDistance) * linkStrength;
                const fx = (dx / distance) * force;
                const fy = (dy / distance) * force;
                
                // Don't apply force to dragged node
                if (!fromNode.isDragged) {{
                    fromNode.vx += fx;
                    fromNode.vy += fy;
                }}
                if (!toNode.isDragged) {{
                    toNode.vx -= fx;
                    toNode.vy -= fy;
                }}
            }});
            
            // Update positions based on velocities
            nodes.forEach(node => {{
                if (node.isDragged) return; // Skip dragged node
                
                // Apply damping
                node.vx *= damping;
                node.vy *= damping;
                
                // Update position
                node.x += node.vx;
                node.y += node.vy;
                
                // Keep nodes within canvas bounds
                const margin = node.size || 20;
                node.x = Math.max(margin, Math.min(canvas.offsetWidth - margin, node.x));
                node.y = Math.max(margin, Math.min(canvas.offsetHeight - margin, node.y));
                
                // Check if still moving
                if (Math.abs(node.vx) > 0.05 || Math.abs(node.vy) > 0.05) {{
                    hasMovement = true;
                }}
            }});
            
            render();
            
            // Continue animation if there's movement or dragging
            if (hasMovement || isDragging) {{
                animationId = requestAnimationFrame(applyPhysics);
            }} else {{
                animationId = null;
            }}
        }}
        
        // Start physics loop
        function startPhysics() {{
            if (!animationId) {{
                animationId = requestAnimationFrame(applyPhysics);
            }}
        }}
        
        // Mouse move handler
        document.addEventListener('mousemove', (e) => {{
            if (isDragging && draggedNode) {{
                const canvasRect = canvas.getBoundingClientRect();
                const newX = e.clientX - canvasRect.left - offset.x;
                const newY = e.clientY - canvasRect.top - offset.y;
                
                // Keep node within bounds
                const margin = draggedNode.size || 20;
                draggedNode.x = Math.max(margin, Math.min(canvas.offsetWidth - margin, newX));
                draggedNode.y = Math.max(margin, Math.min(canvas.offsetHeight - margin, newY));
                
                // Render immediately for smooth dragging
                render();
            }}
            
            if (tooltip.classList.contains('visible')) {{
                tooltip.style.left = e.pageX + 2 + 'px';
                tooltip.style.top = e.pageY + 2 + 'px';
            }}
        }});
        
        document.addEventListener('mouseup', () => {{
            if (isDragging && draggedNode) {{
                draggedNode.isDragged = false;
                const nodeEl = canvas.querySelector(`[data-node-id="${{draggedNode.id}}"]`);
                if (nodeEl) nodeEl.classList.remove('dragging');
                draggedNode = null;
                
                // Continue physics for a bit to settle connected nodes
                startPhysics();
            }}
            isDragging = false;
        }});
        
        function render() {{
            renderEdges();
            renderNodes();
        }}
        
        function resetView() {{
            initializePositions();
            startPhysics();
        }}
        
        // Initialize
        initializePositions();
        render();
        startPhysics();
        
        // Redraw on window resize
        window.addEventListener('resize', () => {{
            resetView();
        }});
    </script>
</body>
</html>'''


def create_timeline_view(result: dict, output_file: str = "regulation_timeline.html"):
    """Create timeline visualization with plotly."""
    import plotly.graph_objects as go
    import plotly.express as px
    
    print(f"\n{'='*80}")
    print(f"Creating Timeline Visualization")
    print(f"{'='*80}")
    
    # Prepare data
    data = []
    for chunk in result['top_chunks']:
        meta = chunk['metadata']
        year = meta.get('year')
        if not year or year == 'N/A':
            continue
        
        data.append({
            'Regulation': meta.get('regulation_name', 'Unknown')[:50],
            'Year': year,
            'Score': chunk['score'],
            'Article': str(meta.get('article_number', 'N/A')),
            'Type': meta.get('doc_type', 'Unknown'),
            'Text': meta.get('full_text', '')[:200] + '...'
        })
    
    if not data:
        print("⚠️  No valid year data for timeline")
        return None
    
    print(f"Plotting {len(data)} regulations on timeline")
    
    # Create scatter plot with frontend colors
    fig = px.scatter(
        data,
        x='Year',
        y='Score',
        size=[max(s*1000, 10) for s in [d['Score'] for d in data]],
        color='Type',
        hover_data=['Regulation', 'Article', 'Text'],
        title=f"Regulation Timeline: {result['query']}",
        labels={'Score': 'Relevance Score', 'Year': 'Publication Year'},
        color_discrete_map={
            'Regulation': '#22c55e',
            'Directive': '#3b82f6',
            'Decision': '#f59e0b',
            'Guidelines': '#a855f7'
        }
    )
    
    fig.update_layout(
        template='plotly_white',
        height=700,
        hovermode='closest',
        showlegend=True,
        font=dict(family='system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', size=13, color='oklch(0.145 0 0)'),
        plot_bgcolor='oklch(0.985 0 0)',
        paper_bgcolor='oklch(0.985 0 0)',
        title=dict(
            font=dict(size=18, weight=600)
        ),
        xaxis=dict(
            title='Year',
            gridcolor='rgba(0,0,0,0.04)',
            linecolor='rgba(0,0,0,0.08)',
            zerolinecolor='rgba(0,0,0,0.08)'
        ),
        yaxis=dict(
            title='Relevance Score',
            gridcolor='rgba(0,0,0,0.04)',
            linecolor='rgba(0,0,0,0.08)',
            zerolinecolor='rgba(0,0,0,0.08)'
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='rgba(0,0,0,0.08)',
            borderwidth=1,
            font=dict(size=12)
        )
    )
    
    fig.write_html(output_file)
    print(f"✅ Timeline saved to: {output_file}")
    
    return output_file


def create_sunburst_view(result: dict, output_file: str = "regulation_sunburst.html"):
    """Create hierarchical sunburst visualization."""
    import plotly.graph_objects as go
    
    print(f"\n{'='*80}")
    print(f"Creating Sunburst Hierarchy Visualization")
    print(f"{'='*80}")
    
    # Build hierarchy: Query -> Type -> Year -> Regulation
    hierarchy_data = {
        'labels': [],
        'parents': [],
        'values': [],
        'colors': []
    }
    
    # Root
    hierarchy_data['labels'].append(result['query'][:40])
    hierarchy_data['parents'].append('')
    hierarchy_data['values'].append(0)
    hierarchy_data['colors'].append('#1e50be')
    
    # Group by type and year
    type_groups = defaultdict(lambda: defaultdict(list))
    
    for chunk in result['top_chunks']:
        meta = chunk['metadata']
        doc_type = meta.get('doc_type', 'Unknown')
        year = str(meta.get('year', 'N/A'))
        reg_name = meta.get('regulation_name', 'Unknown')[:40]
        
        type_groups[doc_type][year].append((reg_name, chunk['score']))
    
    type_colors = {
        'Regulation': '#22c55e',
        'Directive': '#3b82f6',
        'Decision': '#f59e0b',
        'Guidelines': '#a855f7',
        'Unknown': '#9ca3af'
    }
    
    root_label = result['query'][:40]
    
    for doc_type, years in type_groups.items():
        # Add type level
        type_label = doc_type
        hierarchy_data['labels'].append(type_label)
        hierarchy_data['parents'].append(root_label)
        hierarchy_data['values'].append(sum(len(regs) for regs in years.values()))
        hierarchy_data['colors'].append(type_colors.get(doc_type, '#9E9E9E'))
        
        for year, regs in years.items():
            # Add year level
            year_label = f"{year} ({doc_type})"
            hierarchy_data['labels'].append(year_label)
            hierarchy_data['parents'].append(type_label)
            hierarchy_data['values'].append(len(regs))
            hierarchy_data['colors'].append(type_colors.get(doc_type, '#9E9E9E'))
            
            # Add regulation level
            seen_regs = set()
            for reg_name, score in regs:
                if reg_name not in seen_regs:
                    hierarchy_data['labels'].append(reg_name)
                    hierarchy_data['parents'].append(year_label)
                    hierarchy_data['values'].append(score * 100)
                    hierarchy_data['colors'].append(type_colors.get(doc_type, '#9E9E9E'))
                    seen_regs.add(reg_name)
    
    print(f"Created hierarchy with {len(hierarchy_data['labels'])} nodes")
    
    fig = go.Figure(go.Sunburst(
        labels=hierarchy_data['labels'],
        parents=hierarchy_data['parents'],
        values=hierarchy_data['values'],
        marker=dict(colors=hierarchy_data['colors']),
        branchvalues='total'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Regulation Hierarchy: {result['query']}",
            font=dict(size=18, family='system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', color='oklch(0.145 0 0)', weight=600)
        ),
        template='plotly_white',
        height=800,
        font=dict(family='system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', size=12, color='oklch(0.145 0 0)'),
        paper_bgcolor='oklch(0.985 0 0)',
        plot_bgcolor='oklch(0.985 0 0)'
    )
    
    fig.write_html(output_file)
    print(f"✅ Sunburst saved to: {output_file}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description='Visualize RAG search results')
    parser.add_argument(
        '--query',
        type=str,
        help='Search query (alternative to --results)'
    )
    parser.add_argument(
        '--index-endpoint',
        type=str,
        default='projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912',
        help='Index endpoint name'
    )
    parser.add_argument(
        '--deployed-index-id',
        type=str,
        default='eu_legislation_prod_75480320',
        help='Deployed index ID'
    )
    parser.add_argument(
        '--project-id',
        type=str,
        default='nimble-granite-478311-u2',
        help='GCP project ID'
    )
    parser.add_argument(
        '--location',
        type=str,
        default='europe-west1',
        help='GCP region'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=10,
        help='Number of results to retrieve'
    )
    parser.add_argument(
        '--results',
        type=str,
        help='JSON file with search results (alternative to --query)'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=['graph', 'timeline', 'sunburst', 'all'],
        default='graph',
        help='Type of visualization'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='regulation_graph.html',
        help='Output HTML file'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Open in browser after creation'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Skip cache, force fresh search'
    )
    parser.add_argument(
        '--system-prompt',
        type=str,
        help='Custom system prompt for LLM analysis'
    )
    
    args = parser.parse_args()
    
    # Get results either from search or file
    if args.query:
        # Run search directly
        result, rag = run_search(
            query=args.query,
            index_endpoint=args.index_endpoint,
            deployed_index_id=args.deployed_index_id,
            project_id=args.project_id,
            location=args.location,
            top_k=args.top_k,
            use_cache=not args.no_cache,
            system_prompt=args.system_prompt
        )
    elif args.results:
        # Load from file
        if not os.path.exists(args.results):
            print(f"❌ Results file not found: {args.results}")
            print(f"   Use --query to run a search directly")
            return
        print(f"Loading results from: {args.results}")
        result = load_results(args.results)
        rag = None  # No RAG instance when loading from file
    else:
        print("❌ Must provide either --query or --results")
        parser.print_help()
        return
    
    output_files = []
    
    if args.type in ['graph', 'all']:
        graph_file = args.output
        create_network_graph(result, rag, graph_file)
        output_files.append(graph_file)
    
    if args.type in ['timeline', 'all']:
        timeline_file = args.output.replace('.html', '_timeline.html')
        create_timeline_view(result, timeline_file)
        if timeline_file:
            output_files.append(timeline_file)
    
    if args.type in ['sunburst', 'all']:
        sunburst_file = args.output.replace('.html', '_sunburst.html')
        create_sunburst_view(result, sunburst_file)
        output_files.append(sunburst_file)
    
    # Open in browser if requested
    if args.open and output_files:
        import webbrowser
        for f in output_files:
            webbrowser.open('file://' + os.path.abspath(f))
    
    print(f"\n{'='*80}")
    print(f"✅ Visualization Complete!")
    print(f"{'='*80}")
    print(f"Generated files:")
    for f in output_files:
        print(f"  • {f}")
    print()


if __name__ == "__main__":
    main()
