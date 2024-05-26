import requests
import json

url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json',
}

conversation_history = []

def generate_response(prompt):
    conversation_history.append(prompt)

    full_prompt = "\n".join(conversation_history)

    data = {
        "model": "mistral",
        "stream": False,
        "prompt": full_prompt,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data["response"]
        conversation_history.append(actual_response)
        return actual_response
    else:
        print("Error:", response.status_code, response.text)
        return None


def prompt(topic :str, difficulty :str = "moderate", count :int = 5, isIndep :bool = False ) -> list[str]:
    if isIndep:
        response = generate_response(f"{topic}, keep the response short and to the point, print only the response, don't print anything extra from your side, return the response in plain text do not include any bash shell section or anything similar")
        response = str(response)
        return response
    else:
        response = generate_response(f"generate {count} {difficulty} questions on {topic}, print only those questions. keep all the questions on the same line, each questions should be separated by pipe symbol. do not include the question number")
        response = str(response)
        response.replace('\n', " ")
        return organize(response)


def organize(res :str) -> None:
    questions = res.split('|')
    return questions
