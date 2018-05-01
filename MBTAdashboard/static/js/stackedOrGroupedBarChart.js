/*
 * StackedORGroupedBarChart         -- Object constructor function
 * @param _parentElement 	        -- the HTML element in which to draw the visualization
 * @param _selectorParentElement 	-- the HTML element in which to draw the view selector
 * @param _data			          	-- array of data
 * @param _titleText               -- chart title
 * @param _colors                   -- range of colors for color scale
 * @param _view                     -- whether viewing by cluster
 */

StackedORGroupedBarChart = function(_parentElement, _selectorParentElement, _data, _titleText, _colors, _view = false) {
    this.parentElement = _parentElement;
    this.selectorParentElement = _selectorParentElement;
    this.data = _data; // an array of data each item is one donut chart
    this.titleText = _titleText; // an array of string for each donut chart
    this.colors = _colors;
    this.prefix = _parentElement.split("-")[0];
    this.selectorPrefix = _selectorParentElement.split("-")[0];
    this.$graphicContainer = $("#" + _parentElement);
    this.view = _view;

    this.initVis();
}

StackedORGroupedBarChart.prototype.initVis = function() {
    var vis = this;
    vis.formatFloat = d3.format(",.2f");
    vis.margin = {
        top: 40,
        right: 10,
        bottom: 20,
        left: 10
    };
    if ($("#" + vis.parentElement).width() - vis.margin.right - vis.margin.left > 200) {
        vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    } else {
        vis.width = 200;
    }
    vis.height = 400 - vis.margin.top - vis.margin.bottom;

    // separate groups and values (e.g. races and respective percentages)
    vis.groups = [];
    for (var key in vis.data[0]) {
        vis.groups.push(key);
    };

    // list of clusters
    vis.clusters = [];
    if (vis.view) {
        vis.data.forEach(function(d, i) {
            var clusterStr = "cluster " + i;
            vis.clusters.push(clusterStr);
        });
    } else {
        vis.clusters.push("Overview");
    }

    vis.nGroup = vis.groups.length; // number of layers
    vis.nCluster = vis.clusters.length; // number of samples per layer
    vis.stack = d3.stack().keys(vis.groups);

    // scales
    vis.x = d3.scaleBand()
        .rangeRound([0, vis.width * 6 / 8])
        .padding(0.08);

    vis.y = d3.scaleLinear()
        .range([vis.height, 0]);
    vis.z = d3.scaleBand().rangeRound([0, vis.x.bandwidth()]);
    vis.color = d3.scaleOrdinal()
        .range(vis.colors);

    // SVG drawing area
    vis.svg = d3.select("#" + vis.parentElement).append("svg")
        .attr("width", vis.width + vis.margin.left + vis.margin.right)
        .attr("height", vis.height + vis.margin.top + vis.margin.bottom)
        .append("g")
        .attr("transform", "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    // append title
    vis.svg.append("text")
        .attr("x", vis.x.bandwidth() / 2)
        .attr("y", -10)
        .attr("class", "stackedChartTitle")
        .style("text-anchor", "middle")
        .text(vis.titleText);

    // Prep the tooltip bits, initial display is hidden
    // vis.tooltip = d3.tip()
    //     .attr("class", "d3-tip")
    //     .offset([0, 0]);

    // Prep the tooltip bits, initial display is hidden
    vis.tooltip = d3.select("#" + vis.parentElement).append("div")
        .attr("class", "tooltip")
        .style("opacity", "0");
    // vis.tooltip = vis.svg.append("g")
    //     .attr("class", "tooltip")
    //     .style("display", "none");

    vis.wrangleData();

    // Listen to view change events
    $('#' + vis.selectorParentElement + ' div input').click(function() {
        vis.selection = d3.select(this).property("value");
        if (vis.selection === "stacked") {
            vis.transitionStacked();
        } else {
            vis.transitionGrouped();
        }
    });
}

StackedORGroupedBarChart.prototype.wrangleData = function() {
    var vis = this;
    vis.displayData = vis.data;

    // console.log(vis.displayData);
    vis.layers = vis.stack(vis.displayData); // calculate the stack layout

    vis.layers.forEach(function(d, i) { //adding keys to every datapoint
        d.forEach(function(dd, j) {
            dd.cluster = vis.clusters[j];
            dd.group = vis.groups[i];
        })
    });
    vis.yGroupMax = d3.max(vis.layers, function(layer) {
        return d3.max(layer, function(d) {
            return d[1] - d[0];
        });
    });
    vis.yStackMax = d3.max(vis.layers, function(layer) {
        return d3.max(layer, function(d) {
            return d[1];
        });
    });

    vis.updateVis();
}

StackedORGroupedBarChart.prototype.updateVis = function() {
    var vis = this;

    // scale domains
    vis.x.domain(vis.clusters);
    vis.y.domain([0, vis.yStackMax]);
    vis.z.domain(vis.groups);
    // vis.color.domain([0, vis.nGroup - 1])

    vis.layer = vis.svg.selectAll(".layer")
        .data(vis.layers)
        .enter().append("g")
        .attr("class", "layer")
        .style("fill", function(d, i) {
            return vis.color(i);
        });

    vis.rect = vis.layer.selectAll("rect")
        .data(function(d) {
            return d;
        })
        .enter().append("rect")
        .attr("x", function(d) {
            return vis.x(d.cluster);
        })
        .attr("y", vis.height)
        .attr("width", vis.x.bandwidth())
        .attr("height", 0)
        .on("mouseover", function(d) {
        var xPosition = d3.mouse(this)[0];
        var yPosition = d3.mouse(this)[1];
        vis.tooltip.transition()
            .duration(200)
            .style("opacity", 1.0);
        vis.tooltip .html(d.c + ":" +"</br>"+ Math.round(d3.round(d.y, -2)) + " (DALYs)")   //Math.round(d3.round(d.y, -6))
            .style("left", xPosition + "px")
            .style("top", (yPosition - 20) + "px")
            //.style("border-color", colors[colors.length-1-i] )
      }).on("mousemove", function(d) {
        var xPosition = d3.mouse(this)[0];
        var yPosition = d3.mouse(this)[1];
        vis.tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");
        vis.tooltip .html(d.c + ":" +"</br>"+ Math.round(d3.round(d.y, -2)) + " (DALYs)") //Math.round(d3.round(d.y, -6))
            .style("left", (xPosition - 35) + "px")  
            .style("top", (yPosition - 35) + "px")
            //.style("border-color", colors[colors.length-1-i] ) possible to set colors based on mouseover box?
            .attr("transform", "translate(" + xPosition + "," + yPosition + ")");
      })
      .on("mouseout", function(d) {
            vis.tooltip.transition()
                .duration(500)
                .style("opacity", 0);
      });
        // .on("mouseover", vis.mouseover())
        // .on("mousemove", function(d) {
        //     vis.mousemove(d)
        // })
        // .on("mouseout", vis.mouseout());;

    vis.rect.transition()
        .delay(function(d, i) {
            return i * 10;
        })
        .attr("y", function(d) {
            return vis.y(d[1]);
        })
        .attr("height", function(d) {
            return vis.y(d[0]) - vis.y(d[1]);
        });

    vis.svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + vis.height + ")")
        .call(d3.axisBottom(vis.x).tickSizeOuter(0));

    vis.legend = vis.svg.selectAll(".legend")
        .data(vis.groups)
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) {
            return "translate(0," + i * 20 + ")";
        });

    vis.legend.append("rect")
        .attr("x", vis.width - 18)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", function(d, i) {
            return vis.color(i)
        });

    vis.legend.append("text")
        .attr("x", vis.width - 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) {
            return d;
        });
}

StackedORGroupedBarChart.prototype.transitionGrouped = function() {
    var vis = this;
    vis.y.domain([0, vis.yGroupMax]);
    vis.z.rangeRound([0, vis.x.bandwidth()]);

    vis.rect.transition()
        .duration(500)
        .delay(function(d, i) {
            return i * 10;
        })
        .attr("x", function(d) {
            return vis.x(d.cluster) + vis.z(d.group);
        })
        .attr("width", vis.x.bandwidth() / vis.nGroup)
        .transition()
        .attr("y", function(d) {
            return vis.y(d.data[d.group]);
        })
        .attr("height", function(d) {
            return vis.height - vis.y(d.data[d.group]);
        });
}
StackedORGroupedBarChart.prototype.transitionStacked = function() {
    var vis = this;
    vis.y.domain([0, vis.yStackMax]);

    vis.rect.transition()
        .duration(500)
        .delay(function(d, i) {
            return i * 10;
        })
        .attr("y", function(d) {
            return vis.y(d[1]);
        })
        .attr("height", function(d) {
            return vis.y(d[0]) - vis.y(d[1]);
        })
        .transition()
        .attr("x", function(d) {
            return vis.x(d.cluster);
        })
        .attr("width", vis.x.bandwidth());
}
StackedORGroupedBarChart.prototype.mouseover = function() {
    var vis = this;
    vis.tooltip.style("display", "inline");
}
StackedORGroupedBarChart.prototype.mousemove = function(d) {
    var vis = this;
    // console.log(d.group + ": " + vis.formatFloat(d[1] - d[0]) + "%");
    // console.log(vis.tooltip);
    vis.tooltip.text(d.group + ":  " + vis.formatFloat(d[1] - d[0]) + "%")
        .style("display", "inline")
        .style("left", (d3.event.pageX - 34) + "px")
        .style("top", (d3.event.pageY - 12) + "px");
}
StackedORGroupedBarChart.prototype.mouseout = function(d) {
    var vis = this;
    vis.tooltip.style("display", "none");
}
