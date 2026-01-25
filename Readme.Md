# FastAPI Starter Pack

This is a **simple FastAPI repository** for learning and building basic APIs using Python.

<img width="1420" height="947" alt="Image" src="https://github.com/user-attachments/assets/643db94b-a51f-425d-9b2d-9a3ef16d1f1e" />

---

## Features

- FastAPI framework
- Simple REST APIs
- Automatic Swagger documentation
- Easy to understand project structure
- Beginner friendly

---

## Requirements

- Python 3.8+
- pip

---

## Installation

### Clone the repository

```bash
git clone https://github.com/Md-Emon-Hasan/FastAPI
cd FastAPI
````

---

### Create virtual environment

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac / Linux
```

---

### Install dependencies

```bash
pip install fastapi uvicorn
```

Or using requirements file:

```bash
pip install -r requirements.txt
```

---

## Run the App

```bash
uvicorn main:app --reload
```

App will run on:

```
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI provides built-in API docs:

* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

* ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Example Endpoint

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello FastAPI"}
```

---

## License

MIT License

---

## Author

**Md. Hasan Imon**<br>
Email: [emon.mlengineer@gmail.com](mailto:emon.mlengineer@gmail.com)<br>
Github: [https://github.com/Md-Emon-Hasan](https://github.com/Md-Emon-Hasan)