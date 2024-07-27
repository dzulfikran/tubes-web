document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('salesChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: salesChartData.labels,
            datasets: [{
                label: 'Grafik Penjualan',
                data: salesChartData.data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // Ensure the chart is responsive
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
