import requests as r
import pandas as pd
import re

url_template = "https://ppra.org.pk/dad_tenders.asp?PageNo="
html_string = """
    <html>
    <head><title>Latest PPRA Tenders</title></head>
    <body>
        <style>
        table {
            border-collapse: collapse;
            border: 1px solid silver;
        }
        table tr:nth-child(even) {
            background: #E0E0E0;
        }
        </style>
        %s
    </body>
    </html>
"""

def download_parse_table(url):
    html = r.get(url)
    details = re.findall('<td bgcolor="(?:.+?)" width="305">(.+?)</td>', html.text, re.DOTALL)
    details = [detail.replace('\r\n','') for detail in details]
    dfs = pd.read_html(html.text, attrs={'width': '656'}, header=0, parse_dates=['Advertised Date'])
    download_links = re.findall('<a target="_blank" href="(.+?)"><img border="0" src="images/(?:.+?)"></a>',html.text)
    download_links = ["<a href='https://ppra.org.pk/"+link+"' style='display: block;text-align: center;'> <img src='https://ppra.org.pk/images/download_icon.gif'/></a>" for link in download_links]
    tender_table = dfs[0]
    tender_table['Download'] = download_links
    tender_table["Tender  Details"] = details
    return tender_table

combined_df = []
for index in range(1,8):
    df = download_parse_table(url_template+str(index))
    combined_df.append(df)

combined_df = pd.concat(combined_df).reset_index(drop=True)
latest_date = combined_df.iloc[0]['Advertised Date']
filtered_df = combined_df[combined_df['Advertised Date'] == latest_date]

table_html = filtered_df.to_html(index=False,render_links=True, justify="center", escape=False, border=4)
with open('ppra.html', 'w') as f:
    f.write(html_string %(table_html))