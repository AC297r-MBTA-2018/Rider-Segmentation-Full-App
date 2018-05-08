/*
 *  TemporalLegend - Object constructor function
 *  @param _parentElement   -- HTML element in which to draw the visualization
 *  @param _data            -- array of data
 *  @param _colors          -- array of colors
 */

TemporalLegend = function(_parentElement, _data, _colors) {

    this.$graphicContainer = $("#" + _parentElement);
    this.parentElement = _parentElement;
    this.data = _data;
    this.days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"];
    this.hours = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"];
    this.colors = _colors;
    this.buckets = _colors.length;
    this.maxSaturation = d3.max(this.data.map(function(d) {
        return d3.max(d, function(e) {
            return e.value;
        });
    }));
    this.duration = 1000;

    this.initVis();
}

/*
 * Initialize visualization (static content, e.g. SVG area or axes)
 */
TemporalLegend.prototype.initVis = function() {
    var vis = this;
    vis.margin = { top: 0, right: 30, bottom: 0, left: 30 };

    vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    if (vis.width < 355){
        vis.width = 355;
    }
    vis.gridSize = Math.floor(vis.width / 24);
    vis.height = 30 - vis.margin.top - vis.margin.bottom;
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

    vis.wrangleData();
}

TemporalLegend.prototype.wrangleData = function() {
    var vis = this;
    vis.updateVis();
}

TemporalLegend.prototype.updateVis = function() {
    var vis = this;
    // Update color scale
    vis.colorScale.domain(d3.range(0, vis.maxSaturation, vis.maxSaturation/vis.buckets));
    ///////////////////////////////////////////////////////////////////////////
    //////////////// Create the gradient for the legend ///////////////////////
    ///////////////////////////////////////////////////////////////////////////
    //Extra scale since the color scale is interpolated
    vis.countScale = d3.scaleLinear()
            .domain([0, vis.maxSaturation])
            .range([0, vis.width]);

    //Calculate the variables for the temp gradient
    vis.legendNumStops = 10;
    vis.countRange = vis.countScale.domain();
    vis.countRange[2] = vis.countRange[1] - vis.countRange[0];
    vis.countPoint = [];
    for(var i = 0; i < vis.legendNumStops; i++) {
        vis.countPoint.push(i * vis.countRange[2]/(vis.legendNumStops-1) + vis.countRange[0]);
    }//for i

    //Create the gradient
    vis.svg.append("defs")
        .append("linearGradient")
        .attr("id", "legend-temporal")
        .attr("x1", "0%").attr("y1", "0%")
        .attr("x2", "100%").attr("y2", "0%")
        .selectAll("stop")
        .data(d3.range(vis.legendNumStops))
        .enter().append("stop")
        .attr("offset", function(d,i) {
            return vis.countScale( vis.countPoint[i] )/vis.width;
        })
        .attr("stop-color", function(d,i) {
            return vis.colorScale( vis.countPoint[i] );
        });

    ///////////////////////////////////////////////////////////////////////////
    ////////////////////////// Draw the legend ////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////

    vis.legendWidth = Math.min(vis.width*0.8, 400);
    //Color Legend container
    vis.legendsvg = vis.svg.append("g")
        .attr("class", "legendWrapper")
        .attr("transform", "translate(" + (vis.width/2) + "," + 0 + ")");

    //Draw the Rectangle
    vis.legendsvg.append("rect")
        .attr("class", "legendRect")
        .attr("x", -vis.legendWidth/2)
        .attr("y", 0)
        //.attr("rx", hexRadius*1.25/2)
        .attr("width", vis.legendWidth)
        .attr("height", 10)
        .style("fill", "url(#legend-temporal)");

    //Append title
    vis.legendsvg.append("text")
        .attr("class", "legendTitle")
        .attr("x", -255)
        .attr("y", 13)
        .style("text-anchor", "middle")
        .text("% of Traffic");

    //Set scale for x-axis
    vis.xScale = d3.scaleLinear()
        .range([-vis.legendWidth/2, vis.legendWidth/2])
        .domain([ 0, vis.maxSaturation] );

    //Define x-axis
    vis.xAxis =  d3.axisBottom()
        .scale(vis.xScale)
        .ticks(5);

    //Set up X axis
    vis.legendsvg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + (10) + ")")
        .call(vis.xAxis);
}
