import { useEffect, useRef, useState } from 'react';
import type { Regulation } from '../data/mockData';

interface Node {
  id: string;
  label: string;
  type: 'query' | 'regulation';
  size: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  color?: string;
  bgColor?: string;
  regulation?: Regulation;
}

interface Edge {
  from: string;
  to: string;
  weight: number;
  color: string;
}

interface NetworkGraphProps {
  query: string;
  regulations: Regulation[];
}

export function NetworkGraph({ query, regulations }: NetworkGraphProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [hoveredNode, setHoveredNode] = useState<Node | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const animationRef = useRef<number | undefined>(undefined);

  // Initialize graph data
  useEffect(() => {
    if (!regulations || regulations.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    // Add query node
    newNodes.push({
      id: 'query',
      label: query,
      type: 'query',
      size: 50,
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
    });

    // Add regulation nodes
    regulations.forEach((reg, idx) => {
      const angle = (idx / regulations.length) * 2 * Math.PI;
      const radius = 200;
      
      newNodes.push({
        id: reg.id,
        label: reg.name,
        type: 'regulation',
        size: 30 + reg.similarityScore * 20,
        x: radius * Math.cos(angle),
        y: radius * Math.sin(angle),
        vx: 0,
        vy: 0,
        color: '#22c55e',
        bgColor: '#f0fdf4',
        regulation: reg,
      });

      // Add edge
      newEdges.push({
        from: 'query',
        to: reg.id,
        weight: reg.similarityScore,
        color: `rgba(34, 197, 94, ${reg.similarityScore * 0.5})`,
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [query, regulations]);

  // Physics simulation
  useEffect(() => {
    if (!canvasRef.current || nodes.length === 0) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const simulate = () => {
      setNodes(prevNodes => {
        const newNodes = [...prevNodes];
        
        // Apply forces
        newNodes.forEach((node, i) => {
          if (node.type === 'query') {
            // Keep query centered
            node.x = centerX;
            node.y = centerY;
            return;
          }

          // Spring force to maintain distance from query
          const dx = node.x - centerX;
          const dy = node.y - centerY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const targetDist = 200;
          const force = (dist - targetDist) * 0.01;
          
          node.vx -= (dx / dist) * force;
          node.vy -= (dy / dist) * force;

          // Repulsion between nodes
          newNodes.forEach((other, j) => {
            if (i === j || other.type === 'query') return;
            const dx2 = other.x - node.x;
            const dy2 = other.y - node.y;
            const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);
            if (dist2 < 100 && dist2 > 0) {
              const repulsion = 50 / (dist2 * dist2);
              node.vx -= (dx2 / dist2) * repulsion;
              node.vy -= (dy2 / dist2) * repulsion;
            }
          });

          // Apply velocity with damping
          node.vx *= 0.9;
          node.vy *= 0.9;
          node.x += node.vx;
          node.y += node.vy;
        });

        return newNodes;
      });

      animationRef.current = requestAnimationFrame(simulate);
    };

    simulate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [nodes.length]);

  return (
    <div className="relative w-full h-full bg-white">
      <div
        ref={canvasRef}
        className="w-full h-full relative"
        onMouseMove={(e) => setMousePos({ x: e.clientX, y: e.clientY })}
      >
        {/* Render edges */}
        <svg className="absolute inset-0 pointer-events-none">
          {edges.map((edge, idx) => {
            const fromNode = nodes.find(n => n.id === edge.from);
            const toNode = nodes.find(n => n.id === edge.to);
            if (!fromNode || !toNode) return null;

            return (
              <line
                key={idx}
                x1={fromNode.x}
                y1={fromNode.y}
                x2={toNode.x}
                y2={toNode.y}
                stroke={edge.color}
                strokeWidth={2}
              />
            );
          })}
        </svg>

        {/* Render nodes */}
        {nodes.map(node => (
          <div
            key={node.id}
            className={`absolute rounded-full flex items-center justify-center text-center transition-transform hover:scale-110 cursor-pointer ${
              node.type === 'query' ? 'bg-blue-100 border-4 border-blue-500 text-blue-900 font-semibold' : 'border-2'
            }`}
            style={{
              left: node.x - node.size,
              top: node.y - node.size,
              width: node.size * 2,
              height: node.size * 2,
              backgroundColor: node.bgColor,
              borderColor: node.color,
              fontSize: node.type === 'query' ? '0.75rem' : '0.65rem',
              padding: '0.5rem',
              lineHeight: 1.2,
            }}
            onMouseEnter={() => setHoveredNode(node)}
            onMouseLeave={() => setHoveredNode(null)}
          >
            {node.label.length > 30 ? node.label.slice(0, 27) + '...' : node.label}
          </div>
        ))}
      </div>

      {/* Tooltip */}
      {hoveredNode && hoveredNode.type === 'regulation' && hoveredNode.regulation && (
        <div
          className="fixed bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm z-50"
          style={{
            left: mousePos.x + 10,
            top: mousePos.y + 10,
          }}
        >
          <div className="font-semibold text-sm mb-2">{hoveredNode.regulation.name}</div>
          <div className="text-xs text-gray-600 mb-2">
            Similarity: {(hoveredNode.regulation.similarityScore * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-700 line-clamp-3">
            {hoveredNode.regulation.description}
          </div>
        </div>
      )}
    </div>
  );
}
