/*
 *  ClusterReport - Object constructor function
 *  @param _parentElement   -- HTML element in which to draw the visualization
 *  @param _data            -- array of data
 */

ClusterReport = function(_parentElement, _data) {
    this.$graphicContainer = $("#" + _parentElement);
    this.parentElement = _parentElement;
    this.data = _data;
    this.duration = 1000;

    this.initVis();
}
/*
 * Initialize visualization (static content, e.g. SVG area or axes)
 */
ClusterReport.prototype.initVis = function() {
    var vis = this;
    vis.margin = {
        top: 10,
        right: 10,
        bottom: 10,
        left: 10
    };

    if ($("#" + vis.parentElement).width() - vis.margin.right - vis.margin.left > 300) {
        vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    } else {
        vis.width = 300;
    }
    vis.height = 400 - vis.margin.top - vis.margin.bottom;

    // SVG drawing area
    vis.svg = d3.select("#" + vis.parentElement).append("svg")
        .attr("width", vis.width + vis.margin.left + vis.margin.right)
        .attr("height", vis.height + vis.margin.top + vis.margin.bottom)
        .append("g")
        .attr("transform", "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    vis.wrangleData();
}


ClusterReport.prototype.wrangleData = function() {
    var vis = this;
    vis.displayData = vis.data;
    vis.updateVis();
}

ClusterReport.prototype.updateVis = function() {
    var vis = this;
    vis.svg.append("text")
    .attr("class", "report")
    .text(vis.displayData)
}
