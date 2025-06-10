from flask import Blueprint, jsonify, request

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/messages', methods=['GET'])
def get_messages(language = None):

    pass

@api_bp.route('/message', methods=['POST'])
def resource(resource_id):
    pass

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@api_bp.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500
