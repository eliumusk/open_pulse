"""
Jina Web Reader - Custom reader for web content using Jina AI API
Solves the issue with Agno's built-in web readers (WebsiteReader, FirecrawlReader, etc.)
"""
import os
import requests
from typing import List
from agno.knowledge.document.base import Document
from agno.knowledge.reader.base import Reader
from agno.utils.log import logger


class JinaWebReader(Reader):
    
    def __init__(
        self,
        api_key: str = None,
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs
    ):

        super().__init__(**kwargs)
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            logger.warning(
                "No Jina API key provided. "
            )
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://r.jina.ai"
    
    def read(self, url: str, name: str = None) -> List[Document]:
        if not url:
            logger.error("No URL provided to JinaWebReader")
            return []
        
        if not url.startswith(("http://", "https://")):
            logger.error(f"Invalid URL format: {url}")
            return []
        
        logger.info(f"Reading URL with Jina Reader: {url}")
        
        try:
            # Construct Jina Reader URL
            jina_url = f"{self.base_url}/{url}"
            
            # Prepare headers
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Make request with retries
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        jina_url,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        content = response.text
                        
                        if not content or len(content.strip()) == 0:
                            logger.warning(f"Empty content returned from {url}")
                            return []
                        
                        # Create document
                        doc_name = name or url
                        doc = Document(
                            name=doc_name,
                            content=content,
                            meta_data={
                                "source": url,
                                "reader": "JinaWebReader",
                                "content_length": len(content)
                            }
                        )
                        
                        logger.info(
                            f"Successfully read {len(content)} characters from {url}"
                        )
                        return [doc]
                    
                    elif response.status_code == 401:
                        logger.error(
                            "Jina API authentication failed. Check your API key."
                        )
                        return []
                    
                    elif response.status_code == 429:
                        logger.warning(
                            f"Rate limit exceeded (attempt {attempt + 1}/{self.max_retries})"
                        )
                        if attempt < self.max_retries - 1:
                            import time
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        return []
                    
                    else:
                        logger.error(
                            f"Jina Reader returned status {response.status_code}: {response.text[:200]}"
                        )
                        return []
                
                except requests.Timeout:
                    logger.warning(
                        f"Request timeout (attempt {attempt + 1}/{self.max_retries})"
                    )
                    if attempt < self.max_retries - 1:
                        continue
                    logger.error(f"Failed to read {url} after {self.max_retries} attempts")
                    return []
                
                except requests.RequestException as e:
                    logger.error(f"Request error reading {url}: {str(e)}")
                    return []
        
        except Exception as e:
            logger.error(f"Unexpected error reading {url}: {str(e)}")
            return []
    
    async def async_read(self, url: str, name: str = None) -> List[Document]:
        # For now, use sync version in async context
        # TODO: Implement true async with aiohttp if needed
        import asyncio
        return await asyncio.to_thread(self.read, url, name)
    
    def get_supported_chunking_strategies(self) -> List[str]:
        """
        Get list of supported chunking strategies for this reader.
        
        Returns:
            List[str]: List of supported chunking strategy names
        """
        return [
            "FixedSizeChunking",
            "SemanticChunking",
            "RecursiveChunking",
            "DocumentChunking",
            "AgenticChunking"
        ]

