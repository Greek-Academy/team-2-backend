from fastapi import FastAPI
from pydantic import BaseModel
import openai
import json

app = FastAPI()


def sum_numbers(num_a, num_b):
    result = {
        "num_a": num_a,
        "num_b": num_b,
        "summation_result": str(num_a + num_b)
    }
    return json.dumps(result, ensure_ascii=False)


def multiply_numbers(num_a, num_b):
    result = {
        "num_a": num_a,
        "num_b": num_b,
        "multiplication_result": str(num_a * num_b)
    }
    return json.dumps(result, ensure_ascii=False)


def subtract_numbers(num_a, num_b):
    result = {
        "num_a": num_a,
        "num_b": num_b,
        "subtraction_result": str(num_a - num_b)
    }
    return json.dumps(result, ensure_ascii=False)


def divide_numbers(num_a, num_b):
    result = {
        "num_a": float(num_a),
        "num_b": float(num_b),
        "division_result": str(num_a / num_b)
    }
    return json.dumps(result, ensure_ascii=False)


def call_gpt(user_query, message, func, function_name, function_response):
    msg = list()
    msg.append({"role": "user", "content": user_query})

    if message is not None:
        msg.append(message)

    if function_name is not None:
        msg.append({
            "role": "function",
            "name": function_name,
            "content": function_response,
        })

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=msg,
        functions=func,
        function_call="auto",
    )

    return response


def run_conversation(user_query):

    operations = [
        ("sum_numbers", "sum"),
        ("multiply_numbers", "multiply"),
        ("subtract_numbers", "subtract"),
        ("divide_numbers", "divide")
    ]

    func = [{
        "name": op_name,
        "description": f"To {op_desc} two numbers, num_a and num_b",
        "parameters": {
            "type": "object",
            "properties": {
                "num_a": {"type": "string", "description": "first number"},
                "num_b": {"type": "string", "description": "second number"}
            },
            "required": ["num_a", "num_b"]
        }
    } for op_name, op_desc in operations]

    response = call_gpt(user_query=user_query, message=None, func=func, function_name=None, function_response=None)
    message = response["choices"][0]["message"]

    count = 1
    print(f"ChatGPTからの{count}回目のレスポンスを受信: {response}\n")
    while "function_call" in message:
        function_name = message["function_call"]["name"]
        args = json.loads(message["function_call"]["arguments"])
        num_a, num_b = float(args["num_a"]), float(args["num_b"])

        function_response = "none"

        if function_name == "multiply_numbers":
            function_response = multiply_numbers(num_a, num_b)
        elif function_name == "subtract_numbers":
            function_response = subtract_numbers(num_a, num_b)
        elif function_name == "divide_numbers":
            function_response = divide_numbers(num_a, num_b)

        response = call_gpt(user_query=user_query, message=message, func=func, function_name=function_name,
                            function_response=function_response)

        message = response["choices"][0]["message"]

        count += 1
        print(f"ChatGPTからの{count}回目のレスポンスを受信: {response}\n")

    return message["content"]


class AgentResponse(BaseModel):
    result: str


class ConversationAgentRequest(BaseModel):
    content: str


@app.post("/agents/conversation", response_model=AgentResponse)
async def conversation_agent(request: ConversationAgentRequest):
    response = run_conversation(request.content)

    return {"result": response}


# Define root API
@app.get("/")
def read_root():
    return {"Hello": "World"}
