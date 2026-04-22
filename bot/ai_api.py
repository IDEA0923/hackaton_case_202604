from openai import AsyncOpenAI
import env
import alerts
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=env.OPENROUTER_API_KEY
)

async def  get_AI_answer(request : str):
    try:
        response = await client.chat.completions.create(
                model="openrouter/elephant-alpha",
                messages=[
                    {"role": "user", "content": request}
                ]
            )
        return response.choices[0].message.content
    except Exception as e :
        print("[-]API ERROR")
        await alerts.alert_for_all_admins(f"[-]API ERROR : \n<blockquote>{e}</blockquote>\n")
        return "Sorry , but we have some trouble with AI"
        