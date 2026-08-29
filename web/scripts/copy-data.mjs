// Copy the generated dataset from ../data into public/data so the static
// build ships with it. Run automatically before `dev` and `build`.
import { cpSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const src = resolve(root, "..", "data");
const dst = resolve(root, "public", "data");

mkdirSync(dst, { recursive: true });
for (const name of ["stats.json", "imagery.json", "cooccurrence.json", "poems.json"]) {
  cpSync(resolve(src, name), resolve(dst, name));
  console.log(`copied data/${name} -> web/public/data/${name}`);
}
