## Frontend

`cd frontend` \
`npm i` \
`npm run tauri dev`

## Backend
`cd backend` \
`python3 -m venv venv` \
`source venv/bin/activate` \
`pip install --upgrade pip` \
`pip install -r requirements.txt`\
`python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload`