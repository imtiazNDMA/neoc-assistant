# Chat API

The Chat API provides endpoints for conversational interactions with NEOC AI Assistant, supporting both direct chat and retrieval-augmented generation (RAG) responses.

## Base URL

```
http://localhost:8000/api/chat
```

## Endpoints

### POST /api/chat/

Generate a chat response from NEOC AI Assistant.

#### Request

```http
POST /api/chat/
Content-Type: application/json

{
  "message": "What are the main types of natural disasters?",
  "conversation_id": "optional-conversation-id",
  "use_rag": true,
  "max_tokens": 1000
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | The user's message/question |
| `conversation_id` | string | No | Unique identifier for conversation threading |
| `use_rag` | boolean | No | Whether to use RAG for enhanced responses (default: true) |
| `max_tokens` | integer | No | Maximum tokens in response (default: 1000) |
| `temperature` | float | No | Response creativity (0.0-1.0, default: 0.1) |

#### Response

```json
{
  "response": "Natural disasters can be categorized into several main types based on their causes: geological (earthquakes, volcanoes), hydrological (floods, tsunamis), meteorological (hurricanes, tornadoes), climatological (droughts, heatwaves), and biological (epidemics, infestations). Each type requires different prevention and response strategies.",
  "conversation_id": "conv_123456",
  "processing_time": 1.23,
  "tokens_used": 156,
  "citations": [
    {
      "title": "Disaster Management Handbook",
      "authors": ["Smith, J.", "Johnson, A."],
      "year": 2023,
      "source": "International Disaster Management Journal"
    }
  ],
  "cache_hit": false,
  "model_used": "phi3:latest"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The AI-generated response |
| `conversation_id` | string | Conversation identifier |
| `processing_time` | float | Time taken to generate response (seconds) |
| `tokens_used` | integer | Number of tokens consumed |
| `citations` | array | IEEE-formatted citations used |
| `cache_hit` | boolean | Whether response came from cache |
| `model_used` | string | LLM model used for generation |

#### Error Responses

**400 Bad Request**
```json
{
  "error": "Invalid message format",
  "detail": "Message cannot be empty"
}
```

**429 Too Many Requests**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

**500 Internal Server Error**
```json
{
  "error": "LLM service unavailable",
  "detail": "Model loading failed"
}
```

### GET /api/chat/history/{conversation_id}

Retrieve conversation history for a specific conversation.

#### Request

```http
GET /api/chat/history/conv_123456
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conversation_id` | string | Yes | Conversation identifier (URL path) |
| `limit` | integer | No | Maximum messages to return (default: 50) |
| `offset` | integer | No | Number of messages to skip (default: 0) |

#### Response

```json
{
  "conversation_id": "conv_123456",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "What are earthquake preparedness measures?",
      "timestamp": "2024-01-15T10:30:00Z",
      "tokens": 8
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "Earthquake preparedness involves several key measures...",
      "timestamp": "2024-01-15T10:30:02Z",
      "tokens": 245,
      "citations": [
        {
          "title": "Seismic Safety Guidelines",
          "authors": ["USGS"],
          "year": 2023
        }
      ]
    }
  ],
  "total_messages": 2,
  "has_more": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | string | Conversation identifier |
| `messages` | array | Array of message objects |
| `total_messages` | integer | Total number of messages in conversation |
| `has_more` | boolean | Whether more messages are available |

#### Message Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier |
| `role` | string | "user" or "assistant" |
| `content` | string | Message content |
| `timestamp` | string | ISO 8601 timestamp |
| `tokens` | integer | Token count |
| `citations` | array | Citations (assistant messages only) |

## Authentication

All Chat API endpoints require authentication via API key header:

```http
Authorization: Bearer your-api-key
```

API keys can be obtained from the NEOC AI Assistant administration interface.

## Rate Limiting

The Chat API implements rate limiting to ensure fair usage:

- **Authenticated users**: 60 requests per minute
- **Anonymous users**: 10 requests per minute
- **Burst limit**: 100 requests per minute (short-term)

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## Caching

Responses are cached to improve performance and reduce computational load:

- **Cache TTL**: 30 minutes for standard responses
- **Semantic caching**: Similar queries may return cached results
- **Cache bypass**: Use `cache: false` in request to skip caching

## Examples

### Basic Chat Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/",
    json={
        "message": "How do communities prepare for floods?"
    },
    headers={
        "Authorization": "Bearer your-api-key"
    }
)

print(response.json()["response"])
```

### RAG-Enhanced Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/",
    json={
        "message": "What are the latest flood prediction technologies?",
        "use_rag": True,
        "max_tokens": 800
    },
    headers={
        "Authorization": "Bearer your-api-key"
    }
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Citations: {len(data['citations'])}")
```

### Conversation History

```python
import requests

response = requests.get(
    "http://localhost:8000/api/chat/history/conv_123456",
    headers={
        "Authorization": "Bearer your-api-key"
    }
)

history = response.json()
for message in history["messages"]:
    print(f"{message['role']}: {message['content'][:100]}...")
```

### Streaming Responses (Future)

```python
# Note: Streaming support planned for future release
import requests

with requests.post(
    "http://localhost:8000/api/chat/",
    json={"message": "Explain disaster response phases", "stream": True},
    headers={"Authorization": "Bearer your-api-key"},
    stream=True
) as response:
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
```

## Error Handling

### Common Error Codes

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "error": "Error type",
  "detail": "Detailed error description",
  "request_id": "unique-request-identifier",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Best Practices

### Request Optimization

1. **Use conversation IDs** for multi-turn conversations
2. **Enable RAG** for complex queries requiring context
3. **Set appropriate max_tokens** to control response length
4. **Handle rate limits** gracefully with exponential backoff

### Response Processing

1. **Check citations** for academic or technical responses
2. **Monitor processing_time** for performance analysis
3. **Handle cache_hit** appropriately for user experience
4. **Store conversation_id** for follow-up interactions

### Error Recovery

```python
import time
import requests
from requests.exceptions import RequestException

def chat_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/api/chat/",
                json={"message": message},
                timeout=30
            )

            if response.status_code == 429:
                # Rate limited, wait and retry
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()

        except RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff

    raise Exception("Max retries exceeded")
```

## Monitoring

### Metrics

The Chat API exposes the following metrics:

- `chat_requests_total`: Total number of chat requests
- `chat_response_time_seconds`: Response time distribution
- `chat_tokens_used_total`: Total tokens consumed
- `chat_cache_hits_total`: Cache hit counter
- `chat_errors_total`: Error counter by type

### Health Checks

```http
GET /health
```

Returns service health including Chat API status:

```json
{
  "status": "healthy",
  "services": {
    "llm_service": "healthy",
    "rag_pipeline": "healthy",
    "chat_api": "healthy"
  },
  "metrics": {
    "chat_requests_last_hour": 1250,
    "chat_avg_response_time": 1.8,
    "chat_error_rate": 0.02
  }
}
```

## Versioning

The Chat API uses semantic versioning:

- **v1** (current): Basic chat functionality
- **v2** (planned): Streaming responses, advanced RAG features

API versions are specified in the URL path:

```
POST /api/v1/chat/
GET /api/v1/chat/history/{id}
```

## Support

For API support or questions:

- **Documentation**: https://neoc-ai-assistant.readthedocs.io/
- **Issues**: https://github.com/your-org/neoc-ai-assistant/issues
- **Discussions**: https://github.com/your-org/neoc-ai-assistant/discussions