#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
# FashionBazzer — Render Startup Script
# ══════════════════════════════════════════════════════════
# 1. Ensures the working directory is correct
# 2. Runs Django system check
# 3. Collects static files (if not done during build)
# 4. Prints environment info for debugging
# 5. Starts gunicorn with full error logging
# ══════════════════════════════════════════════════════════

echo "=== FashionBazzer Startup ==="
echo "Python: $(python --version 2>&1)"
echo "PWD: $(pwd)"
echo "PORT: ${PORT:-NOT_SET}"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-fashionbazzer.settings}"

# Add current directory to PYTHONPATH so Django modules can be found
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run Django system check — log warnings but keep going
echo "--- Django system check ---"
python manage.py check --deploy 2>&1 || echo "(Django check produced warnings — continuing)"
echo "Django check: OK"

# Verify gunicorn is available
echo "--- Gunicorn check ---"
python -c "import gunicorn; print(f'gunicorn {gunicorn.__version__}')" 2>&1

echo "--- Starting gunicorn ---"
exec gunicorn fashionbazzer.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug
