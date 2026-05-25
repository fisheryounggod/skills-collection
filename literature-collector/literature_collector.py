#!/usr/bin/env python3
"""
文献收集器核心脚本
功能：从用户输入提取文献信息，检测重复，写入飞书表格
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 加载配置
CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)


class LiteratureCollector:
    """文献收集器"""

    def __init__(self):
        self.config = CONFIG
        self.fields = CONFIG['fields']
        self.settings = CONFIG['settings']

    def extract_citation_from_text(self, text: str) -> Dict[str, str]:
        """
        从文本中提取引用信息（作者、年份）
        示例："Smith et al. (2024)" 或 "Smith, Johnson & Williams (2024)"
        """
        citation = {}

        # 提取年份（括号内的4位数字）
        year_match = re.search(r'\((\d{4})\)', text)
        if year_match:
            citation['year'] = int(year_match.group(1))

        # 提取作者（括号前的文本）
        author_part = text.split('(')[0] if '(' in text else text
        authors = re.findall(r'[A-Z][a-z]+', author_part)
        if authors:
            if len(authors) == 1:
                citation_format = f"{authors[0]} ({citation.get('year', 'n.d.')})"
            elif len(authors) == 2:
                citation_format = f"{authors[0]} & {authors[1]} ({citation.get('year', 'n.d.')})"
            elif len(authors) <= 3:
                citation_format = f"{', '.join(authors[:-1])} & {authors[-1]} ({citation.get('year', 'n.d.')})"
            else:
                citation_format = f"{authors[0]} et al. ({citation.get('year', 'n.d.')})"
            citation['citation'] = citation_format

        return citation

    def parse_user_input(self, user_input: str) -> Dict[str, any]:
        """
        解析用户输入，提取文献信息
        支持结构化输入（字段名: 值 或 字段名：值）和自然语言输入
        """
        fields = {}

        # 1. 尝试结构化解析（字段名: 值 或 字段名：值）
        structured_data = {}
        # 支持换行符、中文分号、英文分号作为分隔符
        lines = re.split(r'\n|；|;', user_input)
        for line in lines:
            line = line.strip()
            # 支持中文和英文冒号
            if ':' in line or '：' in line:
                # 使用rsplit从右边分割，处理多个冒号的情况
                separator = '：' if '：' in line else ':'
                parts = line.rsplit(separator, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    # 如果key中还有冒号，取最后一个冒号后的部分
                    if '：' in key:
                        key = key.split('：')[-1].strip()
                    elif ':' in key:
                        key = key.split(':')[-1].strip()

                    key = key.lower()

                # 调试输出（临时，可注释）
                # print(f"[DEBUG] key='{key}', value='{value}'", file=sys.stderr)

                field_mapping = {
                    '标题': 'title', 'title': 'title', '文章标题': 'title',
                    '作者': 'citation', 'citation': 'citation', '引用': 'citation',
                    '年份': 'year', 'year': 'year',
                    '期刊': 'journal', 'journal': 'journal', '来源': 'journal',
                    '科学问题': 'research_question', 'research_question': 'research_question',
                    '研究类型': 'research_type', 'research_type': 'research_type',
                    '创新点': 'innovation', 'innovation': 'innovation',
                    '不足': 'limitations', 'limitations': 'limitations',
                    '数据来源': 'data_source', 'data_source': 'data_source',
                    '方法': 'methods', 'methods': 'methods',
                    '发现': 'findings', 'findings': 'findings',
                    '备注': 'notes', 'notes': 'notes'
                }

                if key in field_mapping:
                    structured_data[field_mapping[key]] = value

        # 2. 如果有结构化数据，直接使用
        if structured_data:
            # 处理多选字段
            if 'research_type' in structured_data:
                structured_data['research_type'] = [s.strip() for s in structured_data['research_type'].split(',')]
            if 'methods' in structured_data:
                structured_data['methods'] = [s.strip() for s in structured_data['methods'].split(',')]
            return structured_data

        # 3. 否则使用自然语言解析（简单规则）
        # 提取标题（通常是第一个重要信息）
        title_match = re.search(r'[:：]\s*([^:\n]+)', user_input)
        if title_match:
            fields['title'] = title_match.group(1).strip()
        elif '《' in user_input and '》' in user_input:
            fields['title'] = re.search(r'《([^》]+)》', user_input).group(1)
        else:
            # 尝试从开头提取
            first_line = user_input.split('\n')[0]
            if first_line and not first_line.startswith('文献'):
                fields['title'] = first_line.strip()

        # 尝试从引用文本中提取作者和年份
        citation_info = self.extract_citation_from_text(user_input)
        if citation_info:
            if 'year' in citation_info:
                fields['year'] = citation_info['year']
            if 'citation' in citation_info:
                fields['citation'] = citation_info['citation']

        # 提取期刊
        journal_match = re.search(r'(期刊|发表在|published in)[:：]\s*([^,\n]+)', user_input, re.IGNORECASE)
        if journal_match:
            fields['journal'] = journal_match.group(2).strip()

        return fields

    def validate_fields(self, fields: Dict[str, any]) -> Dict[str, any]:
        """
        验证和规范化字段
        """
        # 检查必填字段
        if 'title' not in fields or not fields['title']:
            raise ValueError("缺少必填字段：文章标题")

        # 年份转换
        if 'year' in fields and isinstance(fields['year'], str):
            year_match = re.search(r'\d{4}', fields['year'])
            if year_match:
                fields['year'] = int(year_match.group())
            else:
                del fields['year']

        # 验证多选字段
        for field_name in ['research_type', 'methods']:
            if field_name in fields and isinstance(fields[field_name], str):
                fields[field_name] = [s.strip() for s in fields[field_name].split(',')]

        return fields

    def format_for_bitable(self, fields: Dict[str, any]) -> Dict[str, any]:
        """
        将字段格式化为飞书Bitable API格式
        """
        bitable_fields = {}

        for field_name, field_value in fields.items():
            field_config = self.fields.get(field_name)

            if not field_config:
                continue

            field_id = field_config['id']
            field_type = field_config['type']

            if field_value:
                if field_type == 'Text':
                    bitable_fields[field_id] = field_value
                elif field_type == 'Number':
                    if isinstance(field_value, str):
                        # 尝试提取数字
                        num_match = re.search(r'\d+', field_value)
                        if num_match:
                            bitable_fields[field_id] = int(num_match.group())
                    else:
                        bitable_fields[field_id] = field_value
                elif field_type == 'MultiSelect' and isinstance(field_value, list):
                    # 验证选项是否在允许的选项列表中
                    valid_options = [opt for opt in field_value if opt in field_config.get('options', [])]
                    if valid_options:
                        bitable_fields[field_id] = valid_options

        return bitable_fields

    def generate_summary(self, fields: Dict[str, any], record_id: str = None) -> str:
        """
        生成收藏确认信息
        """
        summary = []

        if 'title' in fields:
            summary.append(f"📖 标题：{fields['title']}")
        if 'citation' in fields:
            summary.append(f"📝 引用形式：{fields['citation']}")
        if 'year' in fields:
            summary.append(f"📅 年份：{fields['year']}")
        if 'journal' in fields:
            summary.append(f"📚 期刊：{fields['journal']}")
        if 'research_type' in fields:
            summary.append(f"🔬 研究类型：{', '.join(fields['research_type'])}")
        if 'methods' in fields:
            summary.append(f"🔧 方法：{', '.join(fields['methods'])}")
        if 'findings' in fields:
            summary.append(f"🎯 主要发现：{fields['findings']}")

        if record_id:
            summary.append(f"📝 记录ID：{record_id}")

        return '\n'.join(summary)


def main():
    """主函数（用于测试）"""
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        user_input = input("请输入文献信息：")

    collector = LiteratureCollector()

    try:
        # 解析输入
        fields = collector.parse_user_input(user_input)
        print(f"解析结果：{json.dumps(fields, ensure_ascii=False, indent=2)}")

        # 验证字段
        validated_fields = collector.validate_fields(fields)

        # 格式化为飞书格式
        bitable_fields = collector.format_for_bitable(validated_fields)
        print(f"\n飞书格式：{json.dumps(bitable_fields, ensure_ascii=False, indent=2)}")

        # 生成摘要
        summary = collector.generate_summary(validated_fields)
        print(f"\n{summary}")

    except ValueError as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
