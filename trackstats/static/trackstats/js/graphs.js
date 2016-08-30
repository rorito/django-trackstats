(function () {
    "use strict";

    function init() {
        google.load('visualization', '1', {packages: ['corechart']});
        google.setOnLoadCallback(drawChart);

        function drawChart() {
            var dataElement = document.getElementById('trackstats-graph');
            if (dataElement === null) {
                console.info("No data for plotting");
                return;
            }

            var data = new google.visualization.DataTable();
            data.addColumn('date', 'Date');
            data.addColumn('number', 'Value');

            data.addRows(graphData);
            var chart = new google.visualization.ColumnChart(dataElement);
            chart.draw(data, graphOptions);
        }
    }

    document.addEventListener("DOMContentLoaded", function() {
        init();
    });
})();
