from flask import Flask, jsonify, request
from pathlib import Path
from datetime import datetime
import json
import uuid

app = Flask(__name__)

DATA_FILE = Path("data/courses.json")

VALID_STATUSES = {
    "No iniciado",
    "En progreso",
    "Completado"
}


def ensure_data_file():
    """
    Crea la carpeta y el archivo JSON si todavía no existen.
    """
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def read_courses():
    """
    Lee todos los cursos desde el archivo JSON.
    """
    ensure_data_file()

    try:
        content = DATA_FILE.read_text(encoding="utf-8")

        if not content.strip():
            return []

        return json.loads(content)

    except json.JSONDecodeError:
        return []


def write_courses(courses):
    """
    Guarda todos los cursos en el archivo JSON.
    """
    ensure_data_file()

    DATA_FILE.write_text(
        json.dumps(courses, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def is_valid_date(date_string):
    """
    Verifica que la fecha tenga el formato YYYY-MM-DD.
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def validate_course_data(data, partial=False):
    """
    Valida los campos recibidos en una petición.
    """
    if not isinstance(data, dict):
        return "El cuerpo de la petición debe ser un objeto JSON."

    required_fields = [
        "name",
        "description",
        "target_completion_date",
        "status"
    ]

    if not partial:
        missing_fields = [
            field for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return f"Faltan campos requeridos: {', '.join(missing_fields)}"

    if "name" in data and not isinstance(data["name"], str):
        return "El campo 'name' debe ser texto."

    if "description" in data and not isinstance(data["description"], str):
        return "El campo 'description' debe ser texto."

    if "target_completion_date" in data:
        if not is_valid_date(data["target_completion_date"]):
            return (
                "El campo 'target_completion_date' debe tener "
                "el formato YYYY-MM-DD."
            )

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return (
                "El campo 'status' debe ser uno de: "
                + ", ".join(VALID_STATUSES)
            )

    return None


@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "message": "CodeCraftHub API está funcionando"
    })


@app.get("/api/courses")
def get_courses():
    courses = read_courses()
    return jsonify(courses), 200


@app.get("/api/courses")
def get_course(course_id):
    courses = read_courses()

    course = next(
        (course for course in courses if course["id"] == course_id),
        None
    )

    if course is None:
        return jsonify({
            "error": "Curso no encontrado"
        }), 404

    return jsonify(course), 200


@app.post("/api/courses")
def create_course():
    data = request.get_json(silent=True)

    error = validate_course_data(data)

    if error:
        return jsonify({"error": error}), 400

    courses = read_courses()

    new_course = {
        "id": str(uuid.uuid4()),
        "name": data["name"],
        "description": data["description"],
        "target_completion_date": data["target_completion_date"],
        "status": data["status"]
    }

    courses.append(new_course)
    write_courses(courses)

    return jsonify(new_course), 201


@app.put("/api/courses")
def replace_course(course_id):
    data = request.get_json(silent=True)

    error = validate_course_data(data)

    if error:
        return jsonify({"error": error}), 400

    courses = read_courses()

    for index, course in enumerate(courses):
        if course["id"] == course_id:
            replaced_course = {
                "id": course_id,
                "name": data["name"],
                "description": data["description"],
                "target_completion_date": data["target_completion_date"],
                "status": data["status"]
            }

            courses[index] = replaced_course
            write_courses(courses)

            return jsonify(replaced_course), 200

    return jsonify({
        "error": "Curso no encontrado"
    }), 404


@app.patch("/api/courses")
def update_course(course_id):
    data = request.get_json(silent=True)

    error = validate_course_data(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    courses = read_courses()

    for course in courses:
        if course["id"] == course_id:
            allowed_fields = [
                "name",
                "description",
                "target_completion_date",
                "status"
            ]

            for field in allowed_fields:
                if field in data:
                    course[field] = data[field]

            write_courses(courses)

            return jsonify(course), 200

    return jsonify({
        "error": "Curso no encontrado"
    }), 404


@app.delete("/api/courses")
def delete_course(course_id):
    courses = read_courses()

    updated_courses = [
        course for course in courses
        if course["id"] != course_id
    ]

    if len(updated_courses) == len(courses):
        return jsonify({
            "error": "Curso no encontrado"
        }), 404

    write_courses(updated_courses)

    return jsonify({
        "message": "Curso eliminado correctamente"
    }), 200


if __name__ == "__main__":
    ensure_data_file()
    app.run(debug=True)