# tests/test_generateCSV.py
import csv
import unittest
import os
import xml.etree.ElementTree as ET  # 导入ElementTree
from generateCSV import parse_xml, write_csv

class TestGenerateCSV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 类级别的设置，这将在所有测试开始前执行一次
        cls.test_data_path = 'tests/test-data/test_data.xml'
        cls.test_output_path = 'tests/test-data/test_output.csv'
        # 这里可以创建一个测试用的XML文件或使用一个已知数据的真实文件进行测试

    def test_parse_xml_with_valid_data(self):
        # 测试解析格式良好的XML文件
        data = parse_xml(self.test_data_path)
        # 断言返回的数据是列表类型
        self.assertIsInstance(data, list)
        # 断言列表中的每一行都有正确数量的列
        self.assertTrue(all(len(row) == 4 for row in data))
        # 根据测试XML的已知值添加更具体的测试

    def test_parse_xml_with_missing_elements(self):
        # 测试解析缺少元素的XML文件，检查是否能够优雅地处理
        test_xml_path_missing_elements = 'tests/test-data/test_data_with_missing_values.xml'
        try:
            data = parse_xml(test_xml_path_missing_elements)
            # 根据你的函数设计，此处可以是检查返回了空列表，或者是否捕获了特定异常
            self.assertIsInstance(data, list)
            # 如果函数设计为遇到缺失元素时返回空列表，则可以检查列表是否为空
            self.assertEqual(len(data), 0)
            # 或者，如果函数设计为填充缺失元素的默认值，则检查这些值
            # 例如，使用安大略区的价格作为默认值：
            for row in data:
                self.assertIn('Ontario', row)  # 假设使用了安大略的价格
        except ET.ParseError as e:
            self.fail(f"XML解析失败，抛出了一个异常：{str(e)}")

    def test_parse_xml_with_invalid_structure(self):
        # 测试解析结构无效的XML
        test_xml_path_invalid = 'tests/test-data/test_data_invalid_structure.xml'
        try:
            data = parse_xml(test_xml_path_invalid)
            # 根据你的函数设计，这里可以是检查返回了空列表，或者是否捕获了特定异常
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 0)  # 如果设计为返回空列表
        except ET.ParseError as e:
            # 如果设计为在结构无效时抛出异常
            self.assertTrue(isinstance(e, ET.ParseError))

    def test_write_csv_creates_file(self):
        # 测试write_csv函数是否在指定路径创建了CSV文件
        test_data = parse_xml(self.test_data_path)
        write_csv(test_data, self.test_output_path)
        self.assertTrue(os.path.exists(self.test_output_path))

    def test_write_csv_with_no_data(self):
        # 测试write_csv函数处理空列表时是否没有抛出错误
        write_csv([], self.test_output_path)
        # CSV应该仍然有头部，但没有数据行
        with open(self.test_output_path, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)  # 只应该存在头部

    def test_csv_file_content(self):
        # 测试CSV文件的实际内容，确保正确写入
        test_data = parse_xml(self.test_data_path)
        write_csv(test_data, self.test_output_path)
        with open(self.test_output_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertEqual(headers, ['Zone', 'Type', 'Delivery Interval', 'Dollars per MW'])
            for row in reader:
                self.assertEqual(len(row), 4)
                # 在这里根据测试数据的已知值添加更多的检查
    def test_intertie_zone_values_with_ontario_defaults(self):
        test_xml_file_with_blank_intertie_values = 'tests/test-data/test_data_with_blank_values.xml'
        # 确保文件路径正确
        self.assertTrue(os.path.exists(test_xml_file_with_blank_intertie_values), "测试文件不存在")

        # 尝试打开并读取文件，以确保它不是空的
        with open(test_xml_file_with_blank_intertie_values, 'r') as file:
            content = file.read()
            self.assertTrue(content, "测试文件是空的")

        # 测试跨接区域市场价值为空时是否使用了安大略区域的默认值
        # 这里需要指向一个包含空白跨接区域市场价值的特定测试XML文件
        test_xml_file_with_blank_intertie_values = 'tests/test-data/test_data_with_blank_values.xml'
        data = parse_xml(test_xml_file_with_blank_intertie_values)
        
        # 假设我们知道安大略区域的某个默认价值
        known_ontario_price_for_interval = '20.00'  # 示例价值
        # 假设我们知道跨接区域市场价值应该为空的时间间隔
        interval_with_blank_value = '1'  # 示例时间间隔
        
        # 查找该时间间隔的跨接区域市场价值是否被安大略区域的价值所替代
        for row in data:
            if row[2].endswith(f":{int(interval_with_blank_value)*5:02d}:00"):
                # row[0] 是区域名称，我们需要找到非安大略区域的行
                if row[0] != 'Ontario':
                    self.assertEqual(row[3], known_ontario_price_for_interval)
    @classmethod
    def tearDownClass(cls):
        # 清理测试过程中创建的文件
        if os.path.exists(cls.test_output_path):
            os.remove(cls.test_output_path)

if __name__ == '__main__':
    unittest.main()
