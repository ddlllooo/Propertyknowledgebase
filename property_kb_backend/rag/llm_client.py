import os

from rag.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    load_env_files,
)


class DeepSeekClientError(RuntimeError):
    pass


_client = None
_client_config = None


def get_deepseek_settings():
    load_env_files()
    return {
        "api_key": os.getenv("DEEPSEEK_API_KEY", DEEPSEEK_API_KEY).strip(),
        "base_url": os.getenv("DEEPSEEK_BASE_URL", DEEPSEEK_BASE_URL).strip(),
        "model": os.getenv("DEEPSEEK_MODEL", DEEPSEEK_MODEL).strip(),
    }


def is_missing_api_key(api_key):
    return not api_key or api_key in {"sk-xxxx", "sk-xxx", "your-api-key"}


def get_deepseek_client(settings):
    global _client, _client_config
    client_config = (settings["api_key"], settings["base_url"])
    if _client is None or _client_config != client_config:
        from openai import OpenAI

        _client = OpenAI(
            api_key=settings["api_key"],
            base_url=settings["base_url"],
        )
        _client_config = client_config
    return _client


def call_deepseek(prompt):
    settings = get_deepseek_settings()
    if is_missing_api_key(settings["api_key"]):
        raise DeepSeekClientError("DEEPSEEK_API_KEY 未配置，请在 property_kb_backend/.env 中配置真实 Key")

    try:
        client = get_deepseek_client(settings)
        response = client.chat.completions.create(
            model=settings["model"],
            messages=[
                {
                    "role": "system",
                    "content": "你是智慧物业知识库助手，只能基于用户提供的知识库内容回答。",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.2,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as exc:
        detail = str(exc)
        if settings["api_key"]:
            detail = detail.replace(settings["api_key"], "***")
        raise DeepSeekClientError(f"DeepSeek 调用失败：{exc.__class__.__name__} {detail[:240]}") from exc


def get_deepseek_health():
    settings = get_deepseek_settings()
    api_key = settings["api_key"]
    return {
        "configured": not is_missing_api_key(api_key),
        "baseUrl": settings["base_url"],
        "model": settings["model"],
        "keyPrefix": f"{api_key[:6]}..." if api_key else "",
    }
