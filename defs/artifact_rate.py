import json

from ci import client

ocr_url = "https://api.genshin.pub/api/v1/app/ocr"
rate_url = "https://api.genshin.pub/api/v1/relic/rate"
head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "Connection": "close"
}


async def get_artifact_attr(b64_str):
    upload_json = json.dumps(
        {
            "image": b64_str
        }
    )
    try:
        req = await client.post(ocr_url, data=upload_json, headers=head, timeout=8)
    except Exception as e:
        raise e
    data = json.loads(req.text)
    if req.status_code != 200:
        return {"err": "未知错误", "full": data}
    return data


async def rate_artifact(artifact_attr: dict):
    upload_json_str = json.dumps(artifact_attr, ensure_ascii=False).encode('utf-8')
    try:
        req = await client.post(rate_url, data=upload_json_str, headers=head, timeout=8)
    except Exception as e:
        raise e
    data = json.loads(req.text)
    if req.status_code != 200:
        return {"err": "未知错误", "full": data}
    return data
