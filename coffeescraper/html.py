# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from datetime import datetime
from jinja2 import Template
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return z.isoformat()
        else:
            return super().default(z)


def generate_graph_html(data_tuples, cheapest_site="unkown", lowest_price_today="unknown", filename="/tmp/graph.html"):
    # Organize data by key for the graph
    data_by_key = {}
    labels = set()
    colors = ["#ff0000", "#00ff00", "#0000ff", "#aaaa00", "#00aaaa", "#aa00aa"]
    color_index = 0
    for _, key, value, timestamp in data_tuples:
        if key not in data_by_key:
            data_by_key[key] = {
                "values": [],
                "color": colors[color_index],
            }
            color_index = (color_index + 1) % len(colors)
        data_by_key[key]["values"].append({"x": timestamp, "y": value})
        labels.add(timestamp)
    labels = sorted(labels)

    if type(lowest_price_today) == float:
        lowest_price_today = f"{lowest_price_today:.2f}"
        
    # Create a Jinja2 template
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Graph Example</title>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"
        integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"
        integrity="sha256-+8RZJua0aEWg+QVVKg4LEzEEm/8RFez5Tb4JBNiV5xA=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@2.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"
        integrity="sha256-xlxh4PaMDyZ72hWQ7f/37oYI0E2PrBbtzi1yhvnG+/E=" crossorigin="anonymous"></script>
    <meta charset="UTF-8">
    </head>
    <body>
        <style>
        .site {
            background-color: #eeeeee;
            width: 40em;
            list-style: none;
            margin-top: 3px;
        }
        .lowest {
            font-weight: bold;
        }
        </style>
        <h2>Prijzen Dolce Gusto Lungo XL (30 cups)</h2>
        <p>We houden op dit moment de volgende sites in de gaten:</p>
        <ul>
        {% for key in data_by_key.keys() %}
        <li class="site"><a href="{{key}}">{{key}}</a></li>
        {% endfor %}
        </ul><br>
        <p>De laagste prijs op dit moment is <span class="lowest">{{lowest_price_today}} €</span> bij <a href="{{cheapest_site}}">{{cheapest_site}}</a></p>
        <canvas id="myChart"></canvas>
        <script>
            $(document).ready(function() {
                var ctx = document.getElementById('myChart').getContext('2d');
                var datasets = [];
                {% for key, data in data_by_key.items() %}
                    datasets.push({
                        label: '{{ key }}',
                        data: {{ json(data['values']) }},
                        borderColor: '{{ data.color }}',
                        backgroundColor: 'rgba(0, 0, 0, 0)',  // Transparent background
                        borderWidth: 2
                    });
                {% endfor %}
                var myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: {{ json(labels) }},
                        datasets: datasets
                    },
                    options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                text: 'prijs in €',
                                display: true
                            },
                            ticks: {
                                callback: (val) => {
                                    return val.toFixed(2);
                                }
                            }
                        }
                    }
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    template = Template(template_str)
    html_content = template.render(
        data_by_key=data_by_key,
        labels=labels,
        cheapest_site=cheapest_site,
        lowest_price_today=lowest_price_today,
        json=lambda x: json.dumps(x, cls=DateTimeEncoder),
    )
    with open(filename, "w") as f:
        f.write(html_content)
        logging.info(f"html file generated ({filename})")


if __name__ == "__main__":
    # Test data
    data = [
        ("A", 10.2, datetime(2023, 8, 1)),
        ("B", 15.5, datetime(2023, 8, 5)),
        ("A", 8.7, datetime(2023, 8, 10)),
        ("B", 12.1, datetime(2023, 8, 15)),
        # Add more data tuples here
    ]

    generate_graph_html(data)
