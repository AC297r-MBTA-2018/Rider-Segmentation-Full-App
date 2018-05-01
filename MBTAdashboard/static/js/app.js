// Default user interface controls
var USER_CONTROLS = {
    "START_MONTH": "1701",
    "DURATION": "1",
    "TIME_WEIGHT": "0",
    "ALGORITHM": "kmeans",
    "VIEW": "overview", // overview, hierarchical clusters or non-hierarchical clusters
}

// Construct url to receive csv data
var URL_BASE = "/reload_data";

// Return url to receive csv data
function update_url() {
    return URL_BASE +
        "?view=" + USER_CONTROLS.VIEW +
        "&start_month=" + USER_CONTROLS.START_MONTH +
        "&duration=" + USER_CONTROLS.DURATION +
        "&time_weight=" + USER_CONTROLS.TIME_WEIGHT +
        "&algorithm=" + USER_CONTROLS.ALGORITHM;
}

// Run pyscript
function run_pyscript(input) {
    $.ajax({
        type: "POST",
        url: update_url(),
        data: {
            param: input
        }, //use this to store what changed
        success: call_back
    });
}

function call_back(response) {
    // window.location.href = "/request_view";
    clusters = Object.keys(response).map(function(key) {
        return response[key];
    });
    console.log("this is call back");
    // get different types of patterns
    temporal_data = clusters.map(function(d) {
        return d.temporal_patterns;
    });
    geographical_data = clusters.map(function(d) {
        return d.geographical_patterns;
    });
    usertype_data = clusters.map(function(d) {
        return d.usertype;
    });
    tariff_data = clusters.map(function(d) {
        return d.tariff;
    });
    servicebrand_data = clusters.map(function(d) {
        return d.servicebrand;
    });

    // get cluster info
    clust_info_data = clusters.map(function(d) {
        return d.clust_info;
    });
    viz_data = clusters.map(function(d) {
        return d.viz;
    });
    // get all demographics info
    race_data = clusters.map(function(d) {
        return d.race;
    });
    // agesex_data = clusters.map(function(d) {
    //     return d.agesex;
    // });
    edu_data = clusters.map(function(d) {
        return d.edu;
    });
    income_data = clusters.map(function(d) {
        return d.income;
    });

    if (USER_CONTROLS.VIEW === 'overview') {
        USER_CONTROLS.VIEW_BY_CLUSTER = false;
    } else {
        USER_CONTROLS.VIEW_BY_CLUSTER = true;
    }

    $("#pca-chart").empty();
    clusterpcaVis = new ClusterPCAVis("pca-chart", viz_data, colors2, USER_CONTROLS.VIEW_BY_CLUSTER);
    $("#simple-stat-chart").empty();
    clusterstatVis = new ClusterSimpleStatVis("simple-stat-chart", "simple-stat-data-selection", clust_info_data, colors3, USER_CONTROLS.VIEW_BY_CLUSTER);
    // $("#description-chart").empty();
    // $("#description-chart").text(report_data);
    // update temporal pattern chart
    $("#temporal-chart").empty();
    timePatternVisTitleList = [];
    temporal_data.map(function(d, i) {
        timePatternVisTitleList.push("Cluster " + i);
    })
    timePatternVis = new TemporalPatternChart("temporal-chart", temporal_data, timePatternVisTitleList, temporal_data.length, colors)

    // update geographical pattern chart
    geoPatternVis.bostonMap.remove();
    geoPatternVis = new BostonMap("geographical-chart", geographical_data, 0, colors, USER_CONTROLS.VIEW_BY_CLUSTER);

    // update purchase pattern
    $('#purchase-chart').empty();
    // purchaseVis = new GroupDonutChart("purchase-chart", "purchase-data-selection", [usertype_data, tariff_data], ["User Type", "Tariff Type"], 2, 0, colors, USER_CONTROLS.VIEW);
    purchaseVis = new GroupDistributionChart("purchase-chart", "purchase_chart-selector", "purchase_view-selector", [usertype_data, tariff_data, servicebrand_data], ["User Type", "Tariff Type", "Servicebrand"], 3, 0, colors, USER_CONTROLS.VIEW_BY_CLUSTER);

    // update basic demographics Charts
    $('#basic_demographics-chart').empty();
    basicDemographicsVis = new GroupDistributionChart("basic_demographics-chart", "basic_demographics_chart-selector",
        "basic_demographics_view-selector", [race_data, edu_data, income_data], ["Race", "Education", "Income"], 3, 0, colors, USER_CONTROLS.VIEW_BY_CLUSTER);
}

// Listen to user input
$(document).ready(function() {

    // Navbar active class switch
    $("#MBTAnavbar ul li").click(function() {
        // remove classes from all
        $("#MBTAnavbar ul li").removeClass("active");
        // add class to the one we clicked
        $(this).addClass("active");
    });

    // View request
    $("#req-form").on("submit", function(e) {
        e.preventDefault();

        // Set view
        var $view = $("#view-selection")[0];
        USER_CONTROLS.VIEW = $view.options[$view.selectedIndex].value;
        // Set start_month
        var $month = $("#month-selection")[0];
        USER_CONTROLS.START_MONTH = $month.options[$month.selectedIndex].value;
        // Set duration
        var $duration = $("#duration-selection")[0];
        USER_CONTROLS.DURATION = $duration.options[$duration.selectedIndex].value;
        // Set time weight
        var $time_weight = $("#time-weight-selection")[0];
        USER_CONTROLS.TIME_WEIGHT = $time_weight.options[$time_weight.selectedIndex].value;
        // Set algorithm
        var $algorithm = $("#algorithm-selection")[0];
        USER_CONTROLS.ALGORITHM = $algorithm.options[$algorithm.selectedIndex].value;

        var datatosend = "view request";
        run_pyscript(datatosend);
    })
});
