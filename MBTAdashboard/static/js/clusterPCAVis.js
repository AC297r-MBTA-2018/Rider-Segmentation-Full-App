/*
 *  ClusterPCAVis - Object constructor function
 *  @param _parentElement   -- HTML element in which to draw the visualization
 *  @param _data            -- array of data
 *  @param _colors          -- array of colors
 *  @param _view            -- whether viewing by cluster
 */

ClusterPCAVis = function(_parentElement, _data, _colors, _view = false){
    this.$graphicContainer = $("#" + _parentElement);
    this.parentElement = _parentElement;
    this.data = _data;
    this.colors = _colors;
    this.buckets = _colors.length;
    this.duration = 1000;
    this.view = _view; // false = overview; true = by_cluster

    this.initVis();
}

/*
 * Initialize visualization (static content, e.g. SVG area or axes)
 */
ClusterPCAVis.prototype.initVis = function() {
    var vis = this;
    // console.log(vis.data);
    vis.margin = { top: 50, right: 30, bottom: 20, left: 30 };

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

    // Scales
	vis.xScale = d3.scaleLinear()
		.range([0, vis.width]);

	vis.yScale = d3.scaleLinear()
		.range([vis.height, 0]);

	vis.xAxis = d3.axisBottom()
		.scale(vis.xScale);

	vis.yAxis = d3.axisLeft()
		.scale(vis.yScale);

    vis.colorScale = d3.scaleOrdinal()
        .range(vis.colors);

    //Create title
    vis.svg.append("text")
    .attr("x", vis.width/2)
    .attr("y",  -20)
    .attr("class", "pcaVisTitle")
    .style("text-anchor", "middle")
    .text("Visualizing in PCA Subspace");

    // Prep the tooltip bits, initial display is hidden
    vis.tooltip = d3.select("#" + vis.parentElement).append("div")
        .attr("class", "tooltip")
        .style("opacity", "0");

    vis.wrangleData();
}

/*
 * Wrangle data
 */
ClusterPCAVis.prototype.wrangleData = function() {
    var vis = this;
    vis.displayData = vis.data;
    vis.updateVis();
}

/*
 * Wrangle data
 */
ClusterPCAVis.prototype.updateVis = function() {
    var vis = this;
    // update scale domain
    vis.xScale.domain([d3.min(vis.displayData, function(d){
		return d.pca1;
	})-5, d3.max(vis.displayData, function(d){
		return d.pca1;
	})+5]).nice();

	vis.yScale.domain([d3.min(vis.displayData, function(d){
		return d.pca1;
	})-5, d3.max(vis.displayData, function(d){
		return d.pca1;
	})+5]).nice();

    if (vis.view){
        // square root scale.
        vis.radius = d3.scaleSqrt()
            .range([5,30]);
    }
    else{
        vis.radius = d3.scaleSqrt()
            .range([50,60]);
    }

	vis.radius.domain([d3.min(vis.displayData, function(d){
		return d.size;
	})-5, d3.max(vis.displayData, function(d){
		return d.size;
	})+5]).nice();

    // Update axes
	vis.svg.append('g')
		.attr('transform', 'translate(0,' + vis.height + ')')
		.attr('class', 'x axis')
		.call(vis.xAxis);

	// y-axis is translated to (0,0)
	vis.svg.append('g')
		.attr('transform', 'translate(0,0)')
		.attr('class', 'y axis')
		.call(vis.yAxis);

    // update bubbles
    vis.bubble = vis.svg.selectAll('.bubble')
    .data(vis.displayData)
    .enter().append('circle')
    .attr('class', 'bubble')
    .attr('cx', function(d){return vis.xScale(d.pca1);})
    .attr('cy', function(d){ return vis.yScale(d.pca2); })
    .attr('r', function(d){ return vis.radius(d.size); })
    .style('fill', function(d){ return vis.colorScale(d.grp); })
    .style('opacity', 0.65)
    .on("mouseover", function(d, i) {
    var xPosition = d3.mouse(this)[0];
    var yPosition = d3.mouse(this)[1];
    vis.tooltip.transition()
        .duration(200)
        .style("opacity", 1.0);
    vis.tooltip.html("Cluster " + i)
        .style("left", xPosition + "px")
        .style("top", (yPosition) + "px")
  }).on("mousemove", function(d, i) {
    var xPosition = d3.mouse(this)[0];
    var yPosition = d3.mouse(this)[1];
    vis.tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");

    vis.tooltip.html("Cluster " + i)
        .style("left", (xPosition) + "px")
        .style("top", (yPosition) + "px")
        .attr("transform", "translate(" + xPosition + "," + yPosition + ")");
  })
  .on("mouseout", function(d) {
        vis.tooltip.transition()
            .duration(500)
            .style("opacity", 0);
  });

    vis.bubble.append('title')
        .attr('x', function(d){ return vis.radius(d.size); })
        .text(function(d){
            return d.grp;
        });

    // adding label. For x-axis, it's at (10, 10), and for y-axis at (width, height-10).
    vis.svg.append('text')
        .attr('x', 10)
        .attr('y', 10)
        .attr('class', 'label')
        .text('PCA 2');


    vis.svg.append('text')
        .attr('x', vis.width)
        .attr('y', vis.height - 10)
        .attr('class', 'label')
        .style('text-anchor', 'end')
        .text('PCA 1');

    vis.legend = vis.svg.selectAll('legend')
    			.data(vis.colorScale.domain())
    			.enter().append('g')
    			.attr('class', 'legend')
    			.attr('transform', function(d,i){ return 'translate(0,' + i * 20 + ')'; });

	// give x value equal to the legend elements.
	// no need to define a function for fill, this is automatically fill by color.
	vis.legend.append('rect')
		.attr('x', vis.width)
		.attr('width', 18)
		.attr('height', 18)
		.style('fill', vis.colorScale);

	// add text to the legend elements.
	// rects are defined at x value equal to width, we define text at width - 6, this will print name of the legends before the rects.
	vis.legend.append('text')
		.attr('x', vis.width - 6)
		.attr('y', 9)
		.attr('dy', '.35em')
		.style('text-anchor', 'end')
        .style('font-size', '14px')
		.text(function(d){
        if (d === 0){
            return 'overview';
        }
        else if (d === 1){
            return '<20 trips/month group';
        }
        else if (d === 2){
            return '>20 trips/month group';
        }
        else {
            return 'others'
        }
    });
}
