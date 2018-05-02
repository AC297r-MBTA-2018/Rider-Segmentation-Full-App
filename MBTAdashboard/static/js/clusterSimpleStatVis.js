/*
 *  ClusterSimpleStatVis - Object constructor function
 *  @param _parentElement   -- HTML element in which to draw the visualization
 *  @param _data            -- array of data
 *  @param _colors          -- array of colors
 *  @param _view            -- whether viewing by cluster
 */

ClusterSimpleStatVis = function(_parentElement, _selectorParentElement, _data, _colors, _view = false) {
    this.$graphicContainer = $("#" + _parentElement);
    this.parentElement = _parentElement;
    this.selectorParentElement = _selectorParentElement;
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
ClusterSimpleStatVis.prototype.initVis = function() {
    var vis = this;
    vis.appendDataSelector();
    vis.formatFloat = d3.format(",.2f");
    vis.margin = {
        top: 50,
        right: 30,
        bottom: 50,
        left: 70
    };

    if ($("#" + vis.parentElement).width() - vis.margin.right - vis.margin.left > 300) {
        vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    } else {
        vis.width = 300;
    }
    vis.height = 363 - vis.margin.top - vis.margin.bottom;

    // SVG drawing area
    vis.svg = d3.select("#" + vis.parentElement).append("svg")
        .attr("width", vis.width + vis.margin.left + vis.margin.right)
        .attr("height", vis.height + vis.margin.top + vis.margin.bottom)
        .append("g")
        .attr("transform", "translate(" + vis.margin.left + "," + vis.margin.top + ")");

    vis.x = d3.scaleBand()
        .range([0, vis.width], .1);

    vis.y = d3.scaleLinear()
        .range([vis.height, 0]);

    vis.xAxislabel = vis.svg.append("text")
        .attr("class", "x-axis-label")
        .attr("x", (vis.width/2 - 20))
        .attr("y", (vis.height + 40));

    vis.yAxislabel = vis.svg.append("text")
    .attr('x', 20)
    .attr('y', -10)
    .attr("class", "y-axis-label")
        .style("text-anchor", "end");

    vis.xAxis = d3.axisBottom(vis.x);

    vis.svg.append("g")
        .attr("class", "x axis x-axis")
        .attr("transform", "translate(0," + vis.height + ")")

    vis.yAxis = d3.axisLeft(vis.y);

    vis.yAxisShow = vis.svg.append("g")
        .attr("class", "y axis y-axis")

    vis.selection = 'Size'; // initial selection is to show cluster size

    // Prep the tooltip bits, initial display is hidden
    vis.tooltip = d3.select("#" + vis.parentElement).append("div")
        .attr("class", "tooltip")
        .style("opacity", "0");

    vis.wrangleData();

    // Listen to view change events
    $('#' + vis.selectorParentElement + ' div input').click(function() {
        vis.selection = d3.select(this).property("value");
        vis.wrangleData();
    });
}

ClusterSimpleStatVis.prototype.wrangleData = function() {
    var vis = this;
    vis.displayData = vis.data.map(function(d) {
        return d[vis.selection];
    });
    vis.updateVis();
}

ClusterSimpleStatVis.prototype.updateVis = function() {
    var vis = this;

    vis.x.domain(vis.displayData.map(function(d, i) {
            return i;
        }))
        .paddingInner(0.1)
        .paddingOuter(0.5);

    vis.y.domain([0, d3.max(vis.displayData, function(d) {
        return d;
    })]);

    //Create title
    vis.svg.select(".x-axis-label")
        .text("Cluster");

    vis.svg.select(".y-axis-label")
        .text(function(){
            if (vis.selection === "Size"){
                return "# of Riders";
            }
            else {
                return "Avg # Trips"
            }
        });

    vis.bars = vis.svg.selectAll(".bar")
        .data(vis.displayData);

    vis.bars.enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d, i) {
            return vis.x(i);
        })
        .attr("width", vis.x.bandwidth())
        .attr("y", function(d) {
            return vis.y(d);
        })
        .attr("height", function(d) {
            return vis.height - vis.y(d);
        })
        .style('fill', vis.colors)
        .style('opacity', 0.8)
        .on("mouseover", function(d) {
            var xPosition = d3.mouse(this)[0];
            var yPosition = d3.mouse(this)[1];
            vis.tooltip.transition()
                .duration(200)
                .style("opacity", 1.0);
            vis.tooltip.html(function(e) {
                    if (vis.selection === 'Average # of Trips') {
                        return vis.selection + ":  " + vis.formatFloat(d);
                    } else {
                        return vis.selection + ":  " + d;
                    }
                })
                .style("left", xPosition + "px")
                .style("top", (yPosition) + "px")
        }).on("mousemove", function(d) {
            var xPosition = d3.mouse(this)[0];
            var yPosition = d3.mouse(this)[1];
            vis.tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");

            vis.tooltip.html(function(e) {
                    if (vis.selection === 'Average # of Trips') {
                        return vis.selection + ": " + vis.formatFloat(d);
                    } else {
                        return vis.selection + ":  " + d;
                    }
                })
                .style("left", (xPosition) + "px")
                .style("top", (yPosition) + "px")
                .attr("transform", "translate(" + xPosition + "," + yPosition + ")");
        })
        .on("mouseout", function(d) {
            vis.tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        })
        .merge(vis.bars)
        .transition().duration(vis.duration)
        .ease(d3.easeLinear)
        .attr("x", function(d, i) {
            return vis.x(i)
        })
        .attr("y", function(d) {
            return vis.y(d)
        })
        .attr("width", function(d) {
            return vis.x.bandwidth()
        })
        .attr("height", function(d) {
            return vis.height - vis.y(d);
        })
        .style('fill', vis.colors)
        .style('opacity', 0.8);

    vis.bars.exit().remove();

    // update the axis
    vis.svg.select(".x-axis")
        .transition()
        .duration(vis.duration / 3)
        .ease(d3.easeLinear)
        .call(vis.xAxis);

    vis.svg.select(".y-axis")
        .transition()
        .duration(vis.duration / 3)
        .ease(d3.easeLinear)
        .call(vis.yAxis)

    // vis.svg.select(".y-axis .axis-label")
    //     .append("text")
    //     .attr("class", "axis-label")
    //     .style("text-anchor", "end")
    //     .text(function() {
    //         if (vis.selection == "size") {
    //             return "# of People in Cluster";
    //         } else if (vis.selection == "avg_num_trips") {
    //             return "Avg # of Trips";
    //         }
    //     })
    //     .attr("fill", "#000")
    //     .attr("transform", "rotate(-90)")
    //     .attr("y", -70)
    //     .attr("x", 20)
    //     .attr("dy", "1em");

}

ClusterSimpleStatVis.prototype.appendDataSelector = function() {
    var vis = this;

    $("#" + vis.selectorParentElement).empty(); // clear out the selection div
    var p = document.getElementById(vis.selectorParentElement);

    // append selector
    var html_str =
        '<form class="form-inline" role="group" id="simple-stat-datatype-selector">' +
        '<label class="form-label p-2" for="simple-stat-datatype-selector">Data: </label>' +
        '<div class="form-check">' +
        '<input class="form-check-input" name="data" type="radio" id="simple-stat-cluster-size" value="Size" checked="checked"' +
        '<label class="form-check-label" for="simple-stat-cluster-size"> Cluster size </label>' +
        '</div>' +
        '<div class="form-check">' +
        '<input class="form-check-input ml-2" name="data" type="radio" id="simple-stat-avg-num-trips" value="Average # of Trips"' +
        '<label class="form-check-label" for="simple-stat-avg-num-trips"> Average # of trips </label>' +
        '</div>';
    html_str += '</form>';
    p.innerHTML = html_str;
}
