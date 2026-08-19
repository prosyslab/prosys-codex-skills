#!/bin/bash

set -euo pipefail

SOURCE_DIR=$(pwd -P)
SKILLS_DIR="$HOME/.codex/skills"

mkdir -p "$SKILLS_DIR"

for skill_path in "$SOURCE_DIR"/*; do
  [ -d "$skill_path" ] || continue

  skill_name=$(basename "$skill_path")
  target_path="$SKILLS_DIR/$skill_name"

  # Do not let ln create a link inside an existing directory.
  if [ -e "$target_path" ] || [ -L "$target_path" ]; then
    echo "Skipping existing skill path: $target_path"
    continue
  fi

  echo "Creating symbolic link for skill: $skill_name in $SKILLS_DIR"
  ln -s "$skill_path" "$target_path"
done
