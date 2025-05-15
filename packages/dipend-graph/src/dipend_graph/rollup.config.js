import fs from "fs";

import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import terser from "@rollup/plugin-terser";

const production = !process.env.ROLLUP_WATCH;

function copyFile(files = []) {
  return {
    name: "copy-file",
    async buildStart() {
      files.forEach((file) => this.addWatchFile(file.inputFile));
    },
    async generateBundle() {
      files.forEach((file) =>
        this.emitFile({
          type: "asset",
          fileName: file.outputFile,
          source: fs.readFileSync(file.inputFile),
        }),
      );
    },
  };
}

export default {
  input: "page/main.js",
  output: {
    file: "public/page.js",
    format: "iife",
    sourcemap: !production,
  },
  plugins: [
    copyFile([{ inputFile: "page/index.html", outputFile: "index.html" }]),
    resolve(),
    commonjs(),
    production && terser(),
  ],
};
