import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
  type Simulation,
} from "d3-force";
import { useData } from "../App";
import type { ImageryNode, Theme } from "../types";
import { THEME_LABELS, themeColor } from "../lib/theme";

// Each word connects only to its strongest few co-occurrences.
const RELATED_K = 4;

interface SimNode {
  id: string;
  theme: Theme;
  frequency: number;
  x: number;
  y: number;
}

interface SimLink {
  source: string;
  target: string;
  score: number;
}

interface Position {
  x: number;
  y: number;
}

// Font size (px) for a node label, scaled by its frequency.
function fontSize(frequency: number, maxFreq: number): number {
  return 11 + Math.pow(frequency / maxFreq, 0.8) * 26;
}

// Dot marker radius for a node.
function dotRadius(frequency: number, maxFreq: number): number {
  return 2.4 + Math.pow(frequency / maxFreq, 0.8) * 4;
}

export default function Atlas() {
  const { data } = useData();
  const navigate = useNavigate();
  const stageRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ w: 960, h: 640 });
  const [positions, setPositions] = useState<Record<string, Position>>({});
  const [hover, setHover] = useState<string | null>(null);
  const [offset, setOffset] = useState<Position>({ x: 0, y: 0 });

  const { nodes, links, neighbors, maxFreq } = useMemo(() => {
    const maxFreq = Math.max(...data.imagery.map((n) => n.frequency));
    const nodeList: SimNode[] = data.imagery
      .map((n: ImageryNode) => ({
        id: n.word,
        theme: n.theme,
        frequency: n.frequency,
        x: 0,
        y: 0,
      }))
      .sort((a, b) => b.frequency - a.frequency);

    // Build a sparse constellation: each word keeps only its strongest few
    // co-occurrences (its top RELATED_K neighbours), so the field reads as
    // related images rather than a dense hairball.
    const seen = new Set<string>();
    const linkList: SimLink[] = [];
    for (const n of data.imagery) {
      for (const r of n.related.slice(0, RELATED_K)) {
        const key = [n.word, r.word].sort().join("\u0000");
        if (seen.has(key)) continue;
        seen.add(key);
        linkList.push({ source: n.word, target: r.word, score: r.score });
      }
    }

    const neighborMap = new Map<string, Set<string>>();
    for (const l of linkList) {
      if (!neighborMap.has(l.source)) neighborMap.set(l.source, new Set());
      if (!neighborMap.has(l.target)) neighborMap.set(l.target, new Set());
      neighborMap.get(l.source)!.add(l.target);
      neighborMap.get(l.target)!.add(l.source);
    }

    return { nodes: nodeList, links: linkList, neighbors: neighborMap, maxFreq };
  }, [data]);

  // Measure the stage so text renders at a consistent pixel size.
  useEffect(() => {
    const el = stageRef.current;
    if (!el) return;
    const measure = () => setDims({ w: el.clientWidth, h: el.clientHeight });
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Run the force simulation once nodes/links/space are ready.
  useEffect(() => {
    const simNodes: SimNode[] = nodes.map((n) => ({ ...n }));
    const simLinks: SimLink[] = links.map((l) => ({ ...l }));

    const simulation: Simulation<SimNode, SimLink> = forceSimulation(simNodes)
      .force(
        "link",
        forceLink<SimNode, SimLink>(simLinks)
          .id((d) => d.id)
          .distance(72)
          .strength(0.16)
      )
      .force("charge", forceManyBody<SimNode>().strength(-150))
      .force(
        "collide",
        forceCollide<SimNode>().radius(
          (d) => (d.id.length * fontSize(d.frequency, maxFreq)) / 2 + 6
        )
      )
      .force("x", forceX<SimNode>(dims.w / 2).strength(0.08))
      .force("y", forceY<SimNode>(dims.h / 2).strength(0.12));

    simulation.on("tick", () => {
      const pos: Record<string, Position> = {};
      let minX = Infinity;
      let maxX = -Infinity;
      let minY = Infinity;
      let maxY = -Infinity;
      for (const n of simNodes) {
        pos[n.id] = { x: n.x, y: n.y };
        if (n.x < minX) minX = n.x;
        if (n.x > maxX) maxX = n.x;
        if (n.y < minY) minY = n.y;
        if (n.y > maxY) maxY = n.y;
      }
      setPositions(pos);
      // Keep the whole constellation visually centred in the stage.
      setOffset({
        x: dims.w / 2 - (minX + maxX) / 2,
        y: dims.h / 2 - (minY + maxY) / 2,
      });
    });

    return () => {
      simulation.stop();
    };
  }, [nodes, links, dims, maxFreq]);

  const hoverNeighbors = hover ? neighbors.get(hover) : undefined;

  return (
    <div className="container container--wide">
      <section className="section" style={{ paddingBottom: "0" }}>
        <h1 className="display" style={{ textAlign: "center" }}>
          海子诗歌图谱
        </h1>
        <p
          className="eyebrow"
          style={{ textAlign: "center", marginTop: "0.75rem" }}
        >
          Haizi Poetry Atlas
        </p>
      </section>

      <div
        ref={stageRef}
        className={`atlas-stage ${hover ? "dimmed" : ""}`}
        style={{ margin: "1.25rem 0" }}
      >
        <svg>
          <g transform={`translate(${offset.x}, ${offset.y})`}>
            {links.map((l, i) => {
              const a = positions[l.source];
              const b = positions[l.target];
              if (!a || !b) return null;
              const active = hover && (l.source === hover || l.target === hover);
              return (
                <line
                  key={i}
                  className={`atlas-edge ${active ? "active" : ""}`}
                  x1={a.x}
                  y1={a.y}
                  x2={b.x}
                  y2={b.y}
                  strokeOpacity={active ? 0.6 : 0.32}
                  strokeWidth={active ? 1.1 : 0.7}
                />
              );
            })}

            {nodes.map((n) => {
              const p = positions[n.id];
              if (!p) return null;
              const color = themeColor(n.theme);
              const active = !hover || hover === n.id || hoverNeighbors?.has(n.id);
              const fs = fontSize(n.frequency, maxFreq);
              return (
                <g
                  key={n.id}
                  className={`atlas-node ${active ? "active" : ""}`}
                  transform={`translate(${p.x},${p.y})`}
                  onMouseEnter={() => setHover(n.id)}
                  onMouseLeave={() => setHover(null)}
                  onClick={() => navigate(`/imagery/${encodeURIComponent(n.id)}`)}
                >
                  <circle
                    r={dotRadius(n.frequency, maxFreq)}
                    fill={color}
                    fillOpacity={0.85}
                  />
                  <text
                    fontSize={fs}
                    x={dotRadius(n.frequency, maxFreq) + 5}
                    dominantBaseline="central"
                  >
                    {n.id}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      <section className="section" style={{ paddingTop: "1.25rem" }}>
        <p className="lead" style={{ textAlign: "center" }}>
          探索海子诗歌中反复出现的意象，以及它们彼此之间的关系。
          <br />
          点击一个词，进入它的世界。
        </p>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            gap: "0.9rem 1.5rem",
            marginTop: "2rem",
          }}
        >
          {(Object.keys(THEME_LABELS) as Theme[]).map((t) => (
            <span
              key={t}
              className="muted"
              style={{ fontSize: "0.82rem", letterSpacing: "0.06em" }}
            >
              <span
                style={{
                  display: "inline-block",
                  width: "0.55rem",
                  height: "0.55rem",
                  borderRadius: "50%",
                  background: themeColor(t),
                  marginRight: "0.45rem",
                  verticalAlign: "middle",
                }}
              />
              {THEME_LABELS[t]}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
