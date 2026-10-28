# CodeCraftHub

CodeCraftHub es una plataforma de aprendizaje personalizada para que desarrolladores organicen y sigan los cursos que desean completar. El proyecto está pensado para practicar los fundamentos de las API REST con Python y Flask, sin base de datos ni autenticación.

## Funciones principales

Cada curso incluye:

- **Nombre**
- **Descripción**
- **Fecha objetivo de finalización**
- **Estado:** `No iniciado`, `En progreso` o `Completado`

La información se almacena en un archivo JSON local.

## Requisitos

- Python 3.9 o superior
- Flask

## Estructura del proyecto

Una estructura sencilla para empezar:

```text
CodeCraftHub/
├── app.py
├── requirements.txt
├── data/
│   └── courses.json
└── README.md