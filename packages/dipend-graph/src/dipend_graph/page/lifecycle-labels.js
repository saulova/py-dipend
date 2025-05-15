export function lifecycleLabels(svg, types_data) {
  const legendGroup = svg
    .append("g")
    .attr("class", "legend")
    .attr("transform", `translate(20, 50)`);
  const legend = legendGroup
    .selectAll("g")
    .data(types_data)
    .enter()
    .append("g")
    .attr("transform", (d, i) => `translate(0, ${i * 20})`);

  legend
    .append("rect")
    .attr("width", 15)
    .attr("height", 15)
    .attr("fill", (d) => d.color);
  legend
    .append("text")
    .attr("x", 20)
    .attr("y", 12)
    .attr("font-size", "12px")
    .attr("font-family", "Arial")
    .text((d) => d.type);
}
