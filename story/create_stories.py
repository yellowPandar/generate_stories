import streamlit as st
import json
import openai
from pydantic import BaseModel, Field
import io
import os
from PIL import Image
from stability_sdk import client as stability_client

openai.api_key = os.environ["GPT_KEY"]

class Story(BaseModel):
    contents: str = Field(
        description="内容", examples=["昔あるところに、黄色のうさぎがいました。", "黄色のうさぎは、ある日森の中で道に迷ってしまいました。"]
    )

class Illustration(BaseModel):
    in_english: str = Field(description="挿絵")

# おはなし作成
STORY_PROMPT_TEMPLATE = """
    下記の####で区切られたユーザーからの入力文章があります。
    入力文章から、5歳児向けの物語を考えてください。300字以内でお願いします。
    入力文章は以下の通り
    ####
    {user_input}
    ####
"""

STORY_OUTPUT_FUNCTION = {
    "name": "output_story",
    "description": "物語を出力する",
    "parameters": Story.schema(),
}
# 挿絵生成
IMAGE_PROMPT_TEMPLATE = """
    下記の####で区切られたユーザーからの入力文章があります。
    入力文章を、Dream studioに入力するプロンプトに変換してください。出力は、英語で、Dream studio に入力するプロンプトのみでお願いします。
    入力文章は以下の通り
    ####
    {user_input}
    ####
"""

IMAGE_OUTPUT_FUNCTION = {
    "name": "output_image",
    "description": "挿絵を出力する",
    "parameters": Illustration.schema(),
}

def get_chatgpt_response(
    user_input: str,
    input_template: str,
    output_func: str,
    # model: str = "gpt-3.5-turbo-0613",
    model: str = "gpt-4",
    temperature: float = 0,
    max_tokens: int = 500,
):
    """
    ChatGPTに対して対話を投げかけ、返答を取得する
    """
    prompt = input_template.format(user_input=user_input)
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        functions=[output_func],
        function_call={"name": output_func["name"]},
    )
    return response


st.title("物語生成AI")

user_input = st.text_input(label="キーワード")
user_input=str(user_input)

if user_input:
    with st.spinner(text="生成中..."):

        response_stories = get_chatgpt_response(user_input, STORY_PROMPT_TEMPLATE,STORY_OUTPUT_FUNCTION)

        response_message = response_stories["choices"][0]["message"]
        function_call_args = response_message["function_call"]["arguments"]


        story = json.loads(function_call_args)
        
        # 以下の形式のマークダウンの文字列を作成して表示
        #
        # ## おはなし
        # 昔あるところに、黄色のうさぎがいました。
        # 黄色のうさぎは、ある日森の中で道に迷ってしまいました。
        instructions_markdown = "## おはなし\n"
        instructions_markdown += (story["contents"]+"\n")
        st.write(instructions_markdown)

        # 画像生成
        st.write("## 挿絵")
        response_image = get_chatgpt_response(user_input, IMAGE_PROMPT_TEMPLATE,IMAGE_OUTPUT_FUNCTION)

        response_capture = response_image["choices"][0]["message"]
        function_call_args_capture = response_capture["function_call"]["arguments"]
        illustration = json.loads(function_call_args_capture)

        stability_api = stability_client.StabilityInference(
            key=os.environ["STABILITY_KEY"], engine="stable-diffusion-512-v2-1"
        )

        answers = stability_api.generate(
            prompt=illustration["in_english"], height=512, width=512, samples=1
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == stability_client.generation.FILTER:
                    st.warning("画像を生成できませんでした")
                if artifact.type == stability_client.generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    st.image(img)

