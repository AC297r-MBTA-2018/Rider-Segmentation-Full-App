/*
 *  Heatmap - Object constructor function
 *  @param _parentElement   -- HTML element in which to draw the visualization
 *  @param _data            -- array of data
 *  @param _colors          -- array of colors
 *  @param _maxSaturation   -- maximum color saturation on the color scale
 *  @param _showLegend      -- whether to show legend (boolean)
 */

HourlyHeatmap = function(_parentElement, _data, _titleText, _colors, _maxSaturation){
    this.$graphicContainer = $("#" + _parentElement);
    this.parentElement = _parentElement;
    this.data = _data;
    this.titleText = _titleText;
    this.days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"];
    // this.hours = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];
    this.hours = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"];
    this.colors = _colors;
    this.buckets = _colors.length;
    this.maxSaturation = _maxSaturation;
    this.duration = 1000;

    this.initVis();
}

/*
 * Initialize visualization (static content, e.g. SVG area or axes)
 */
HourlyHeatmap.prototype.initVis = function() {
    var vis = this;
    vis.margin = { top: 50, right: 30, bottom: 70, left: 30 };

    vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    if (vis.width < 355){
        vis.width = 355;
    }
    vis.gridSize = Math.floor(vis.width / 24);
    vis.height = vis.gridSize * (vis.days.length+4) - vis.margin.top - vis.margin.bottom;
    vis.legendElementWidth = vis.gridSize*2;
    vis.fontSize = vis.width * 62.5 / 900;

    // SVG drawing area
    vis.svg = d3.select("#" + vis.parentElement).append("svg")
        .attr("width", vis.width + vis.margin.left + vis.margin.right)
        .attr("height", vis.height + vis.margin.top + vis.margin.bottom)
        .append("g")
        .attr("transform", "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    vis.colorScale = d3.scaleLinear()
        .range(vis.colors);

    // Label the y-axis with days
    vis.dayLabels = vis.svg.selectAll(".dayLabel")
    .data(vis.days)
    .enter().append("text")
        .text(function (d) { return d; })
        .attr("x", 0)
        .attr("y", function (d, i) { return i * vis.gridSize; })
        .style("text-anchor", "end")
        .attr("transform", "translate(-6," + vis.gridSize / 1.5 + ")")
        .attr("class", function (d, i) { return ((i >= 0 && i <= 4) ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis"); });

    // Label the x-axis with times
    vis.hourLabels = vis.svg.selectAll(".hourLabel")
    .data(vis.hours)
    .enter().append("text")
    .text(function(d) { return d; })
    .attr("x", function(d, i) { return i * vis.gridSize; })
    .attr("y", 0)
    .style("text-anchor", "middle")
    .attr("transform", "translate(" + vis.gridSize / 2 + ", -6)")
    .attr("class", function(d, i) { return ((i >= 7 && i <= 16) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"); });

    //Create title
    vis.svg.append("text")
    .attr("x", 0)
    .attr("y",  -20)
    .attr("class", "heatMapTitle")
    .style("text-anchor", "middle")
    .text(vis.titleText);


    vis.wrangleData();

    // Listen to events
}

/*
 * Data wrangling
 */
HourlyHeatmap.prototype.wrangleData = function() {
    var vis = this;
    // Update the visualization
    vis.updateVis();
}

/*
 * The drawing function
 */
HourlyHeatmap.prototype.updateVis = function() {
    var vis = this;

    // Update color scale
    vis.colorScale.domain(d3.range(0, vis.maxSaturation, vis.maxSaturation/vis.buckets));

    vis.cards = vis.svg.selectAll(".hour")
		.data(vis.data, function(d) {return d.day+':'+d.hour;});

	vis.cards.append("title");

	vis.cards.enter().append("rect")
		.attr("x", function(d) { return (d.hour - 1) * vis.gridSize; })
		.attr("y", function(d) { return (d.day - 1) * vis.gridSize; })
		.attr("rx", 3)
		.attr("ry", 3)
		.attr("class", "hour bordered")
		.attr("width", vis.gridSize)
		.attr("height", vis.gridSize)
        .style("fill", vis.colors[0])

        .merge(vis.cards)
        .transition().duration(vis.duration)
        .attr("x", function(d) { return (d.hour - 1) * vis.gridSize; })
		.attr("y", function(d) { return (d.day - 1) * vis.gridSize; })
		.attr("rx", 4)
		.attr("ry", 4)
		.attr("class", "hour bordered")
		.attr("width", vis.gridSize)
		.attr("height", vis.gridSize)
        .style("fill", function(d) { return vis.colorScale(d.value); });

	vis.cards.select("title").text(function(d) { return d.value; });

    vis.cards.exit().remove();
}
