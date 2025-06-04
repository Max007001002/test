# WAN I2V Demo
demo-wan-i2v/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── main.jsx
│   ├── public/
│   ├── app/
│   ├── node_modules/
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── start_script_frontend.sh
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── worker.py
│   ├── uploads/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── start_script_backend.sh
│
├── infra/
│   └── docker-compose.yml
│
├── node_modules/
├── package.json
├── package-lock.json
└── README.md
```

в папке infra (в терминале) прпоисываем docker-compose up --build