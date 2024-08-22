# setup.sh

#!/bin/bash

HOOKS_DIR=$(git rev-parse --show-toplevel)/.git/hooks

echo "Setting up pre-commit hook..."
cp hooks/precommit.py $HOOKS_DIR/pre-commit
chmod +x $HOOKS_DIR/pre-commit
echo "Pre-commit hook installed."
