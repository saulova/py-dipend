export function createSVG(width, height) {
  const svg = d3
    .select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height);
  const graph = svg.append("g");

  const zoom = d3
    .zoom()
    .scaleExtent([0.5, 5])
    .on("zoom", (event) => {
      graph.attr("transform", event.transform);
    });

  svg.call(zoom);

  svg.on("mousedown", function (event) {
    if (event.button === 1) {
      event.preventDefault();
    }
  });

  return [svg, graph];
}
