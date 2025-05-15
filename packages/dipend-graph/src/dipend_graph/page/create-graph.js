import { fetchData } from "./fetch-data.js";
import { createSVG } from "./create-svg.js";
import { logo } from "./logo.js";
import { lifecycleLabels } from "./lifecycle-labels.js";
import { drawNodes } from "./draw-nodes.js";
import { drawLinks } from "./draw-links.js";

export async function createGraph() {
  const data = await fetchData();
  if (!data) return;

  const { nodes: nodes_data, links: links_data, types: types_data } = data;
  const width = window.innerWidth;
  const height = window.innerHeight;
  const [svg, graph] = createSVG(width, height);

  const simulation = d3
    .forceSimulation(nodes_data)
    .force(
      "link",
      d3
        .forceLink(links_data)
        .id((d) => d.node)
        .distance(100),
    )
    .force("charge", d3.forceManyBody().strength(-150))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const links = drawLinks(links_data, graph);
  const [nodes, labels] = drawNodes(nodes_data, graph, types_data, simulation);

  logo(svg);
  lifecycleLabels(svg, types_data);

  simulation.on("tick", () => {
    links
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);
    nodes.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
    labels.attr("x", (d) => d.x).attr("y", (d) => d.y);
  });
}
