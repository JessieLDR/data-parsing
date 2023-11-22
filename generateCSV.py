import csv
import xml.etree.ElementTree as ET

xml_file_path = 'data/PUB_RealtimeMktPrice_2019041309_v12.xml'

tree = ET.parse(xml_file_path)
root = tree.getroot()

csv_data = []
ns = {'ns': 'http://www.ieso.ca/schema'}
delivery_date = root.find('.//ns:DeliveryDate', ns).text
delivery_hour = root.find('.//ns:DeliveryHour', ns).text

# 存储安大略区的价格
ontario_prices = {}

# 首先提取安大略区的价格
for intertie_price in root.findall('.//ns:IntertieZonalPrices', ns):
    zone = intertie_price.find('.//ns:IntertieZoneName', ns).text
    if zone == "Ontario":
        for price in intertie_price.findall('.//ns:Prices', ns):
            for interval_price in price.findall('.//ns:IntervalPrice', ns):
                interval = interval_price.find('ns:Interval', ns).text
                mcp = interval_price.find('ns:MCP', ns).text
                ontario_prices[interval] = mcp

# 提取所有区域的价格
for intertie_price in root.findall('.//ns:IntertieZonalPrices', ns):
    zone = intertie_price.find('.//ns:IntertieZoneName', ns).text

    for price in intertie_price.findall('.//ns:Prices', ns):
        price_type = price.find('.//ns:PriceType', ns).text

        for interval_price in price.findall('.//ns:IntervalPrice', ns):
            interval = interval_price.find('ns:Interval', ns).text
            mcp = interval_price.find('ns:MCP', ns).text

            if not mcp:  # 如果MCP为空，则使用安大略区的价格
                mcp = ontario_prices.get(interval, "0.00")  # 如果安大略区也没有，就默认为0.00

            delivery_interval = f"{delivery_date} {int(delivery_hour):02d}:{int(interval)*5:02d}:00"
            csv_data.append([zone, price_type, delivery_interval, mcp])

sorted_csv_data = sorted(csv_data, key=lambda x: (x[0], x[2]))

csv_file_path = 'output.csv'
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Zone', 'Type', 'Delivery Interval', 'Dollars per MW'])
    csv_writer.writerows(sorted_csv_data)

print(f"CSV 文件已生成：{csv_file_path}")