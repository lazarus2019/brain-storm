#!/usr/bin/env bash

TEMPLATE_DIR="_template"

generate_docs() {
  echo "Generating documentation..."
  
  mkdir -p ./$1
  
  cp -r "$TEMPLATE_DIR"/* ./$1/

  CATEGORY_UPPERCASE=$(echo "$1" | tr '[:lower:]' '[:upper:]')

  mv ./$1/docs/DOC_1.md ./$1/docs/${CATEGORY_UPPERCASE}.md
}

if [ "$#" -eq 1 ]; then
  generate_docs $1
else
  echo "Usage: $0 <category>"
  echo "Example: $0 api"
fi