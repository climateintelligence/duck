from pathlib import Path

from pywps import Process, LiteralInput, ComplexOutput, Format

from duck import query


class Dashboard(Process):
    def __init__(self):
        inputs = [
            LiteralInput(
                "time",
                "Time Period",
                abstract="The time period for the report seperated by /"
                "Example: 2023-09-01/2023-09-30",
                data_type="string",
                default="2023-09-01/2023-09-30",
                min_occurs=0,
                max_occurs=1,
            ),
        ]
        outputs = [
            ComplexOutput(
                "report",
                "Generated HTML Report",
                as_reference=True,
                supported_formats=[Format("text/html")],
            ),
        ]

        super(Dashboard, self).__init__(
            self._handler,
            identifier="dashboard",
            title="Generate HTML Report",
            version="1.0",
            abstract="Generate an HTML report from a provenance database.",
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        workdir = Path(self.workdir)
        # input_csv = request.inputs['input_csv'][0].file

        # Query the provenance database ... result is a Pandas DataFrame
        df = query.query()

        # Generate an HTML report from the DataFrame
        html_report = self.write_html(df, workdir)

        print(f"report: {html_report}")
        response.outputs["report"].file = html_report
        # response.outputs["report"].output_format = Format("text/html")

        return response

    def write_html(self, df, workdir):
        # Convert the DataFrame to an HTML table
        html_table = df.to_html(escape=False, index=False)

        # Define the HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Provenance Report</title>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    border: 1px solid #ddd;
                }}

                th, td {{
                    text-align: left;
                    padding: 8px;
                }}

                th {{
                    background-color: #f2f2f2;
                }}

                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1>Provenance Report</h1>
            {html_table}
        </body>
        </html>
        """

        # Write the HTML template to a file
        outfile = workdir / "provenance_report.html"
        with outfile.open(mode="w") as file:
            file.write(html_template)

        return outfile
