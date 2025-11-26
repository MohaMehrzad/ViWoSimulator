module.exports = {
  apps: [
    {
      name: 'viwo-frontend',
      cwd: '/var/www/ViWoSimulator/frontend',
      script: 'node_modules/.bin/next',
      args: 'start -p 3025',
      env: {
        NODE_ENV: 'production',
        NEXT_PUBLIC_API_URL: 'https://viwoapp.info/api',
        NEXT_PUBLIC_WS_URL: 'wss://viwoapp.info/api'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    },
    {
      name: 'viwo-backend',
      cwd: '/var/www/ViWoSimulator/backend',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 127.0.0.1 --port 8025',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    }
  ]
};

