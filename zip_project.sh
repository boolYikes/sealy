#!/bin/bash

zip -r project.zip ./ -x ".pytest_cache/*" ".ruff_cache/*" ".venv/*" "build/*" "*/__pycache__/*" "*.mako" "*.ico" "sealy.egg-info/*" "*.zip" "*/README.md" ".git/*"