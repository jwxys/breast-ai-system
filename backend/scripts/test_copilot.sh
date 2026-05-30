#!/bin/bash

# ============================================
# Copilot 系统命令快速测试脚本
# ============================================

set -e

echo "=============================================="
echo "医疗 Copilot 系统命令测试"
echo "=============================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
SESSION_ID=""

# 测试函数
test_create_session() {
    echo -e "${BLUE}测试 1: 创建 Copilot 会话${NC}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions" \
        -H "Content-Type: application/json" \
        -d '{"mode": "control"}')
    
    SESSION_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))")
    
    if [ -n "$SESSION_ID" ]; then
        echo -e "${GREEN}✅ 会话创建成功：$SESSION_ID${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}❌ 会话创建失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_create_patient() {
    echo -e "${BLUE}测试 2: 创建患者${NC}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/commands" \
        -H "Content-Type: application/json" \
        -d '{
            "command": "create_patient",
            "params": {
                "name": "测试患者",
                "age": 35,
                "gender": "female",
                "phone": "13812345678"
            }
        }')
    
    SUCCESS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ 患者创建成功${NC}"
        PATIENT_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('patient_id', ''))")
        echo "   患者 ID: $PATIENT_ID"
        echo ""
        return 0
    else
        echo -e "${RED}❌ 患者创建失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_get_patient() {
    echo -e "${BLUE}测试 3: 查询患者${NC}"
    
    # 假设患者 ID 为 1（第一个测试创建的患者）
    PATIENT_ID="${1:-1}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/commands" \
        -H "Content-Type: application/json" \
        -d "{
            \"command\": \"get_patient\",
            \"params\": {
                \"patient_id\": $PATIENT_ID
            }
        }")
    
    SUCCESS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ 患者查询成功${NC}"
        echo "$RESPONSE" | python3 -m json.tool
        echo ""
        return 0
    else
        echo -e "${YELLOW}⚠️  患者不存在或查询失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_create_ultrasound() {
    echo -e "${BLUE}测试 4: 创建超声检查${NC}"
    
    PATIENT_ID="${1:-1}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/commands" \
        -H "Content-Type: application/json" \
        -d "{
            \"command\": \"create_ultrasound\",
            \"params\": {
                \"patient_id\": $PATIENT_ID,
                \"exam_type\": \"乳腺超声\"
            }
        }")
    
    SUCCESS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ 超声检查创建成功${NC}"
        ULTRASOUND_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('ultrasound_id', ''))")
        echo "   检查 ID: $ULTRASOUND_ID"
        echo ""
        return 0
    else
        echo -e "${RED}❌ 超声检查创建失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_run_ai_inference() {
    echo -e "${BLUE}测试 5: AI 推理分析${NC}"
    
    ULTRASOUND_ID="${1:-1}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/commands" \
        -H "Content-Type: application/json" \
        -d "{
            \"command\": \"run_ai_inference\",
            \"params\": {
                \"ultrasound_id\": $ULTRASOUND_ID
            }
        }")
    
    SUCCESS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ AI 推理完成${NC}"
        echo "$RESPONSE" | python3 -m json.tool
        echo ""
        return 0
    else
        echo -e "${YELLOW}⚠️  AI 推理失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_generate_report() {
    echo -e "${BLUE}测试 6: 生成报告${NC}"
    
    PATIENT_ID="${1:-1}"
    VISIT_ID="${2:-1}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/commands" \
        -H "Content-Type: application/json" \
        -d "{
            \"command\": \"generate_report\",
            \"params\": {
                \"patient_id\": $PATIENT_ID,
                \"visit_id\": $VISIT_ID
            }
        }")
    
    SUCCESS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ 报告生成成功${NC}"
        echo "$RESPONSE" | python3 -m json.tool
        echo ""
        return 0
    else
        echo -e "${YELLOW}⚠️  报告生成失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_schedule_followup() {
    echo -e "${BLUE}测试 7: 安排随访${NC}"
    
    PATIENT_ID="${1:-1}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/commands" \
        -H "Content-Type: application/json" \
        -d "{
            \"command\": \"schedule_followup\",
            \"params\": {
                \"patient_id\": $PATIENT_ID,
                \"visit_type\": \"随访\",
                \"purpose\": \"乳腺结节复查\"
            }
        }")
    
    SUCCESS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ 随访安排成功${NC}"
        echo "$RESPONSE" | python3 -m json.tool
        echo ""
        return 0
    else
        echo -e "${RED}❌ 随访安排失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_list_followups() {
    echo -e "${BLUE}测试 8: 查询随访列表${NC}"
    
    PATIENT_ID="${1:-1}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/commands" \
        -H "Content-Type: application/json" \
        -d "{
            \"command\": \"list_followups\",
            \"params\": {
                \"patient_id\": $PATIENT_ID,
                \"limit\": 10
            }
        }")
    
    SUCCESS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ 随访列表查询成功${NC}"
        echo "$RESPONSE" | python3 -m json.tool
        echo ""
        return 0
    else
        echo -e "${RED}❌ 随访列表查询失败${NC}"
        echo "响应：$RESPONSE"
        return 1
    fi
}

test_close_session() {
    echo -e "${BLUE}测试 9: 关闭会话${NC}"
    
    RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/copilot/sessions/${SESSION_ID}/close" \
        -H "Content-Type: application/json")
    
    echo -e "${GREEN}✅ 会话已关闭${NC}"
    echo ""
}

# 帮助信息
print_help() {
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help         显示帮助信息"
    echo "  -u, --url URL      后端 API URL (默认：http://localhost:8000)"
    echo "  -t, --test TEST    运行单个测试 (可选：create_patient, get_patient, etc.)"
    echo "  -a, --all          运行所有测试"
    echo ""
    echo "示例:"
    echo "  $0 --all                      # 运行所有测试"
    echo "  $0 --test create_patient      # 只运行创建患者测试"
    echo "  $0 --url http://host:8000     # 指定后端 URL"
    echo ""
}

# 主函数
main() {
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                print_help
                exit 0
                ;;
            -u|--url)
                BACKEND_URL="$2"
                shift 2
                ;;
            -t|--test)
                TEST_NAME="$2"
                shift 2
                ;;
            -a|--all)
                RUN_ALL=true
                shift
                ;;
            *)
                echo "未知参数：$1"
                print_help
                exit 1
                ;;
        esac
    done
    
    # 创建会话
    test_create_session || exit 1
    
    # 运行单个测试
    if [ -n "$TEST_NAME" ]; then
        case $TEST_NAME in
            create_patient)
                test_create_patient
                ;;
            get_patient)
                test_get_patient
                ;;
            create_ultrasound)
                test_create_ultrasound
                ;;
            run_ai_inference)
                test_run_ai_inference
                ;;
            generate_report)
                test_generate_report
                ;;
            schedule_followup)
                test_schedule_followup
                ;;
            list_followups)
                test_list_followups
                ;;
            *)
                echo "未知测试：$TEST_NAME"
                exit 1
                ;;
        esac
        
        test_close_session
        exit 0
    fi
    
    # 运行所有测试
    if [ "$RUN_ALL" = true ]; then
        echo "=============================================="
        echo "运行完整测试流程"
        echo "=============================================="
        echo ""
        
        test_create_patient || true
        test_get_patient 1 || true
        test_create_ultrasound 1 || true
        test_run_ai_inference 1 || true
        test_generate_report 1 1 || true
        test_schedule_followup 1 || true
        test_list_followups 1 || true
        
        test_close_session
        
        echo "=============================================="
        echo -e "${GREEN}✅ 所有测试完成!${NC}"
        echo "=============================================="
        exit 0
    fi
    
    # 默认显示帮助
    print_help
}

# 执行主函数
main "$@"
