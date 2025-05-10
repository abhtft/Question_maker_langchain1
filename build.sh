#!/bin/bash

echo "Starting build process..."

python -m venv venv

source venv/bin/activate
#for windows
venv\Scripts\activate

venv\Scripts\deactivate

# Upgrade pip and install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt && npm run build && python app.py #always use user word
python check_requirements.py
python test_langchain.py

npm run build && python app.py

#first should check backend testing





npm install
npm run build


if [ ! -d "dist" ]; then
    echo "Error: dist directory not found after build"
    exit 1
fi

if [ ! -f "dist/index.html" ]; then
    echo "Error: index.html not found in dist directory"
    exit 1
fi

echo "Build completed successfully!" 
# Run the server
python server.py