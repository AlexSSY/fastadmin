Python 3.9.21


{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [

        {
            "name": "Python: Debug FastAPI with Uvicorn",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app:app",
                "--reload",
                "--host",
                "127.0.0.1",
                "--port",
                "8000"
            ],
            "jinja": true,
            "console": "integratedTerminal"
        }
    ]
}