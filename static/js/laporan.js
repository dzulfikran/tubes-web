document.addEventListener("DOMContentLoaded", function() {
    var modal = document.getElementById("printReportModal");
    var btn = document.getElementById("printReportButton");
    var span = document.getElementsByClassName("close")[0];

    btn.onclick = function() {
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Form submission
    document.getElementById('printReportForm').onsubmit = function(event) {
        event.preventDefault();
        var reportType = document.getElementById('reportType').value;
        var startDate = document.getElementById('startDate').value;
        var endDate = document.getElementById('endDate').value;

        var url = '/print_report?reportType=' + reportType + '&startDate=' + startDate + '&endDate=' + endDate;
        window.open(url, '_blank');
    }
});
