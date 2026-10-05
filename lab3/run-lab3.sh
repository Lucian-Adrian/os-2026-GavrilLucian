#!/bin/bash
# Test harness for Laboratory 3 verification
set -e

echo "=== Verifying Laboratory 3 Deliverables ==="

# 1. Check access.log line count
if [ ! -f "access.log" ]; then
    echo "ERROR: access.log not found!" >&2
    exit 1
fi
LINES=$(wc -l < access.log)
echo "access.log line count: $LINES (Expected: 500)"
if [ "$LINES" -ne 500 ]; then
    echo "ERROR: Line count mismatch!" >&2
    exit 1
fi

# 2. Run oneliners.sh
echo "=== Running oneliners.sh ==="
bash oneliners.sh

# 3. Test report.sh on access.log
echo "=== Running report.sh on access.log ==="
bash report.sh access.log

# 4. Test report.sh error handling
echo "=== Running report.sh error case ==="
set +e
bash report.sh nonexistent.log
ERR_CODE=$?
set -e
echo "Error exit code: $ERR_CODE (Expected: 1)"

echo "=== All Laboratory 3 checks passed successfully ==="
