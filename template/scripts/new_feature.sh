#!/usr/bin/env bash
# Scaffold the three planning docs for a new feature from dev/_templates/.
#
#   scripts/new_feature.sh user-auth
#
# Creates dev/active/user-auth/{user-auth-plan,user-auth-context,user-auth-tasks}.md.
set -euo pipefail
cd "$(dirname "$0")/.."

name="${1:?usage: scripts/new_feature.sh <feature-name>}"
if ! [[ "$name" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "error: use kebab-case (a-z, 0-9, hyphens), got '$name'" >&2
  exit 1
fi

dest="dev/active/$name"
if [ -e "$dest" ]; then
  echo "error: $dest already exists" >&2
  exit 1
fi

mkdir -p "$dest"
today="$(date +%F)"
for kind in plan context tasks; do
  sed -e "s/__FEATURE__/$name/g" -e "s/__DATE__/$today/g" \
    "dev/_templates/$kind.md" > "$dest/$name-$kind.md"
done

echo "Created $dest/"
echo "Next: fill in $name-plan.md and get it reviewed before writing code."
