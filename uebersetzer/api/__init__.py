import json
import os
from datetime import datetime
from typing import List

from flask import Blueprint, jsonify, request
from mistralai import Mistral

from ..database.db import Message

chat_api = Blueprint('chat_api', __name__, url_prefix='/api/')


@chat_api.route('/messages', methods=['GET'])
def get_messages():
    """Get all chat messages"""
    messages: List[Message] = Message.get_all_messages()
    return jsonify({"messages": [message.to_dict() for message in messages]}), 200


@chat_api.route('/messages', methods=['POST'])
def post_message():
    """Post a new message to the chat"""
    data = request.json

    if not data or 'content' not in data or 'author' not in data or 'language' not in data:
        return jsonify({"error": "Message must contain content, author, and language"}), 400

    translate = data.get('translate', True)

    message = Message.create_new(
        content=data['content'],
        timestamp=datetime.now(),
        author=data['author'],
        language=data['language'],
        translate=translate
    )

    return jsonify(message.to_dict()), 201


@chat_api.route('/messages/translate/<int:message_id>/<string:target_language>', methods=['POST', 'GET'])
def translate_message(message_id, target_language):
    """Translate a message by its ID"""
    message = Message.get_via_id(message_id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    # Initialize Mistral API client
    api_key = os.environ.get("MISTRAL_API_KEY")

    # Prepare the translation request JSON
    translation_request = {
        "text": message.content,
        "target_lang": target_language,
        "id": message_id
    }

    # Send the request to the Mistral agent with the JSON structure
    with Mistral(api_key=api_key) as mistral:
        response = mistral.agents.complete(
            agent_id="ag:9195f226:20250610:untitled-agent:0cfcafcd",
            messages=[
                {
                    "role": "user",
                    "content": f"{translation_request}"
                }
            ]
        )

    # Parse response which is structured as a list with a dict containing text and id
    try:
        response_content = json.loads(response.choices[0].message.content)
        translated_text = response_content[0]['text'] if response_content else ""
    except (json.JSONDecodeError, IndexError, KeyError):
        # Fallback if parsing fails
        translated_text = response.choices[0].message.content

    try:
        if isinstance(translated_text, str):
            translated_dict = json.loads(translated_text)
        else:
            translated_dict = translated_text

        translated_text = translated_dict.get("text", "")
        if not translated_text:
            return jsonify({"error": "Translation error: Missing text field"}), 500
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        return jsonify({"error": f"Translation error: {str(e)}"}), 500

    return jsonify({"translated_text": translated_text, "id": message_id}), 200
