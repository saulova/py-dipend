export function logo(svg) {
  const logoGroup = svg.append("g").attr("class", "logo").attr("transform", `translate(0, 20)`);
  const logo = logoGroup
    .selectAll("g")
    .data([{ logo: "Dipend Graph" }])
    .enter()
    .append("g")
    .attr("transform", "translate(0, 0)");

  logo
    .append("text")
    .attr("x", 20)
    .attr("y", 12)
    .attr("font-size", "12px")
    .attr("font-weight", "bold")
    .attr("font-family", "Arial")
    .text((d) => d.logo);
}
