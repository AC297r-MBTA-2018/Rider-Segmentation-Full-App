// Driver to initialize the loading page
var colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"]; // alternatively colorbrewer.YlGnBu[9]
var colors2 = ["#edf8b1", "#7fcdbb","#225ea8","#081d58"]; // alternatively colorbrewer.YlGnBu[9]
var colors3 = ["#7fcdbb"]
var temporal_data;
var geographical_data;
var clusters;

// make chart names global
var timePatternVis;
var purchasVis;
var basicDemographicsVis;
var geoPatternVis = null;
var pathPrefix = "http://0.0.0.0:5000"
if (window.location.href === (pathPrefix + "/")||window.location.href === (pathPrefix + "/dashboard" )) {
    queue()
        .defer(d3.json, "/initialize_data")
        .await(createVis);
}

function createVis(error, jsonData) {
    if (error) { console.log(error); };
    if (!error) {
        console.log("this is from initial view");
        // get the clusters into an array
        clusters = Object.keys(jsonData).map(function(key) {return jsonData[key];});
        console.log("data:")
        console.log(clusters);
        // get different types of patterns
        temporal_data = clusters.map(function(d){return d.temporal_patterns;});
        geographical_data = clusters.map(function(d){return d.geographical_patterns;});
        usertype_data = clusters.map(function(d){return d.usertype;});
        tariff_data = clusters.map(function(d){return d.tariff;});
        servicebrand_data = clusters.map(function(d){return d.servicebrand;});

        // get cluster info
        clust_info_data = clusters.map(function(d){return d.clust_info;});
        viz_data = clusters.map(function(d){return d.viz;});

        // get all demographics info
        race_data = clusters.map(function(d){return d.race;});
        edu_data = clusters.map(function(d){return d.edu;});
        income_data = clusters.map(function(d){return d.income;});

        // report

        // report_data = clusters.map(function(d){return d.report});
        // $("#description-chart").text(report_data);

        // Graph
        clusterpcaVis = new ClusterPCAVis("pca-chart", viz_data, colors2);
        clusterstatVis = new ClusterSimpleStatVis("simple-stat-chart", "simple-stat-data-selection", clust_info_data, colors3);
        timePatternVis = new TemporalPatternChart("temporal-chart", temporal_data, ["Overview"], temporal_data.length, colors)
        timeLegend = new TemporalLegend("temporal-legend", temporal_data, colors);
        geoPatternVis = new BostonMap("geographical-chart", geographical_data, 0, colors);
        purchaseVis = new GroupDistributionChart("purchase-chart", "purchase_chart-selector", "purchase_view-selector",
                            [usertype_data, tariff_data, servicebrand_data], ["User Type", "Tariff Type", "Servicebrand"], 3, 0, colors);
        basicDemographicsVis = new GroupDistributionChart("basic_demographics-chart", "basic_demographics_chart-selector",
                        "basic_demographics_view-selector", [race_data, edu_data, income_data],
                        ["Race", "Education", "Income"], 3, 0, colors);
    }
};
