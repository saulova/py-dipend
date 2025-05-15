export function drawNodes(nodes_data, graph, types_data, simulation) {
  const typeColorMap = {};
  types_data.forEach((type) => {
    typeColorMap[type.type] = type.color;
  });

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.01).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  const nodes = graph
    .append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(nodes_data)
    .enter()
    .append("circle")
    .attr("r", 10)
    .attr("fill", (d) => typeColorMap[d.type] || "#ccc")
    .call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended),
    );

  const labels = graph
    .append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(nodes_data)
    .enter()
    .append("text")
    .attr("dy", -15)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .attr("font-weight", "bold")
    .attr("font-family", "Arial")
    .text((d) => d.node);

  return [nodes, labels];
}
