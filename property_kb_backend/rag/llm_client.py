from rag.config import (
    BIGMODEL_API_KEY,
    BIGMODEL_BASE_URL,
    BIGMODEL_MODEL,
)


class LLMClientError(RuntimeError):
    pass


_client = None
_client_config = None


def get_llm_settings():
    return {
        "api_key": BIGMODEL_API_KEY.strip(),
        "base_url": BIGMODEL_BASE_URL.strip(),
        "model": BIGMODEL_MODEL.strip(),
    }


def is_missing_api_key(api_key):
    return not api_key or api_key in {"sk-xxxx", "sk-xxx", "your-api-key"}


def get_llm_client(settings):
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


def call_llm(prompt):
    settings = get_llm_settings()
    if is_missing_api_key(settings["api_key"]):
        raise LLMClientError("BIGMODEL_API_KEY 未配置，请在 property_kb_backend/.env 中配置真实 Key")

    try:
        client = get_llm_client(settings)
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
            thinking={"type": "disable"},
        )
        return response.choices[0].message.content
    except Exception as exc:
        detail = str(exc)
        if settings["api_key"]:
            detail = detail.replace(settings["api_key"], "***")
        raise LLMClientError(f"质谱大模型调用失败：{exc.__class__.__name__} {detail[:240]}") from exc


def get_llm_health():
    settings = get_llm_settings()
    api_key = settings["api_key"]
    return {
        "configured": not is_missing_api_key(api_key),
        "baseUrl": settings["base_url"],
        "model": settings["model"],
        "keyPrefix": f"{api_key[:6]}..." if api_key else "",
    }
