#!/bin/bash
cd /home/kavia/workspace/code-generation/resume-analyzer-and-job-matcher-214036-214047/resume_app_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

