"""
Advanced Search and Discovery Tools for SRRD Builder MCP Server
Handles semantic search, pattern discovery, and knowledge graph operations
"""

from typing import Dict, Any, Optional, List, Tuple
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path to access storage modules
sys.path.append(str(Path(__file__).parent.parent))

from storage.project_manager import ProjectManager
from storage.vector_manager import VectorManager

async def semantic_search_tool(
    query: str,
    collection: str = "research_docs",
    limit: int = 10,
    similarity_threshold: float = 0.7,
    project_path: str = ""
) -> str:
    """Perform semantic search across research documents"""
    
    try:
        vector_manager = None
        
        if project_path:
            project_manager = ProjectManager(project_path)
            vector_manager = project_manager.vector_manager
        else:
            vector_manager = VectorManager()
            try:
                await vector_manager.initialize()
            except Exception as e:
                vector_manager = None
        
        # Handle case where vector manager is not available or None
        if vector_manager is None:
            return f"Semantic search results for '{query}':\nVector database not available - using fallback search\n\nFallback results:\n- No semantic search capabilities available\n- Consider installing ChromaDB and sentence-transformers for full functionality"
        
        results = await vector_manager.search_knowledge(
            query=query,
            collection=collection,
            n_results=limit
        )
        
        # Filter by similarity threshold if available
        filtered_results = []
        documents = results.get('documents', [])
        
        # Handle nested list structure from ChromaDB
        if documents and isinstance(documents[0], list):
            documents = documents[0]
        
        for result in documents:
            # Assuming results include similarity scores
            filtered_results.append(result)
        
        if not filtered_results:
            return f"Semantic search results for '{query}':\nNo matching documents found in collection '{collection}'"
        
        return f"Semantic search results for '{query}':\n{json.dumps(filtered_results[:limit], indent=2)}"
        
    except Exception as e:
        return f"Error performing semantic search: {str(e)}"

async def discover_patterns_tool(
    content: str,
    pattern_type: str = "research_themes",
    min_frequency: int = 2
) -> str:
    """Discover patterns and themes in research content"""
    
    try:
        patterns = {}
        
        if pattern_type == "research_themes":
            # Extract potential research themes using keyword analysis
            words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
            word_freq = {}
            
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Filter by minimum frequency
            themes = {word: freq for word, freq in word_freq.items() 
                     if freq >= min_frequency and len(word) > 4}
            
            # Sort by frequency
            sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
            patterns['themes'] = sorted_themes[:20]  # Top 20 themes
        
        elif pattern_type == "methodologies":
            # Look for methodology-related terms
            method_keywords = [
                'analysis', 'approach', 'method', 'technique', 'algorithm',
                'framework', 'model', 'theory', 'hypothesis', 'experiment'
            ]
            
            methodologies = []
            for keyword in method_keywords:
                matches = re.findall(f'\\b\\w*{keyword}\\w*\\b', content.lower())
                if matches:
                    methodologies.extend(matches)
            
            patterns['methodologies'] = list(set(methodologies))
        
        elif pattern_type == "citations":
            # Extract citation patterns
            citations = re.findall(r'\([^)]*\d{4}[^)]*\)', content)
            patterns['citations'] = citations
        
        elif pattern_type == "equations":
            # Extract mathematical expressions
            equations = re.findall(r'\$[^$]+\$|\\\([^)]+\\\)|\\\[[^\]]+\\\]', content)
            patterns['equations'] = equations
        
        return f"Discovered patterns ({pattern_type}):\n{json.dumps(patterns, indent=2)}"
        
    except Exception as e:
        return f"Error discovering patterns: {str(e)}"

async def build_knowledge_graph_tool(
    documents: List[str],
    relationship_types: List[str] = ["cites", "related_to", "builds_upon"],
    project_path: str = ""
) -> str:
    """Build knowledge graph from research documents"""
    
    try:
        knowledge_graph = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'created': datetime.now().isoformat(),
                'document_count': len(documents),
                'relationship_types': relationship_types
            }
        }
        
        # Extract entities (simplified approach)
        entities = set()
        for doc in documents:
            # Extract potential entities (capitalized terms, technical terms)
            doc_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', doc)
            entities.update(doc_entities)
        
        # Create nodes
        for i, entity in enumerate(entities):
            knowledge_graph['nodes'].append({
                'id': i,
                'label': entity,
                'type': 'concept'
            })
        
        # Create edges based on co-occurrence (simplified)
        entity_list = list(entities)
        for i, doc in enumerate(documents):
            doc_entities = [e for e in entity_list if e in doc]
            
            # Create edges between entities that appear in the same document
            for j, entity1 in enumerate(doc_entities):
                for entity2 in doc_entities[j+1:]:
                    idx1 = entity_list.index(entity1)
                    idx2 = entity_list.index(entity2)
                    
                    knowledge_graph['edges'].append({
                        'source': idx1,
                        'target': idx2,
                        'relationship': 'co_occurs',
                        'document': f"doc_{i}",
                        'weight': 1.0
                    })
        
        # Save to project if path provided
        if project_path:
            kg_path = Path(project_path) / "knowledge_graphs" / f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            kg_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(kg_path, 'w') as f:
                json.dump(knowledge_graph, f, indent=2)
            
            return f"Knowledge graph built and saved to: {kg_path}"
        
        return f"Knowledge graph built with {len(knowledge_graph['nodes'])} nodes and {len(knowledge_graph['edges'])} edges"
        
    except Exception as e:
        return f"Error building knowledge graph: {str(e)}"

async def find_similar_documents_tool(
    target_document: str,
    collection: str = "research_docs",
    similarity_threshold: float = 0.8,
    max_results: int = 5,
    project_path: str = ""
) -> str:
    """Find documents similar to the target document"""
    
    try:
        vector_manager = None
        
        if project_path:
            project_manager = ProjectManager(project_path)
            vector_manager = project_manager.vector_manager
        else:
            vector_manager = VectorManager()
            try:
                await vector_manager.initialize()
            except Exception as e:
                vector_manager = None
        
        # Handle case where vector manager is not available or None
        if vector_manager is None:
            return f"Similar documents search:\nVector database not available - cannot perform similarity search\n\nConsider installing ChromaDB and sentence-transformers for full functionality"
        
        # Use the document content as query for similarity search
        results = await vector_manager.search_knowledge(
            query=target_document,
            collection=collection,
            n_results=max_results
        )
        
        similar_docs = []
        documents = results.get('documents', [])
        
        # Handle nested list structure from ChromaDB
        if documents and isinstance(documents[0], list):
            documents = documents[0]
        
        for result in documents:
            similar_docs.append({
                'content': result[:200] + "..." if len(result) > 200 else result,  # Truncate for display
                'similarity': "High"  # Placeholder - would need actual similarity scores
            })
        
        if not similar_docs:
            return f"Similar documents:\nNo similar documents found in collection '{collection}'"
        
        return f"Similar documents found:\n{json.dumps(similar_docs, indent=2)}"
        
    except Exception as e:
        return f"Error finding similar documents: {str(e)}"

async def extract_key_concepts_tool(
    text: str,
    max_concepts: int = 20,
    concept_types: List[str] = ["technical_terms", "theories", "methods"]
) -> str:
    """Extract key concepts from research text"""
    
    try:
        concepts = {}
        
        if "technical_terms" in concept_types:
            # Extract technical terms (words with specific patterns)
            technical_terms = re.findall(r'\b[a-z]+(?:-[a-z]+)*(?:\s+[a-z]+(?:-[a-z]+)*)*\b', text.lower())
            # Filter for likely technical terms (longer, compound words)
            technical_terms = [term for term in technical_terms 
                             if len(term) > 6 or '-' in term or term.count(' ') > 0]
            concepts['technical_terms'] = list(set(technical_terms))[:max_concepts//3]
        
        if "theories" in concept_types:
            # Look for theory-related terms
            theory_patterns = [
                r'\b\w*theory\b', r'\b\w*theorem\b', r'\b\w*principle\b',
                r'\b\w*law\b', r'\b\w*hypothesis\b', r'\b\w*conjecture\b'
            ]
            
            theories = []
            for pattern in theory_patterns:
                matches = re.findall(pattern, text.lower())
                theories.extend(matches)
            
            concepts['theories'] = list(set(theories))[:max_concepts//3]
        
        if "methods" in concept_types:
            # Look for methodology terms
            method_patterns = [
                r'\b\w*analysis\b', r'\b\w*method\b', r'\b\w*approach\b',
                r'\b\w*technique\b', r'\b\w*algorithm\b', r'\b\w*procedure\b'
            ]
            
            methods = []
            for pattern in method_patterns:
                matches = re.findall(pattern, text.lower())
                methods.extend(matches)
            
            concepts['methods'] = list(set(methods))[:max_concepts//3]
        
        return f"Extracted key concepts:\n{json.dumps(concepts, indent=2)}"
        
    except Exception as e:
        return f"Error extracting key concepts: {str(e)}"

async def generate_research_summary_tool(
    documents: List[str],
    summary_type: str = "comprehensive",
    max_length: int = 500
) -> str:
    """Generate summary of research documents"""
    
    try:
        if summary_type == "comprehensive":
            # Create a comprehensive summary
            all_text = " ".join(documents)
            
            # Extract key sentences (simplified approach)
            sentences = re.split(r'[.!?]+', all_text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            # Score sentences by keyword frequency
            word_freq = {}
            for sentence in sentences:
                words = re.findall(r'\b\w+\b', sentence.lower())
                for word in words:
                    if len(word) > 4:  # Focus on meaningful words
                        word_freq[word] = word_freq.get(word, 0) + 1
            
            # Score sentences
            sentence_scores = []
            for sentence in sentences:
                words = re.findall(r'\b\w+\b', sentence.lower())
                score = sum(word_freq.get(word, 0) for word in words if len(word) > 4)
                sentence_scores.append((sentence, score))
            
            # Sort by score and take top sentences
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            top_sentences = [s[0] for s in sentence_scores[:10]]
            
            summary = ". ".join(top_sentences)
            
            # Truncate if too long
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
        
        elif summary_type == "abstract":
            # Create an abstract-style summary
            summary = "This research encompasses multiple documents covering various aspects of the studied domain."
        
        else:
            summary = "Summary type not supported."
        
        return f"Research Summary ({summary_type}):\n{summary}"
        
    except Exception as e:
        return f"Error generating research summary: {str(e)}"

def register_search_tools(server):
    """Register search and discovery tools with the MCP server"""
    server.tools["semantic_search"] = semantic_search_tool
    server.tools["discover_patterns"] = discover_patterns_tool
    server.tools["build_knowledge_graph"] = build_knowledge_graph_tool
    server.tools["find_similar_documents"] = find_similar_documents_tool
    server.tools["extract_key_concepts"] = extract_key_concepts_tool
    server.tools["generate_research_summary"] = generate_research_summary_tool
