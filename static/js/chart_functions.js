function drawChart(id, grafico, type, colors) {
    var main = new Array();
    var labels = new Array();
    var title = new Array();

    if (!colors) {
        var colors = ["#DC3912", "#F90", "#36C", "#521", "#AD2", "#AF5", "#DF2", "#C33", "#A11", '#E21']
    }

    if (!type){
        type = 'pie';
    }

    if (type == 'bar') {
        for (var i = 1; i < grafico.length; i++) {
            labels.push(grafico[i][0]);
            main.push(grafico[i][2])
        }

        var config = {
            type: type,
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '',
                        data: main, // [300, 50, 100],
                        backgroundColor: colors,
                        hoverBackgroundColor: colors
                    }
                ]
            },
            options: {
                responsive: true,
                legend: {
                    display: false,
                }
            }
        };
    }

    if (type == 'pie') {
        var _colors = new Array();
        for (var i = 0; i < grafico.length; i++) {
            if (i == 0) {
                for (var j = 0; j < grafico[i].length; j++) {
                    if (j == 0) {

                    } else {
                        title.push(grafico[i][j])
                    }
                }
            } else {
                if (grafico[i][0] == 'Verde') {
                    _colors.push(colors[0]);
                } else if (grafico[i][0] == 'Rojo') {
                    _colors.push(colors[2]);
                } else if (grafico[i][0] == 'Amarillo'){
                    _colors.push(colors[1]);
                } else {
                    _colors = colors;
                }
                labels.push(grafico[i][0]);
                main.push(grafico[i][1]);
            }
        }


        var config = {
            type: type,
            data: {
                labels: labels,
                datasets: [
                    {
                        data: main, // [300, 50, 100],
                        backgroundColor: _colors,
                        hoverBackgroundColor: _colors
                    }
                ]
            },
            options: {
                responsive: true
            }
        };
    }


    if (type == 'line'){
        var datasets = new Array();
        var cho = new Array();

        for (var i = 0; i < grafico.length; i++) {
            if (i == 0) {
                for (var j = 0; j < grafico[i].length; j++) {
                    if (j == 0) {

                    } else {
                        title.push(grafico[i][j])
                    }
                }
            } else {
                labels.push(grafico[i][0])
                main.push(grafico[i][1])
            }
        }

        for (var x = 1; x < grafico[0].length; x++) {
            var auxiliar = [];
            for (var y = 1; y < grafico.length; y++) {
                auxiliar.push(grafico[y][x]);
            }
            cho.push(auxiliar);
        }

        for (var j = 0; j < cho.length; j++) {
            // [j]
            datasets.push(
                {
                    label: title[j],
                    data: cho[j], // [300, 50, 100],
                    tension: 0,
                    fill: false,
                    backgroundColor: colors,
                    hoverBackgroundColor: colors,
                    backgroundColor: colors[j],
                    borderColor: colors[j],
                    borderCapStyle: 'butt',
                    borderDash: [],
                    borderDashOffset: 0.0,
                    borderJoinStyle: 'miter',
                    pointBorderColor: "rgba(75,192,192,1)",
                    pointBackgroundColor: "#fff",
                    pointBorderWidth: 1,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: "rgba(75,192,192,1)",
                    pointHoverBorderColor: "rgba(220,220,220,1)",
                }
            )
        }


        var config = {
            type: type,
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                responsive: true
            }
        }
    }


    window.myPie = new Chart(id, config);
    // Chart.defaults.global.legend.display = false;
}