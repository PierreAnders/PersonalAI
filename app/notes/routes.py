from app.notes import bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app.notes.service import add_note_service
from werkzeug.exceptions import BadRequest

@bp.route('/notes', methods=['POST'])
@jwt_required()
def add_note():
    try:
        data = request.get_json()

        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            raise BadRequest("Title and content are required.")

        user_id = get_jwt_identity()

        result, status_code = add_note_service(title, content, user_id)

        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


