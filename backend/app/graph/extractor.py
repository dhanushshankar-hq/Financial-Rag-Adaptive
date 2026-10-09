from typing import List
from pydantic import BaseModel, Field
import structlog
from groq import Groq
from backend.app.core.config import settings

logger = structlog.get_logger()

class FinancialMetric(BaseModel):
    metric_name: str = Field(description="Standardized metric name such as Total Revenue, Operating Profit, or Net Profit")
    raw_value: float = Field(description="Exact numerical value extracted from the table")
    currency: str = Field(description="Currency code such as INR")
    scale: str = Field(description="Scale multiplier such as Crores or Millions")

class FilingMetrics(BaseModel):
    metrics: List[FinancialMetric]

class MetricExtractor:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def extract_from_table(self, markdown_table: str) -> List[FinancialMetric]:
        logger.info("Extracting structured financial metrics from table markdown")

        system_prompt = """You are a precise financial data extraction engine. 
        Extract accurate financial metrics matching the requested schema exactly."""
        
        user_prompt = f"""
        Table Markdown:
        {markdown_table}
        """

        completion = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role":"system","content":system_prompt},
                {"role": "user", "content":user_prompt}
                ],
            response_format={
                "type": "json_object",
                "json_schema": {
                    "name": "FilingMetrics",
                    "strict": True,
                    "schema": FilingMetrics.model_json_schema()
                }                
            }
        )

        import json
        content = completion.choices[0].message.content
        data = json.loads(content)
        
        parsed = FilingMetrics(**data)
        return parsed.metrics