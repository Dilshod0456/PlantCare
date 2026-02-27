#!/bin/bash
# PlantCare Deployment Script

set -e  # Exit on error

echo "🚀 Starting PlantCare deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create .env file from .env.example and configure it."
    exit 1
fi

# Check if required environment variables are set
echo -e "${YELLOW}Checking environment variables...${NC}"
source .env

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here-change-in-production" ]; then
    echo -e "${RED}❌ Error: SECRET_KEY not configured in .env${NC}"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your-gemini-api-key-here" ]; then
    echo -e "${YELLOW}⚠️  Warning: GEMINI_API_KEY not configured. AI features will not work.${NC}"
fi

# Check if models exist
echo -e "${YELLOW}Checking ML models...${NC}"
if [ ! -f "models/plant_disease_model.h5" ]; then
    echo -e "${RED}❌ Error: ML model not found at models/plant_disease_model.h5${NC}"
    exit 1
fi

if [ ! -f "models/class_indices.json" ]; then
    echo -e "${RED}❌ Error: Class indices not found at models/class_indices.json${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Models found${NC}"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Install/update dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
pip install gunicorn whitenoise

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Create logs directory
mkdir -p logs

# Check for superuser
echo -e "${YELLOW}Checking for superuser...${NC}"
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')"

# Run tests (optional)
if [ "$RUN_TESTS" = "true" ]; then
    echo -e "${YELLOW}Running tests...${NC}"
    python manage.py test
fi

# Start application
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Starting Gunicorn server...${NC}"
echo "Application will be available at http://0.0.0.0:8000"
echo "Press Ctrl+C to stop"
echo ""

gunicorn PlantCare.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    --log-level info \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50
