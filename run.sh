docker compose up -d

echo "The browser will be opened on the app and on the API website in a few seconds..."
echo "Please wait..."
sleep 2

python -m webbrowser "http://localhost:4000/docs" && python -m webbrowser "http://localhost:8501/"