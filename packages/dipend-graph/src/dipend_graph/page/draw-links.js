export function drawLinks(links_data, graph) {
  graph
    .append("defs")
    .append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 20)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("stroke-opacity", 0.7)
    .attr("fill", "#555");

  const links = graph
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links_data)
    .enter()
    .append("line")
    .attr("stroke", "#555")
    .attr("stroke-opacity", 0.7)
    .attr("stroke-width", 1.5)
    .attr("marker-end", "url(#arrowhead)");

  return links;
}
