#!/bin/bash
#
# Run tests with proper isolation by running test directories individually
#

cd "$(dirname "$0")"

echo "🧪 Running SRRD-Builder comprehensive test suite (with test isolation)..."
echo "======================================================================="

# Define test directories to run individually for proper isolation
test_directories=(
    "work/tests/unit/"
    "work/tests/integration/"
    "work/tests/validation/"
)

# Track overall results
total_failed=0
total_passed=0
failed_directories=()

# Run each test directory separately for complete isolation
for test_dir in "${test_directories[@]}"; do
    if [ -d "$test_dir" ]; then
        echo ""
        echo "🔍 Running tests in $test_dir..."
        echo "----------------------------------------"
        
        # Color variables
        GREEN='\033[0;32m'
        RED='\033[0;31m'
        YELLOW='\033[1;33m'
        NC='\033[0m' # No Color

        # Run pytest with color output and capture to temp file
        test_output=$(mktemp)
        timeout 120s python3 -m pytest "$test_dir" --tb=short -v --color=yes | tee "$test_output"
        exit_code=${PIPESTATUS[0]}

        # Check for failures or errors in output
        if grep -qE "FAILED|ERRORS" "$test_output"; then
            if [ $exit_code -eq 124 ]; then
                echo -e "\n${YELLOW}⏰ $test_dir: TIMEOUT (exit code: $exit_code)${NC}"
            else
                echo -e "\n${RED}❌ $test_dir: FAILED (exit code: $exit_code)${NC}"
            fi
            ((total_failed++))
            failed_directories+=("$test_dir")
        elif [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✅ $test_dir: PASSED${NC}"
            ((total_passed++))
        else
            if [ $exit_code -eq 124 ]; then
                echo -e "\n${YELLOW}⏰ $test_dir: TIMEOUT (exit code: $exit_code)${NC}"
            else
                echo -e "\n${RED}❌ $test_dir: FAILED (exit code: $exit_code)${NC}"
            fi
            ((total_failed++))
            failed_directories+=("$test_dir")
        fi
        rm -f "$test_output"
        
        # Small delay between test directories to ensure cleanup
        sleep 1
    else
        echo "⚠️  Test directory $test_dir not found, skipping..."
    fi
done

echo ""
echo "📊 Test Summary:"
echo "=================="
echo "✅ Passed directories: $total_passed"
echo "❌ Failed directories: $total_failed"

if [ $total_failed -gt 0 ]; then
    echo ""
    echo "Failed test directories:"
    for dir in "${failed_directories[@]}"; do
        echo "  - $dir"
    done
    echo ""
    echo "❌ Some tests failed!"
    exit 1
else
    echo ""
    echo "🎉 All test directories passed successfully!"
    echo "✅ Complete test suite PASSED with proper isolation!"
    exit 0
fi
