from flask import Flask, request, jsonify
import requests

languages = {
    "Tamil": ("1", "ta"),
    "Telugu": ("2", "te"),
    "Kannada": ("3", "kn"),
    "Malayalam": ("4", "ml"),
    "Hindi": ("5", "hi"),
    "Gujarati": ("6", "gu"),
    "Marathi": ("7", "mr"),
    "Bengali": ("8", "bn"),
    "Punjabi": ("9", "pa"),
    "Oriya": ("10", "or"),
    "Assamese": ("11", "as")
}

app = Flask(__name__)

user_id = "user_id"
api_key = "api_key"

ulca_service_endpoint = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"


def get_translation_service_id(source_language, target_language):

    headers = {
        "userID": user_id,
        "ulcaApiKey": api_key,
    }

    ulca_service_request_payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": source_language,
                        "targetLanguage": target_language
                    }
                }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": "64392f96daac500b55c543cd"
        }
    }

    ulca_service_response = requests.post(ulca_service_endpoint, json=ulca_service_request_payload, headers=headers)

    if ulca_service_response.status_code == 200:
        ulca_service_data = ulca_service_response.json()
        service_id = ulca_service_data.get("pipelineResponseConfig")[1].get("config")[0].get("serviceId")
        return service_id

    return None


@app.route('/scaler/translate', methods=['POST'])
def translate_text():
    try:
        data = request.json
        source_language = data.get("source_language")
        target_language = data.get("target_language")
        content = data.get("content")

        Service_id = get_translation_service_id(source_language, target_language)

        if Service_id:
            headers = {
                "userID": user_id,
                "ulcaApiKey": api_key,
            }

            ulca_request_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language,
                                "targetLanguage": target_language
                            },
                            "serviceId": Service_id
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": content
                        }
                    ],
                    "audio": [
                        {
                            "audioContent": None
                        }
                    ]
                }
            }

            ulca_response = requests.post(ulca_service_endpoint, json=ulca_request_payload, headers=headers)

            if ulca_response.status_code == 200:
                ulca_response_data = ulca_response.json()
                translated_content = ulca_response_data.get("pipelineResponse")[0].get("output")[0].get("target")
                return jsonify(
                    {"status_code": 200, "message": "Translation successful", "translated_content": translated_content})

        return jsonify({"status_code": 500, "message": "Failed to obtain service ID or translation failed"})

    except Exception as e:
        return jsonify({"status_code": 500, "message": "Internal Server Error: " + str(e)})


if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)
