import os
import sys
import json
import asyncio
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import aiofiles

# Add pageindex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pageindex_lib'))

from pageindex import config, page_index_main
from pageindex.page_index_md import md_to_tree
from pageindex.utils import ConfigLoader
from openai import OpenAI

# Load environment variables
load_dotenv()

app = FastAPI(title="PageIndex RAG API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Storage paths
UPLOAD_DIR = Path("../uploads")
INDEX_DIR = Path("./indices")
UPLOAD_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)


class QuestionRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None  # If None, query all documents


class ChatMessage(BaseModel):
    role: str
    content: str


class ProcessingStatus(BaseModel):
    filename: str
    status: str
    message: str


# Store for indexed documents
indexed_documents = {}


def get_index_path(filename: str) -> Path:
    """Get the path to the index file for a document"""
    base_name = os.path.splitext(filename)[0]
    return INDEX_DIR / f"{base_name}_structure.json"


async def process_pdf_document(file_path: str, filename: str) -> dict:
    """Process a PDF document using PageIndex"""
    try:
        # Configure options
        opt = config(
            model='gpt-4o-2024-11-20',
            toc_check_page_num=20,
            max_page_num_each_node=10,
            max_token_num_each_node=20000,
            if_add_node_id='yes',
            if_add_node_summary='yes',
            if_add_doc_description='yes',
            if_add_node_text='no'
        )

        # Process the PDF
        toc_with_page_number = page_index_main(file_path, opt)

        # Save index
        index_path = get_index_path(filename)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(toc_with_page_number, f, indent=2)

        # Store in memory
        indexed_documents[filename] = toc_with_page_number

        return {
            "status": "success",
            "filename": filename,
            "index_path": str(index_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


async def process_markdown_document(file_path: str, filename: str) -> dict:
    """Process a Markdown document using PageIndex"""
    try:
        # Use ConfigLoader to get consistent defaults
        config_loader = ConfigLoader()

        user_opt = {
            'model': 'gpt-4o-2024-11-20',
            'if_add_node_summary': 'yes',
            'if_add_doc_description': 'yes',
            'if_add_node_text': 'no',
            'if_add_node_id': 'yes'
        }

        opt = config_loader.load(user_opt)

        # Process markdown
        toc_with_page_number = await md_to_tree(
            md_path=file_path,
            if_thinning=False,
            min_token_threshold=5000,
            if_add_node_summary=opt.if_add_node_summary,
            summary_token_threshold=200,
            model=opt.model,
            if_add_doc_description=opt.if_add_doc_description,
            if_add_node_text=opt.if_add_node_text,
            if_add_node_id=opt.if_add_node_id
        )

        # Save index
        index_path = get_index_path(filename)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(toc_with_page_number, f, indent=2, ensure_ascii=False)

        # Store in memory
        indexed_documents[filename] = toc_with_page_number

        return {
            "status": "success",
            "filename": filename,
            "index_path": str(index_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Markdown: {str(e)}")


def traverse_tree_for_context(node: dict, max_depth: int = 3, current_depth: int = 0) -> str:
    """Traverse the tree structure to extract relevant context"""
    context = []

    if current_depth >= max_depth:
        return ""

    # Add current node information
    if isinstance(node, dict):
        title = node.get('title', node.get('section', ''))
        summary = node.get('summary', '')
        text = node.get('text', '')

        if title:
            context.append(f"\n## {title}")
        if summary:
            context.append(f"Summary: {summary}")
        if text and len(text) < 5000:  # Include text if not too long
            context.append(text)

        # Traverse children
        children = node.get('children', [])
        for child in children:
            child_context = traverse_tree_for_context(child, max_depth, current_depth + 1)
            if child_context:
                context.append(child_context)

    return "\n".join(context)


def search_relevant_nodes(tree: dict, query: str, top_k: int = 5) -> List[str]:
    """
    Use LLM reasoning to find relevant sections in the tree structure
    This implements the core PageIndex reasoning-based retrieval
    """
    try:
        # First, get the tree structure summary
        tree_summary = json.dumps(tree, indent=2)[:4000]  # Limit for context

        # Use LLM to reason about which parts are relevant
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at navigating document structures. Given a tree structure of a document and a user query, identify the most relevant sections that would help answer the query. Return the node IDs or section titles that are most relevant."
                },
                {
                    "role": "user",
                    "content": f"Document Structure:\n{tree_summary}\n\nUser Query: {query}\n\nIdentify the most relevant sections (up to {top_k}) that would help answer this query. Return them as a JSON list of paths or identifiers."
                }
            ],
            temperature=0.3
        )

        # Extract relevant sections
        relevant_sections = []

        # Traverse tree and extract contexts
        context = traverse_tree_for_context(tree, max_depth=4)
        if context:
            relevant_sections.append(context)

        return relevant_sections
    except Exception as e:
        print(f"Error in search: {e}")
        # Fallback: return full tree context
        return [traverse_tree_for_context(tree, max_depth=3)]


@app.get("/")
async def root():
    return {"message": "PageIndex RAG API is running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.md', '.markdown'}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Process document based on type
        if file_ext == '.pdf':
            result = await process_pdf_document(str(file_path), file.filename)
        else:  # .md or .markdown
            result = await process_markdown_document(str(file_path), file.filename)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    """List all indexed documents"""
    documents = []

    # Load any existing indices
    for index_file in INDEX_DIR.glob("*_structure.json"):
        filename = index_file.stem.replace("_structure", "")

        # Load index if not in memory
        if filename not in indexed_documents:
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    indexed_documents[filename] = json.load(f)
            except Exception as e:
                print(f"Error loading index for {filename}: {e}")
                continue

        documents.append({
            "id": filename,
            "filename": filename,
            "indexed": True
        })

    return {"documents": documents}


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Answer a question using the indexed documents"""
    try:
        if not indexed_documents:
            # Try to load existing indices
            await list_documents()

        if not indexed_documents:
            raise HTTPException(
                status_code=400,
                detail="No documents indexed. Please upload documents first."
            )

        # Determine which documents to query
        docs_to_query = request.document_ids if request.document_ids else list(indexed_documents.keys())

        # Gather context from relevant documents
        all_contexts = []
        for doc_id in docs_to_query:
            if doc_id in indexed_documents:
                tree = indexed_documents[doc_id]
                relevant_sections = search_relevant_nodes(tree, request.question)
                all_contexts.extend(relevant_sections)

        if not all_contexts:
            raise HTTPException(
                status_code=404,
                detail="No relevant content found in the documents"
            )

        # Combine contexts
        combined_context = "\n\n---\n\n".join(all_contexts)

        # Generate answer using LLM
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided document context. Always cite specific sections or information from the documents when possible."
                },
                {
                    "role": "user",
                    "content": f"Context from documents:\n\n{combined_context}\n\nQuestion: {request.question}\n\nPlease provide a detailed answer based on the context above."
                }
            ],
            temperature=0.7
        )

        answer = response.choices[0].message.content

        return {
            "question": request.question,
            "answer": answer,
            "sources": docs_to_query
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document and its index"""
    try:
        # Remove from memory
        if filename in indexed_documents:
            del indexed_documents[filename]

        # Remove index file
        index_path = get_index_path(filename)
        if index_path.exists():
            index_path.unlink()

        # Remove uploaded file
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()

        return {"message": f"Document {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
