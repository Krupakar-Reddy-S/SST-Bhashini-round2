import requests
import json

user_id = input("Enter your user ID: ")
api_key = input("Enter your API key: ")

jsonFile = open('request.json', 'r')
json_object = json.load(jsonFile)

source_language = json_object["source_language"]
target_language = json_object["target_language"]
content = json_object["content"]

jsonFile.close()

ulca_service_endpoint = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
ulca_compute_endpoint = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"


def get_translation_service_id():

    headers_config = {
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

    ulca_service_response = requests.post(ulca_service_endpoint, json=ulca_service_request_payload, headers=headers_config)

    if ulca_service_response.status_code == 200:
        ulca_service_data = ulca_service_response.json()

        for config in ulca_service_data.get("pipelineResponseConfig"):
            if config.get("taskType") == "translation":
                service_id = config.get("config")[0].get("serviceId")
                return service_id

    return None


Service_id = get_translation_service_id()

if Service_id:

    headers_compute = {
        "Authorization": "A5h_wqQm-PPb_fTbgRXAastGC1DOa-d8jG8V6uxfSN7XwetraaF29lOMGS9zxszL"
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
                    "audioContent": json.dumps(None)
                }
            ]
        }
    }

    ulca_response = requests.post(ulca_compute_endpoint, json=ulca_request_payload, headers=headers_compute)

    if ulca_response.status_code == 200:
        ulca_response_data = ulca_response.json()

        with open("translation_response.json", "w") as response_file:
            json.dump(ulca_response_data, response_file, indent=4)

    else:
        print("Translation failed")
else:
    print("Failed to obtain service ID")
