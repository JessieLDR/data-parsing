import csv
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_xml(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    csv_data = []
    ns = {'ns': 'http://www.ieso.ca/schema'}
    delivery_date_element = root.find('.//ns:DeliveryDate', ns)
    delivery_hour_element = root.find('.//ns:DeliveryHour', ns)

    # 检查是否找到了必要的元素
    if delivery_date_element is None or delivery_hour_element is None:
        return []  # 如果没有找到这些元素，返回空列表

    delivery_date = delivery_date_element.text
    delivery_hour = delivery_hour_element.text

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

    return sorted(csv_data, key=lambda x: (x[0], x[2]))

def write_csv(csv_data, csv_file_path):
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Zone', 'Type', 'Delivery Interval', 'Dollars per MW'])
        csv_writer.writerows(csv_data)

if __name__ == "__main__":
    xml_file_path = 'data/PUB_RealtimeMktPrice_2019041309_v12.xml'
    csv_file_path = 'output.csv'
    csv_data = parse_xml(xml_file_path)
    write_csv(csv_data, csv_file_path)
    print(f"CSV 文件已生成：{csv_file_path}")
