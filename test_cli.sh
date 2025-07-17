#!/bin/bash
# SRRD-Builder CLI Test Script
# Tests all CLI commands in a temporary project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0

echo -e "${BLUE}🧪 SRRD-Builder CLI Test Suite${NC}"
echo "=================================="

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Testing $test_name... "
    
    if output=$(eval "$test_command" 2>&1); then
        if [[ -z "$expected_pattern" ]] || echo "$output" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✅ PASS${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            return 0
        else
            echo -e "${RED}❌ FAIL${NC} (pattern not found: $expected_pattern)"
            echo "Output: $output"
            return 1
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (command failed)"
        echo "Output: $output"
        return 1
    fi
}

# Function to check if file exists
check_file() {
    local file_path="$1"
    local description="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Checking $description... "
    
    if [[ -f "$file_path" ]]; then
        echo -e "${GREEN}✅ EXISTS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ MISSING${NC} ($file_path)"
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    local dir_path="$1"
    local description="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Checking $description... "
    
    if [[ -d "$dir_path" ]]; then
        echo -e "${GREEN}✅ EXISTS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ MISSING${NC} ($dir_path)"
        return 1
    fi
}

# Get the SRRD root directory (where this script is called from)
SRRD_ROOT=$(pwd)
echo "SRRD Root: $SRRD_ROOT"

# Create temporary test directory
TEST_DIR=$(mktemp -d)
echo "Test Directory: $TEST_DIR"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up test directory: $TEST_DIR${NC}"
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Change to test directory
cd "$TEST_DIR"

# Initialize Git repository (required for SRRD)
echo -e "\n${BLUE}📁 Setting up test project${NC}"
git init --quiet
git config user.email "test@srrd-builder.test"
git config user.name "SRRD Test"

# Add some initial content
echo "# Test Research Project" > README.md
git add README.md
git commit -m "Initial commit" --quiet

echo -e "${GREEN}✅ Test project initialized${NC}"

# Activate virtual environment and ensure SRRD is available
cd "$SRRD_ROOT"
source venv/bin/activate
export PATH="$SRRD_ROOT/venv/bin:$PATH"
cd "$TEST_DIR"

echo -e "\n${BLUE}🔧 Testing CLI Help Commands${NC}"
run_test "srrd --help" "srrd --help" "Scientific Research Requirement Document Builder"
run_test "srrd init --help" "srrd init --help" "Research domain"
run_test "srrd generate --help" "srrd generate --help" "Generation actions"
run_test "srrd publish --help" "srrd publish --help" "Name of draft to publish"
run_test "srrd serve --help" "srrd serve --help" "Server actions"
run_test "srrd configure --help" "srrd configure --help" "Configure Claude Desktop"

echo -e "\n${BLUE}🏗️  Testing Project Initialization${NC}"
run_test "srrd init (physics, standard)" "srrd init --domain physics --template standard" "SRRD-Builder project initialized successfully"

# Check project structure
echo -e "\n${BLUE}📁 Verifying Project Structure${NC}"
check_dir ".srrd" ".srrd directory"
check_dir "work" "work directory"
check_dir "work/drafts" "work/drafts directory"  
check_dir "work/research" "work/research directory"
check_dir "work/data" "work/data directory"
check_dir "publications" "publications directory"
check_file ".srrd/config.json" ".srrd/config.json"
check_file ".gitignore" ".gitignore"

# Check if config has correct domain
if [[ -f ".srrd/config.json" ]]; then
    run_test "config contains physics domain" "grep '\"domain\": \"physics\"' .srrd/config.json" '"domain": "physics"'
fi

echo -e "\n${BLUE}📝 Testing Template Generation${NC}"
run_test "generate proposal template" "srrd generate template proposal --title 'Test Proposal'" "LaTeX template generated"
check_file "work/drafts/test_proposal.tex" "proposal template file"

run_test "generate paper template" "srrd generate template paper --title 'Test Paper'" "LaTeX template generated"
check_file "work/drafts/test_paper.tex" "paper template file"

run_test "generate thesis template" "srrd generate template thesis --title 'Test Thesis'" "LaTeX template generated" 
check_file "work/drafts/test_thesis.tex" "thesis template file"

echo -e "\n${BLUE}🔨 Testing PDF Generation${NC}"
# Only test if pdflatex is available
if command -v pdflatex &> /dev/null; then
    run_test "compile proposal to PDF" "srrd generate pdf work/drafts/test_proposal.tex" "PDF generated:"
    check_file "work/drafts/test_proposal.pdf" "compiled proposal PDF"
else
    echo -e "${YELLOW}⚠️  Skipping PDF tests (pdflatex not available)${NC}"
fi

echo -e "\n${BLUE}📚 Testing Publication Workflow${NC}"
# Test publish command
run_test "publish test proposal" "srrd publish test_proposal --version v1.0" "Publication complete"
check_dir "publications/test_proposal" "published proposal directory"
check_file "publications/test_proposal/test_proposal.tex" "published proposal LaTeX"

# Check if README was updated
if [[ -f "README.md" ]]; then
    run_test "README updated with publication" "grep 'test_proposal' README.md" "test_proposal"
fi

# Check Git tag creation
run_test "Git tag created" "git tag -l" "test_proposal-v1.0"

echo -e "\n${BLUE}⚙️  Testing Server Management${NC}"
# Test server commands (without actually starting server)
run_test "server status check" "srrd configure --status" "MCP Configuration Status"

echo -e "\n${BLUE}🔄 Testing Force Reinit${NC}"
run_test "force reinit" "srrd init --domain cs --template minimal --force" "SRRD-Builder project initialized successfully"

# Check that domain was updated
if [[ -f ".srrd/config.json" ]]; then
    run_test "config updated to cs domain" "grep '\"domain\": \"cs\"' .srrd/config.json" '"domain": "cs"'
fi

echo -e "\n${BLUE}❌ Testing Error Cases${NC}"
# Test init in non-git directory - create completely separate directory
NOGIT_DIR=$(mktemp -d)
cd "$NOGIT_DIR"
run_test "init fails without git" "python -m srrd_builder.cli.main init 2>&1 || true" "Not in a Git repository"
cd "$TEST_DIR"
rm -rf "$NOGIT_DIR"

# Test publish non-existent draft
run_test "publish fails for missing draft" "srrd publish nonexistent 2>&1 || true" "Draft not found"

# Test generate PDF with non-existent file
run_test "generate PDF fails for missing file" "srrd generate pdf nonexistent.tex 2>&1 || true" "File not found"

echo -e "\n${BLUE}📊 Test Results${NC}"
echo "=================================="
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $((TESTS_RUN - TESTS_PASSED))"

if [[ $TESTS_PASSED -eq $TESTS_RUN ]]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
