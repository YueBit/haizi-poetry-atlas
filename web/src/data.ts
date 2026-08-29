// Load the generated dataset (copied into public/data by `npm run copy-data`).
import type { AtlasData, ImageryNode, Poem } from "./types";

const BASE = import.meta.env.BASE_URL;

async function fetchJson<T>(name: string): Promise<T> {
  const res = await fetch(`${BASE}data/${name}.json`);
  if (!res.ok) {
    throw new Error(`Failed to load data/${name}.json (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function loadData(): Promise<AtlasData> {
  const [stats, imagery, cooccurrence, poems] = await Promise.all([
    fetchJson<AtlasData["stats"]>("stats"),
    fetchJson<AtlasData["imagery"]>("imagery"),
    fetchJson<AtlasData["cooccurrence"]>("cooccurrence"),
    fetchJson<AtlasData["poems"]>("poems"),
  ]);
  return { stats, imagery, cooccurrence, poems };
}

export function byWord(imagery: ImageryNode[]): Map<string, ImageryNode> {
  const map = new Map<string, ImageryNode>();
  for (const node of imagery) map.set(node.word, node);
  return map;
}

export function byId(poems: Poem[]): Map<string, Poem> {
  const map = new Map<string, Poem>();
  for (const poem of poems) map.set(poem.id, poem);
  return map;
}
