$(document).ready(function () {

    var table = $('#backlinks').DataTable({
        processing: true,
        serverSide: true,
        ordering: false,
        fixedHeader: true,
        scrollY: '60vh',
        scrollX: true,
        scrollCollapse: true,
        paging: true,
        fixedHeader: {
            header: true,
            headerOffset: 0
        },
        responsive: {
            details: {
                type: 'inline',   // or 'column'
                target: 'tr'
            }
        },

        autoWidth: false,
        dom:
            "<'dt-top'<'dt-left'l><'dt-right'fB>>" +
            "<'dt-table'tr>" +
            "<'dt-bottom'ip>",

        buttons: [
            {
                extend: 'print',
                text: 'Print'
            }
        ],
        ajax: {
            url: "/api/backlinks",
            type: "GET",
            data: function (d) {
                d.da_min = $('#da_min').val();
                d.da_max = $('#da_max').val();
                d.source_url = $('#source_url_filter').val();
                d.target_url = $('#target_url_filter').val();
            }
        },

        columns: [
            {
                data: "DA",
                render: function (data) {
                    let cls = "red";
                    if (data >= 60) cls = "green";
                    else if (data >= 40) cls = "yellow";
                    return `<span class="da-badge ${cls}">${data}</span>`;
                },
                className: 'dt-body-right',
                responsivePriority: 1
            },
            {
                data: "Source",
                className: 'dt-body-center',
                responsivePriority: 5,
            },
            {
                data: "Target",
                className: 'dt-body-center',
                responsivePriority: 6,
            },
            {
                data: "Indexed",
                className: 'dt-body-right',
                responsivePriority: 4
            },
            {
                data: "Source_url",
                render: d => `<a href="${d}" target="_blank">${d}</a>`,
                responsivePriority: 2
            },
            {
                data: "Target_url",
                render: d => `<a href="${d}" target="_blank">${d}</a>`,
                responsivePriority: 3
            }
        ]

    });
    // Trigger reload on filter change
    $('#da_min, #da_max, #source_url_filter, #target_url_filter')
        .on('keyup change', function () {
            table.draw();
        });
    // Dark mode toggle logic
    $('#themeToggle').on('click', function () {
        $('body').toggleClass('dark-mode');

        const isDark = $('body').hasClass('dark-mode');
        $(this).text(isDark ? '☀️ Light Mode' : '🌙 Dark Mode');
    });
    //reset filter logic
    $('#resetFilters').on('click', function () {
        $('input, select').val('');
        table.search('').draw();
    });



});
