from pydantic import BaseModel
from typing import List, Optional

# Requests
class EmailGenerateRequest(BaseModel):
    type: str = "business"
    topic: str
    recipient: str
    tone: str = "professional"

class InstagramGenerateRequest(BaseModel):
    topic: str
    tone: str = "engaging"

class FacebookGenerateRequest(BaseModel):
    topic: str
    tone: str = "friendly"

class TwitterGenerateRequest(BaseModel):
    topic: str
    tone: str = "viral"

class PromptGenerateRequest(BaseModel):
    goal: str
    tool: str = "Midjourney"

class BlogGenerateRequest(BaseModel):
    topic: str
    words: int = 700

class ProductGenerateRequest(BaseModel):
    product_name: str
    target_audience: str

class LinkedInGenerateRequest(BaseModel):
    topic: str

# Responses
class EmailGenerateResponse(BaseModel):
    subject: str
    body: str

class InstagramGenerateResponse(BaseModel):
    caption: str
    hashtags: List[str]

class FacebookGenerateResponse(BaseModel):
    post_text: str
    hashtags: List[str]

class TwitterGenerateResponse(BaseModel):
    tweet_thread: List[str]
    hooks: List[str]

class PromptGenerateResponse(BaseModel):
    optimized_prompt: str

class BlogGenerateResponse(BaseModel):
    title: str
    article: str
    conclusion: str

class ProductGenerateResponse(BaseModel):
    product_description: str
    selling_points: List[str]

class LinkedInGenerateResponse(BaseModel):
    post_text: str

class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str

class TemplateListResponse(BaseModel):
    templates: List[TemplateInfo]
