// =====================================================
// analytics.js — графики для страницы аналитики
// =====================================================

// ===== ГРАФИК ВЛАЖНОСТИ =====
function renderHumidityChart(data, labels) {
    var options = {
        series: [{
            name: 'Влажность',
            data: data
        }],
        chart: {
            type: 'area',
            height: 350,
            toolbar: {
                show: true,
                tools: {
                    download: true,
                    zoom: true,
                    zoomin: true,
                    zoomout: true,
                    pan: true,
                    reset: true
                }
            }
        },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 3 },
        title: {
            text: 'Влажность почвы (%)',
            align: 'left'
        },
        labels: labels,
        xaxis: { type: 'category' },
        yaxis: { min: 0, max: 100 },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.2
            }
        },
        colors: ['#0d6efd']
    };
    new ApexCharts(document.querySelector("#humidityChart"), options).render();
}

// ===== ГРАФИК ТЕМПЕРАТУРЫ =====
function renderTemperatureChart(data, labels) {
    var options = {
        series: [{
            name: 'Температура',
            data: data
        }],
        chart: {
            type: 'line',
            height: 350,
            toolbar: { show: true }
        },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 3 },
        title: {
            text: 'Температура (°C)',
            align: 'left'
        },
        labels: labels,
        xaxis: { type: 'category' },
        colors: ['#dc3545'],
        markers: { size: 5 }
    };
    new ApexCharts(document.querySelector("#temperatureChart"), options).render();
}

// ===== ГРАФИК ПОЛИВОВ =====
function renderWateringChart(counts, dates) {
    var options = {
        series: [{
            name: 'Поливы',
            data: counts
        }],
        chart: {
            type: 'bar',
            height: 350,
            toolbar: { show: true }
        },
        title: {
            text: 'Количество поливов по дням',
            align: 'left'
        },
        xaxis: {
            categories: dates
        },
        colors: ['#198754'],
        plotOptions: {
            bar: {
                borderRadius: 6,
                columnWidth: '50%'
            }
        }
    };
    new ApexCharts(document.querySelector("#wateringChart"), options).render();
}