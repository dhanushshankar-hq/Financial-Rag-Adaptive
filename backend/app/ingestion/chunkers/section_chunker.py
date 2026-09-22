from pydantic import BaseModel
from typing import Dict,Any,List,Optional
import tiktoken
import re

class Chunk(BaseModel):
    chunk_index:int
    heading_path:str
    content:str
    token_count:int
    metadata:Dict[str,Any]

class FinancialSectionChunker:
    def __init__(self,target_chunk_size:int = 512,overlap:int=64):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def chunk_document(self,markdown_text:str, default_metadata:Optional[Dict[str,Any]]=None) -> List[Chunk]:
        default_metadata = default_metadata or {}

        header_pattern = re.compile(r'^(#{1,3})\s+(.+)$',re.MULTILINE)

        splits = re.split(r'\n(?=#{1,3}\s)', markdown_text)

        raw_chunks = []
        chunk_idx = 0
        header_stack = {1:"",2:"",3:""}

        for block in splits:
            if not block.strip():
                continue

            lines = block.strip().split('\n')
            heading = lines[0]
            header_match = header_pattern.match(heading)

            if header_match:
                level = len(header_match.group(1))
                header_title = header_match.group(2).strip()

                header_stack[level] = header_title

                for l in range(level+1,4):
                    header_stack[l] = ""

            active_headers = [header_stack[l] for l in range(1, 4) if header_stack[l]]
            heading_path = " > ".join(active_headers) if active_headers else "General Content"
                
            block_tokens = self.count_tokens(block)

            if block_tokens <= self.target_chunk_size or '|' in block:
                contextualized_content = f"[{heading_path}]\n{block.strip()}"

                raw_chunks.append(
                    Chunk(
                        chunk_index=chunk_idx,
                        heading_path=heading_path,
                        content=contextualized_content,
                        token_count=self.count_tokens(contextualized_content),
                        metadata=default_metadata
                    )
                )

                chunk_idx += 1
            else:
                tokens = self.tokenizer.encode(block)

                for start in range(0,len(tokens),self.target_chunk_size-self.overlap):
                    end = start + self.target_chunk_size
                    chunk_tokens = tokens[start:end]
                    chunk_text = self.tokenizer.decode(chunk_tokens)

                    contextualized_content = f"[{heading_path}]\n{chunk_text.strip()}"

                    raw_chunks.append(
                        Chunk(
                            chunk_index=chunk_idx,
                            heading_path=heading_path,
                            content=contextualized_content,
                            token_count=self.count_tokens(contextualized_content),
                            metadata=default_metadata
                        )
                    )
                    chunk_idx += 1

        return raw_chunks


if __name__ == "__main__":
    sample_markdown = """
# TCS Annual Report FY2025

Tata Consultancy Services reported strong financial performance during FY2025. 
The company continued to expand its global technology services business across 
banking, financial services, healthcare, retail, manufacturing, and communications.

TCS focused on artificial intelligence, cloud transformation, cybersecurity, 
data engineering, and enterprise modernization. The company also increased 
investments in research and development and continued to develop partnerships 
with major technology vendors.

## Financial Performance

TCS reported consolidated revenue growth during FY2025. The company maintained 
strong operating margins while continuing to invest in employee development, 
digital capabilities, and artificial intelligence.

The financial performance was supported by demand from large enterprise customers. 
Growth was observed across multiple geographic regions and industry segments. 
The company continued to focus on improving productivity and increasing the share 
of higher-value services in its overall revenue mix.

### Revenue

Revenue increased during FY2025 compared with the previous financial year. 
The company generated revenue from multiple business segments including banking, 
financial services, insurance, retail, consumer packaged goods, manufacturing, 
life sciences, healthcare, communications, media, and technology.

The company continued to expand its cloud transformation portfolio. Large 
customers increasingly adopted cloud-native architectures, data platforms, 
artificial intelligence applications, and automation solutions.

TCS also reported continued demand for cybersecurity services. Enterprises 
increased spending on identity management, security operations, threat detection, 
risk management, and compliance.

The company stated that artificial intelligence became an important component 
of customer transformation programs. Several customers initiated pilots involving 
generative AI, enterprise search, intelligent document processing, and software 
engineering assistants.

### Revenue by Segment

| Segment | FY2025 Revenue | Growth |
|---------|----------------|--------|
| Banking | 12500 | 8.2% |
| Healthcare | 8200 | 6.7% |
| Retail | 9100 | 7.4% |
| Manufacturing | 7600 | 5.9% |
| Communications | 6800 | 4.8% |

## Operating Performance

TCS continued to focus on operational efficiency during FY2025. The company 
invested in automation and internal platforms to improve delivery productivity.

Employee utilization remained an important operational metric. The company also 
continued to train employees in cloud computing, artificial intelligence, 
cybersecurity, data engineering, and modern software development practices.

The company expanded its use of internal artificial intelligence platforms. 
These platforms were used to assist developers, automate repetitive activities, 
improve testing workflows, and support enterprise knowledge discovery.

Customer relationships remained an important component of the business model. 
Large customers continued to engage TCS for multi-year transformation programs 
covering application modernization, infrastructure, cloud migration, and data 
platform development.

## Artificial Intelligence Strategy

TCS increased its focus on generative artificial intelligence during FY2025.

The company explored retrieval augmented generation, enterprise knowledge 
systems, AI-powered software development, intelligent automation, and domain 
specific language models.

The organization also invested in employee training programs designed to improve 
AI engineering capabilities. Employees were encouraged to learn machine learning, 
large language models, prompt engineering, retrieval systems, vector databases, 
and AI application development.

### Generative AI

Generative AI initiatives focused on improving enterprise productivity. 
Applications included document summarization, question answering, code generation, 
customer support, enterprise search, and automated report generation.

A major challenge for enterprise AI systems was maintaining factual accuracy. 
Organizations therefore invested in retrieval systems, evaluation frameworks, 
guardrails, observability, and human review processes.

Retrieval augmented generation systems were designed to retrieve relevant 
information from enterprise data before generating an answer. Hybrid retrieval 
could combine semantic vector search with traditional keyword search.

## Risk Management

The company identified several risks associated with changing technology 
markets, cybersecurity threats, regulatory requirements, economic uncertainty, 
and competition.

Cybersecurity remained an important area of investment. The company continued 
to improve security monitoring, access control, identity management, and incident 
response capabilities.

Technology changes also created opportunities and risks. Rapid developments in 
artificial intelligence could change software development practices and customer 
requirements.

## Conclusion

During FY2025, TCS continued to invest in cloud computing, artificial intelligence, 
cybersecurity, and enterprise transformation. The company maintained its focus on 
large enterprise customers while expanding its digital capabilities.

The combination of technology investments, employee training, operational 
efficiency, and customer relationships remained central to the company's strategy.
"""
    chunker = FinancialSectionChunker()
    chunks = chunker.chunk_document(sample_markdown)

    for chunk in chunks:
        print("=" * 80)
        print("INDEX:", chunk.chunk_index)
        print("PATH:", chunk.heading_path)
        print("TOKENS:", chunk.token_count)
        print(chunk.content[:300])