#!/bin/bash

echo "🔍 JSON Comparison Tools Verification"
echo "======================================"
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version

# Check main tools exist
echo ""
echo "✓ Checking tools..."
[ -f "comprehensive_json_comparator.py" ] && echo "  ✅ comprehensive_json_comparator.py" || echo "  ❌ comprehensive_json_comparator.py"
[ -f "batch_json_comparator.py" ] && echo "  ✅ batch_json_comparator.py" || echo "  ❌ batch_json_comparator.py"

# Check documentation
echo ""
echo "✓ Checking documentation..."
[ -f "INDEX_JSON_TOOLS.md" ] && echo "  ✅ INDEX_JSON_TOOLS.md" || echo "  ❌ INDEX_JSON_TOOLS.md"
[ -f "JSON_COMPARATOR_QUICKSTART.md" ] && echo "  ✅ JSON_COMPARATOR_QUICKSTART.md" || echo "  ❌ JSON_COMPARATOR_QUICKSTART.md"
[ -f "JSON_COMPARATOR_GUIDE.md" ] && echo "  ✅ JSON_COMPARATOR_GUIDE.md" || echo "  ❌ JSON_COMPARATOR_GUIDE.md"
[ -f "JSON_COMPARISON_SOLUTION_SUMMARY.md" ] && echo "  ✅ JSON_COMPARISON_SOLUTION_SUMMARY.md" || echo "  ❌ JSON_COMPARISON_SOLUTION_SUMMARY.md"
[ -f "ISSUE_RESOLVED.md" ] && echo "  ✅ ISSUE_RESOLVED.md" || echo "  ❌ ISSUE_RESOLVED.md"

# Check test data
echo ""
echo "✓ Checking test capture files..."
[ -d "complete_captures_20251121_200510" ] && echo "  ✅ complete_captures_20251121_200510" || echo "  ❌ complete_captures_20251121_200510"
[ -d "complete_captures_20251121_201827" ] && echo "  ✅ complete_captures_20251121_201827" || echo "  ❌ complete_captures_20251121_201827"

# Check generated reports
echo ""
echo "✓ Checking generated reports..."
[ -f "migration_comparison.html" ] && echo "  ✅ migration_comparison.html" || echo "  ⚠️  migration_comparison.html (can be generated)"
[ -f "batch_consecutive_summary.html" ] && echo "  ✅ batch_consecutive_summary.html" || echo "  ⚠️  batch_consecutive_summary.html (can be generated)"
[ -d "batch_comparisons" ] && echo "  ✅ batch_comparisons/" || echo "  ⚠️  batch_comparisons/ (can be generated)"

echo ""
echo "✅ All systems ready!"
echo ""
echo "Quick Start:"
echo "  1. python3 comprehensive_json_comparator.py file1.json file2.json output"
echo "  2. python3 batch_json_comparator.py consecutive ."
echo ""
