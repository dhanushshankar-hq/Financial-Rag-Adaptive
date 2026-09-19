from pydantic import BaseModel
from typing import Dict,Any
class Chunk(BaseModel):
    chunk_index:int
    section_type:str
    content:str
    token_count:str
    metadata:Dict[str,Any]

class FinancialSectionChunker:
    def __init__(Self,target_chunk_size:int = 512,overlap:int=64)
