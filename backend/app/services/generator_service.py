import json
from app.services.ai_service import ask_ai
from typing import Dict, Any

class GeneratorService:
    @staticmethod
    def _get_json_from_ai(prompt: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": "You are a specialized content generator AI. Always return your output in STRICT JSON format. Do not include any text outside the JSON block."},
            {"role": "user", "content": prompt}
        ]
        response_text = ask_ai(messages)
        # Clean potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        try:
            return json.loads(response_text.strip())
        except Exception as e:
            print(f"JSON Parsing Error: {e}\nRaw Response: {response_text}")
            # Fallback or retry logic could go here
            raise ValueError("AI failed to return valid JSON. Please try again.")

    @staticmethod
    def generate_email(type: str, topic: str, recipient: str, tone: str):
        prompt = f"""
        Generate a professional email.
        Type: {type}
        Topic: {topic}
        Recipient: {recipient}
        Tone: {tone}
        
        Return JSON with keys: "subject", "body".
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def generate_instagram(topic: str, tone: str):
        prompt = f"""
        Generate an Instagram caption and hashtags.
        Topic: {topic}
        Tone: {tone}
        
        Return JSON with keys: "caption", "hashtags" (list of strings).
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def generate_facebook(topic: str, tone: str):
        prompt = f"""
        Generate a Facebook post and hashtags.
        Topic: {topic}
        Tone: {tone}
        
        Return JSON with keys: "post_text", "hashtags" (list of strings).
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def generate_twitter(topic: str, tone: str):
        prompt = f"""
        Generate a Twitter/X thread and hooks.
        Topic: {topic}
        Tone: {tone}
        
        Return JSON with keys: "tweet_thread" (list of strings), "hooks" (list of strings).
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def generate_prompt(goal: str, tool: str):
        prompt = f"""
        Generate an optimized AI prompt for {tool}.
        Goal: {goal}
        
        Return JSON with key: "optimized_prompt".
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def generate_blog(topic: str, words: int):
        prompt = f"""
        Generate a blog article (approx {words} words).
        Topic: {topic}
        
        Return JSON with keys: "title", "article", "conclusion".
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def generate_product(product_name: str, target_audience: str):
        prompt = f"""
        Generate a product description and selling points.
        Product Name: {product_name}
        Target Audience: {target_audience}
        
        Return JSON with keys: "product_description", "selling_points" (list of strings).
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def generate_linkedin(topic: str):
        prompt = f"""
        Generate a professional LinkedIn post.
        Topic: {topic}
        
        Return JSON with key: "post_text".
        """
        return GeneratorService._get_json_from_ai(prompt)

    @staticmethod
    def get_templates():
        return [
            {"id": "email", "name": "Professional Email", "description": "Generate business or personal emails", "category": "Business"},
            {"id": "instagram", "name": "Instagram Caption", "description": "Engaging captions and hashtags", "category": "Social Media"},
            {"id": "facebook", "name": "Facebook Post", "description": "Friendly and shareable posts", "category": "Social Media"},
            {"id": "twitter", "name": "Twitter Thread", "description": "Viral threads and hooks", "category": "Social Media"},
            {"id": "prompt", "name": "AI Prompt Generator", "description": "Optimize prompts for Midjourney/DALL-E", "category": "AI Tools"},
            {"id": "blog", "name": "Blog Article", "description": "Full articles with structure", "category": "Content"},
            {"id": "product", "name": "Product Description", "description": "Compelling sales copy", "category": "E-commerce"},
            {"id": "linkedin", "name": "LinkedIn Post", "description": "Professional thought leadership", "category": "Business"},
        ]
