#!/bin/bash
# Jupyter + LaTeX -> PDF 一键生成技能脚本
# 用法: ./jupyter-pdf.sh generate notebook.ipynb [output.pdf] [timeout]

set -e

# 默认值
DEFAULT_TIMEOUT=600
OUTPUT_DIR="."

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印帮助信息
print_help() {
    echo "Jupyter + LaTeX -> PDF 一键生成工具"
    echo ""
    echo "用:"
    echo "  $0 <command> [options]"
    echo ""
    echo "命令:"
    echo "  generate        生成PDF报告（默认命令）"
    echo "  validate        验证notebook格式"
    echo "  help            显示此帮助信息"
    echo ""
    echo "选项:"
    echo "  --timeout N      设置超时时间（秒），默认600"
    echo "  --output FILE    设置输出文件名，默认notebook名.pdf"
    echo "  --dir DIR        设置输出目录，默认当前目录"
    echo ""
    echo "示例:"
    echo "  $0 generate my_analysis.ipynb"
    echo "  $0 generate --timeout 900 --output report.pdf my_analysis.ipynb"
    echo "  $0 validate my_analysis.ipynb"
    exit 0
}

# 检查参数
if [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    print_help
fi

if [ -z "$1" ]; then
    print_help
fi

# 解析参数
COMMAND=$1
shift

NOTEBOOK_FILE=""
PDF_FILE=""
TIMEOUT=$DEFAULT_TIMEOUT

while [[ $# -gt 0 ]]; do
    case $1 in
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --output)
            PDF_FILE="$2"
            shift 2
            ;;
        --dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            NOTEBOOK_FILE="$1"
            shift
            ;;
    esac
done

# 验证notebook文件
if [ -z "$NOTEBOOK_FILE" ]; then
    echo -e "${RED}错误: 未指定notebook文件${NC}"
    echo "用: $0 generate <notebook.ipynb>"
    exit 1
fi

if [ ! -f "$NOTEBOOK_FILE" ]; then
    echo -e "${RED}错误: Notebook文件不存在${NC}"
    echo "文件: $NOTEBOOK_FILE"
    exit 1
fi

# 设置默认PDF文件名
if [ -z "$PDF_FILE" ]; then
    PDF_FILE=$(basename "$NOTEBOOK_FILE" .ipynb).pdf
fi

# 创建输出目录
if [ "$OUTPUT_DIR" != "." ]; then
    mkdir -p "$OUTPUT_DIR"
    PDF_FILE="$OUTPUT_DIR/$PDF_FILE"
fi

# 执行命令
case $COMMAND in
    generate)
        echo "=========================================="
        echo "  Jupyter + LaTeX -> PDF Generator"
        echo "=========================================="
        echo ""
        echo -e "${GREEN}输入文件:${NC}"
        echo "  Notebook: $NOTEBOOK_FILE"
        echo ""
        echo -e "${GREEN}输出配置:${NC}"
        echo "  PDF: $PDF_FILE"
        echo "  超时: ${TIMEOUT}秒"
        echo "  目录: $OUTPUT_DIR"
        echo ""

        # 检查jupyter nbconvert
        if ! command -v jupyter nbconvert &> /dev/null; then
            echo -e "${RED}错误: jupyter nbconvert未安装${NC}"
            echo "安装: pip install jupyter nbconvert"
            exit 1
        fi

        # 检查xelatex
        if ! command -v xelatex &> /dev/null; then
            echo -e "${YELLOW}警告: xelatex未找到${NC}"
            echo "PDF生成可能失败，请安装LaTeX"
            echo ""
        fi

        echo -e "${GREEN}执行notebook...${NC}"
        echo ""

        # 执行nbconvert
        if jupyter nbconvert --execute --to pdf \
            --ExecutePreprocessor.timeout=$TIMEOUT \
            "$NOTEBOOK_FILE" 2>&1; then
            
            # 检查结果
            if [ -f "$PDF_FILE" ]; then
                SIZE=$(ls -lh "$PDF_FILE" | awk '{print $5}')
                echo ""
                echo -e "${GREEN}========================================"
                echo "  ✅ PDF生成成功！"
                echo "========================================${NC}"
                echo ""
                echo -e "${GREEN}📦 文件信息:${NC}"
                echo "  文件: $PDF_FILE"
                echo "  大小: $SIZE"
                echo "  路径: $(cd "$(dirname "$PDF_FILE")" && pwd)"
                echo ""
                
                # 显示图表文件（如果有）
                CHART_FILES=$(find "$(dirname "$NOTEBOOK_FILE")" -maxdepth 1 -name "*.png" -o -name "*.jpg" 2>/dev/null | head -5)
                if [ -n "$CHART_FILES" ]; then
                    echo -e "${GREEN}📊 图表文件:${NC}"
                    echo "$CHART_FILES" | while read file; do
                        CHART_SIZE=$(ls -lh "$file" | awk '{print $5}')
                        echo "  - $(basename "$file") ($CHART_SIZE)"
                    done
                fi
                
                echo ""
                echo -e "${YELLOW}下一步操作:${NC}"
                echo "  查看PDF: xdg-open '$PDF_FILE'"
                echo "  查看位置: cd '$(dirname "$PDF_FILE")'"
                echo ""
                
                # 询问是否打开
                read -p "是否立即打开PDF? (y/n): " -n 1 -r
                echo ""
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    echo -e "${GREEN}正在打开PDF...${NC}"
                    xdg-open "$PDF_FILE" 2>/dev/null || \
                    open "$PDF_FILE" 2>/dev/null || \
                    echo -e "${YELLOW}无法自动打开，请手动打开${NC}"
                fi
                
                echo ""
                echo -e "${GREEN}✅ 完成！${NC}"
                exit 0
            else
                echo -e "${RED}========================================"
                echo "  ❌ PDF生成失败"
                echo "========================================${NC}"
                echo ""
                echo "请检查:"
                echo "  1. notebook JSON格式是否正确"
                echo "  2. 代码是否有语法错误"
                echo "  3. 超时时间是否足够"
                echo "  4. LaTeX是否正确安装"
                exit 1
            fi
        else
            echo -e "${RED}========================================"
            echo "  ❌ 执行失败"
            echo "========================================${NC}"
            echo ""
            echo "请检查错误信息"
            exit 1
        fi
        ;;
        
    validate)
        echo "验证notebook格式..."
        echo "文件: $NOTEBOOK_FILE"
        echo ""
        
        # 检查JSON格式
        if python3 -m json.tool "$NOTEBOOK_FILE" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ JSON格式正确${NC}"
        else
            echo -e "${RED}❌ JSON格式错误${NC}"
            python3 -m json.tool "$NOTEBOOK_FILE" 2>&1 | head -20
            exit 1
        fi
        
        # 检查必要字段
        echo ""
        echo "检查必要字段..."
        HAS_CELLS=$(python3 -c "import json; nb=json.load(open('$NOTEBOOK_FILE')); print('cells' in nb)" 2>/dev/null)
        HAS_METADATA=$(python3 -c "import json; nb=json.load(open('$NOTEBOOK_FILE')); print('metadata' in nb)" 2>/dev/null)
        
        if [ "$HAS_CELLS" == "True" ]; then
            echo -e "${GREEN}  ✅ cells字段存在${NC}"
        else
            echo -e "${RED}  ❌ cells字段缺失${NC}"
        fi
        
        if [ "$HAS_METADATA" == "True" ]; then
            echo -e "${GREEN}  ✅ metadata字段存在${NC}"
        else
            echo -e "${RED}  ❌ metadata字段缺失${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}✅ 验证完成！${NC}"
        ;;
        
    *)
        echo -e "${RED}错误: 未知命令 '$COMMAND'${NC}"
        echo ""
        print_help
        exit 1
        ;;
esac
