// Data model shared with the Python pipeline (see data/*.json).

export type Theme = "nature" | "light" | "home" | "body" | "death" | "myth" | "place";

export interface RelatedWord {
  word: string;
  score: number;
  cooccur: number;
}

export interface ImageryNode {
  word: string;
  theme: Theme;
  theme_label: string;
  frequency: number;
  poem_count: number;
  poem_ids: string[];
  by_year: Record<string, number>;
  related: RelatedWord[];
}

export interface Occurrence {
  word: string;
  line: number;
  text: string;
}

export interface Poem {
  id: string;
  title: string;
  year: number | null;
  date: string | null;
  section: string | null;
  line_count: number;
  imagery: Record<string, number>;
  occurrences: Occurrence[];
}

export interface Edge {
  a: string;
  b: string;
  score: number;
  cooccur: number;
}

export interface Stats {
  generated_at: string;
  title: string;
  corpus: {
    name: string;
    poem_count: number;
    total_characters: number;
    date_range: { min: number | null; max: number | null };
    note: string;
  };
  imagery_word_count: number;
  top_words: { word: string; frequency: number; poem_count: number }[];
  methodology: {
    tokenizer: string;
    cooccurrence: string;
    timeline: string;
    excerpt: string;
  };
}

export interface AtlasData {
  stats: Stats;
  imagery: ImageryNode[];
  cooccurrence: Edge[];
  poems: Poem[];
}
