import { createGraph } from "./create-graph.js";

createGraph();

window.addEventListener("resize", () => {
  d3.select("svg").remove();
  createGraph();
});
