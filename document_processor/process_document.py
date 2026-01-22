import sys
import os
import json
import requests
import uuid

def load_config():
    """
    Load configuration from config.json file.
    
    Returns:
        dict: Configuration dictionary with supported extensions, chunking strategy, and API endpoint
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    config_defaults = {
        'supported_extensions': ['.txt', '.md'],
        'chunking_strategy': 'bytitle',
        'api_endpoint': None
    }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Extract actual values from the config structure
        supported_extensions = config.get('supported_extensions', {}).get('value', config_defaults['supported_extensions'])
        chunking_strategy = config.get('chunking_strategy', {}).get('value', config_defaults['chunking_strategy'])
        api_endpoint = config.get('api_endpoint', {}).get('value', config_defaults['api_endpoint'])
        
        
    except Exception as e:
        print(f"Warning: Error loading config ({e}). Using defaults.")
        supported_extensions = config_defaults['supported_extensions']
        chunking_strategy = config_defaults['chunking_strategy']
        api_endpoint = config_defaults['api_endpoint']
    
    return {
            'supported_extensions': supported_extensions,
            'chunking_strategy': chunking_strategy,
            'api_endpoint': api_endpoint
        }

def parse_arguments():
    """
    Parse command line arguments and extract file paths.
    
    Returns:
        list: Array of file paths from command line arguments
    """
    # Check if arguments are provided
    if len(sys.argv) < 2:
        print("Usage: python process_document.py <file_path> [<file_path2> ...]")
        return []
    
    # Get all file paths from command line arguments (skip the script name)
    file_paths = sys.argv[1:]
    
    return file_paths

def validate_files(file_paths, supported_extensions):
    """
    Validate file paths - check if files exist and have supported extensions.
    
    Args:
        file_paths: List of file paths to validate
        supported_extensions: List of allowed file extensions from config
    
    Returns:
        tuple: (success: bool, valid_file_paths: list)
               success is True if all provided files are valid, False otherwise
               valid_file_paths contains paths of valid files
    """
    # Convert to tuple for consistency
    SUPPORTED_EXTENSIONS = tuple(supported_extensions)
    
    valid_file_paths = []
    all_valid = True
    
    for file_path in file_paths:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File does not exist - {file_path}")
            all_valid = False
            continue
        
        # Check if file has supported extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in SUPPORTED_EXTENSIONS:
            print(f"Error: Unsupported file type '{ext}' - {file_path}")
            print(f"  Supported file types: {', '.join(SUPPORTED_EXTENSIONS)}")
            all_valid = False
            continue
        
        # File is valid, add to list
        valid_file_paths.append(file_path)
    
    return (all_valid, valid_file_paths)

def check_unstructured_library():
    """
    Check if the unstructured library is installed.
    
    Returns:
        bool: True if installed, False otherwise
    """
    try:
        import unstructured
        return True
    except ImportError:
        print("Error: The 'unstructured' library is not installed.")
        print("To install it, run one of the following commands:")
        print("  pip install unstructured")
        print("  pip install \"unstructured[all-docs]\"  # For full document support")
        print("For more information, visit: https://unstructured-io.github.io/unstructured/installing.html")
        return False

def load_documents(file_paths):
    """
    Load documents using unstructured library and partition them into elements.
    
    Args:
        file_paths: List of file paths to load
    
    Returns:
        dict: Dictionary mapping file paths to their list of elements.
              Structure: {
                  'path/to/file1.md': [Element1, Element2, ...],
                  'path/to/file2.txt': [Element1, Element2, ...],
                  ...
              }
              Each Element is an unstructured Element object (e.g., Title, NarrativeText, etc.)
    """
    print("Importing unstructured libraries...")
    from unstructured.partition.md import partition_md
    from unstructured.partition.text import partition_text
    
    documents = {}
    print("Loading documents...")
    for file_path in file_paths:
        print(f"Processing: {file_path}")
        
        # Get file extension to determine which partitioner to use
        _, ext = os.path.splitext(file_path)
        
        try:
            if ext.lower() == '.md':
                elements = partition_md(filename=file_path)
            elif ext.lower() == '.txt':
                elements = partition_text(filename=file_path)
            else:
                print(f"  Skipping unsupported file type: {ext}")
                continue
            
            documents[file_path] = elements
            print(f"  Loaded {len(elements)} partitions")
            
        except Exception as e:
            print(f"  Error loading file: {e}")
            documents[file_path] = []
    
    return documents

def chunk_documents(documents, chunking_strategy, show_preview = True):
    """
    Apply chunking strategy to documents using unstructured.chunking.
    
    Args:
        documents: Dictionary mapping file paths to their list of elements
        chunking_strategy: Strategy to use for chunking ('alltext', 'bytitle', or 'characters50')
    
    Returns:
        dict: Dictionary mapping file paths to their list of chunks.
              Structure: {
                  'path/to/file1.md': [CompositeElement1, CompositeElement2, ...],
                  'path/to/file2.txt': [CompositeElement1, CompositeElement2, ...],
                  ...
              }
              Each chunk is an unstructured CompositeElement that combines multiple original elements
    """
    print(f"Applying chunking strategy: {chunking_strategy}")
    from unstructured.chunking.title import chunk_by_title
    from unstructured.chunking.basic import chunk_elements
    
    chunked_documents = {}
    
    for file_path, elements in documents.items():
        print(f"Chunking: {file_path}")
        print(f"  Original partitions: {len(elements)}")
        
        try:
            if chunking_strategy == 'alltext':
                # Combine all elements into one chunk
                # Use chunk_elements with very large max_characters to keep everything together
                chunks = chunk_elements(
                    elements,
                    max_characters=1000000,  # Very large number to keep all text together
                    new_after_n_chars=1000000
                )
                
            elif chunking_strategy == 'characters50':
                # Chunk with max_characters=100, new_after_n_chars=50, overlap=10
                chunks = chunk_elements(
                    elements,
                    max_characters=100,
                    new_after_n_chars=50,
                    overlap=10
                )

            #elif chunking_strategy == 'bytitle':
            else:
                if chunking_strategy != 'bytitle':
                    print(f"  Warning: Unknown chunking strategy '{chunking_strategy}'. Using default (bytitle).")
                # Create chunks separated by title elements
                chunks = chunk_by_title(
                    elements,
                    combine_text_under_n_chars=0,  # Don't combine small sections
                    multipage_sections=True
                )
            
            chunked_documents[file_path] = chunks
            print(f"  Chunks created: {len(chunks)}")
            
            if show_preview == True:
                # Display chunk preview
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    preview = str(chunk)[:100].replace('\n', ' ')
                    print(f"    Chunk {i+1}: {preview}...")
                if len(chunks) > 3:
                    print(f"    ... and {len(chunks) - 3} more chunks")
                
        except Exception as e:
            print(f"  Error chunking file: {e}")
            chunked_documents[file_path] = elements
    
    return chunked_documents

def upload_chunks(chunked_documents, api_endpoint):
    """
    Upload chunked documents to the specified API endpoint.
    
    Args:
        chunked_documents: Dictionary mapping file paths to their list of chunks
        api_endpoint: URL of the API endpoint to upload chunks to
    
    Returns:
        dict: Summary of upload results including success count, failure count, and details
    
    JSON Structure Sent to Server (POST request):
        {
            "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
            "content": "chunk content as string",
            "metadata": {
                "source": "path/to/file.md",
                "group_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "chunk_index": 0,
                "total_chunks": 5
            }
        }
    
    Note:
        - chunk_id: Unique UUID for each chunk
        - group_id: UUID shared by all chunks from the same file
        - chunk_index: Replaces 'page' field in server interface
    """
    if not api_endpoint:
        print("Warning: No API endpoint configured. Skipping upload.")
        return {'success': 0, 'failed': 0, 'total': 0}
    
    print(f"Uploading chunks to API: {api_endpoint}")
    
    success_count = 0
    failed_count = 0
    total_chunks = 0
    MAX_RETRIES = 3
    
    for file_path, chunks in chunked_documents.items():
        # Generate a unique group_id for all chunks from this file
        group_id = str(uuid.uuid4())
        print(f"Uploading chunks from: {file_path} (group_id: {group_id})")
        
        for i, chunk in enumerate(chunks):
            total_chunks += 1
            
            # Generate a unique chunk_id for this chunk
            chunk_id = str(uuid.uuid4())
            
            # Prepare payload
            payload = {
                'chunk_id': chunk_id,
                'content': str(chunk),
                'metadata': {
                    'source': file_path,
                    'group_id': group_id,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            }
            
            # Retry logic - try up to MAX_RETRIES times
            upload_successful = False
            last_error = None
            
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    # Send POST request to API
                    response = requests.post(
                        api_endpoint,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    # Check if request was successful
                    response.raise_for_status()
                    
                    upload_successful = True
                    success_count += 1
                    print(f"  ✓ Chunk {i+1}/{len(chunks)} uploaded successfully (attempt {attempt})")
                    break  # Exit retry loop on success
                    
                except requests.exceptions.RequestException as e:
                    last_error = e
                    if attempt < MAX_RETRIES:
                        print(f"  ⚠ Chunk {i+1}/{len(chunks)} upload failed (attempt {attempt}/{MAX_RETRIES}), retrying...")
                    else:
                        print(f"  ✗ Failed to upload chunk {i+1}/{len(chunks)} after {MAX_RETRIES} attempts: {e}")
            
            # If all retries failed, increment failed count
            if not upload_successful:
                failed_count += 1
    
    # Print summary
    print(f"Upload Summary:")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")
    
    return {
        'success': success_count,
        'failed': failed_count,
        'total': total_chunks
    }

def main():
    # Load configuration
    config = load_config()
    print(f"Loaded config: {', '.join([f"{key}={value}" for key, value in config.items()])}")
    
    # Parse command line arguments
    file_paths = parse_arguments()
    if not file_paths:
        sys.exit(1)
    
    # Validate the file paths
    success, valid_file_paths = validate_files(file_paths, config['supported_extensions'])
    if not success:
        print(f"Validation failed. Please provide valid {', '.join(config['supported_extensions'])} files that exist.")
        sys.exit(1)
    
    # Import unstructured library and load documents
    ## Check if unstructured library is installed
    if not check_unstructured_library():
        sys.exit(1)
    ## Load documents
    documents = load_documents(valid_file_paths)
    
    # Apply chunking strategy
    chunked_documents = chunk_documents(documents, config['chunking_strategy'], show_preview=True)
    
    # Upload chunks to API endpoint if configured
    upload_chunks(chunked_documents, config['api_endpoint'])


if __name__ == "__main__":
    main()
