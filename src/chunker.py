"""Document chunking using Docling's HybridChunker."""

from docling_core.transforms.chunker import HybridChunker
from docling_core.types.doc import DoclingDocument

from .models import ChunkInfo


class DocumentChunker:
    """Wrapper around Docling's HybridChunker."""

    def __init__(self, tokenizer: str = "BAAI/bge-small-en-v1.5"):
        """Initialize chunker with tokenizer.

        Args:
            tokenizer: HuggingFace tokenizer name or path
        """
        self._tokenizer = tokenizer
        self._chunker: HybridChunker | None = None

    def _get_chunker(self, max_tokens: int) -> HybridChunker:
        """Get or create chunker with specified max tokens."""
        return HybridChunker(
            tokenizer=self._tokenizer,
            max_tokens=max_tokens,
        )

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Simple approximation: ~4 characters per token on average
        return len(text) // 4

    def _get_page_number(self, chunk) -> int | None:
        """Extract page number from chunk metadata if available."""
        if hasattr(chunk, "meta") and chunk.meta:
            if hasattr(chunk.meta, "page_no"):
                return chunk.meta.page_no
            if isinstance(chunk.meta, dict) and "page_no" in chunk.meta:
                return chunk.meta["page_no"]
        return None

    def chunk_document(
        self,
        doc: DoclingDocument,
        max_tokens: int = 512,
        preview_length: int = 100,
    ) -> list[ChunkInfo]:
        """Chunk a DoclingDocument into smaller pieces.

        Args:
            doc: DoclingDocument to chunk
            max_tokens: Maximum tokens per chunk
            preview_length: Length of text preview in ChunkInfo

        Returns:
            List of ChunkInfo objects
        """
        chunker = self._get_chunker(max_tokens)
        chunks = list(chunker.chunk(doc))

        result = []
        for i, chunk in enumerate(chunks):
            text = chunk.text if hasattr(chunk, "text") else str(chunk)

            # Create preview (truncated text)
            preview = text[:preview_length]
            if len(text) > preview_length:
                preview += "..."

            result.append(
                ChunkInfo(
                    index=i,
                    text=text,
                    preview=preview,
                    page_num=self._get_page_number(chunk),
                    token_count=self._estimate_tokens(text),
                )
            )

        return result
