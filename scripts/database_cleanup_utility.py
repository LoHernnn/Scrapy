"""Database and Project Cleanup Utility.

Comprehensive maintenance utility that handles:
- Database table cleanup and reset
- Python cache removal (__pycache__, .pyc files)
- Node.js dependency cleanup (node_modules)
- Build artifact removal (build, dist, .egg-info)
- Log directory cleanup
- Temporary file removal
- Project-specific cleanup (html_output)

Provides both database reset functionality and filesystem cleanup with
interactive prompts for user control.
"""

from scrapy.data.database import CryptoDatabase 
import scrapy.config.settings as conf

import os
import shutil
from pathlib import Path


def clean_pycache(root_dir: str):
    """Remove all __pycache__ directories recursively.
    
    Args:
        root_dir (str): Root directory to search from
        
    Returns:
        int: Number of __pycache__ directories removed
    """
    count = 0
    for dirpath, dirnames, _ in os.walk(root_dir):
        if '__pycache__' in dirnames:
            cache_path = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(cache_path)
                print(f"{cache_path}")
                count += 1
            except Exception as e:
                print(f"Error: {cache_path} - {e}")
    return count


def clean_pyc_files(root_dir: str):
    """Remove all .pyc and .pyo compiled Python files.
    
    Args:
        root_dir (str): Root directory to search from
        
    Returns:
        int: Number of compiled files removed
    """
    count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    print(f"Error: {file_path} - {e}")
    return count


def clean_node_modules(root_dir: str):
    """Remove node_modules directories (typically large in frontend projects).
    
    Args:
        root_dir (str): Root directory to search from
        
    Returns:
        int: Number of node_modules directories removed
    """
    count = 0
    for dirpath, dirnames, _ in os.walk(root_dir):
        if 'node_modules' in dirnames:
            node_modules_path = os.path.join(dirpath, 'node_modules')
            try:
                print(f"Removing: {node_modules_path}")
                shutil.rmtree(node_modules_path)
                count += 1
            except Exception as e:
                print(f"Error: {node_modules_path} - {e}")
    return count


def clean_build_dist(root_dir: str):
    """Remove build artifacts and distribution directories.
    
    Removes: build, dist, .egg-info, .next (Next.js), and out directories.
    
    Args:
        root_dir (str): Root directory to search from
        
    Returns:
        int: Number of build directories removed
    """
    count = 0
    build_dirs = ['build', 'dist', '.egg-info', '.next', 'out']
    
    for dirpath, dirnames, _ in os.walk(root_dir):
        for dirname in dirnames:
            if dirname in build_dirs or dirname.endswith('.egg-info'):
                dir_path = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(dir_path)
                    print(f"{dir_path}")
                    count += 1
                except Exception as e:
                    print(f"Error: {dir_path} - {e}")
    return count


def clean_logs(root_dir: str):
    """Remove all logs directories completely.
    
    Deletes entire logs directories including all log files and subdirectories.
    
    Args:
        root_dir (str): Root directory to search from
        
    Returns:
        int: Number of logs directories removed
    """
    logs_dirs = []
    count = 0
    
    # Find all logs directories
    for dirpath, dirnames, _ in os.walk(root_dir):
        if 'logs' in dirnames:
            logs_dirs.append(os.path.join(dirpath, 'logs'))
    
    for logs_dir in logs_dirs:
        try:
            shutil.rmtree(logs_dir)
            print(f"Removed: {logs_dir}")
            count += 1
        except Exception as e:
            print(f"Error: {logs_dir} - {e}")
    
    return count


def clean_temp_files(root_dir: str):
    """Remove temporary files with common extensions.
    
    Removes files with extensions: .tmp, .temp, .bak, .swp, .log, .cache
    
    Args:
        root_dir (str): Root directory to search from
        
    Returns:
        int: Number of temporary files removed
    """
    count = 0
    temp_extensions = ['.tmp', '.temp', '.bak', '.swp', '.log', '.cache']
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in temp_extensions):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    print(f"Error: {file_path} - {e}")
    return count


def clean_html_output(root_dir: str):
    """Remove html_output directory (project-specific cleanup).
    
    Args:
        root_dir (str): Root directory containing html_output
        
    Returns:
        int: 1 if directory was removed, 0 otherwise
    """
    html_output_dir = os.path.join(root_dir, 'html_output')
    
    if os.path.exists(html_output_dir):
        try:
            shutil.rmtree(html_output_dir)
            print(f"Removed: {html_output_dir}")
            return 1
        except Exception as e:
            print(f"Error: {html_output_dir} - {e}")
    
    return 0


def get_directory_size(path: str) -> int:
    """Calculate total size of directory and all subdirectories in bytes.
    
    Args:
        path (str): Directory path to measure
        
    Returns:
        int: Total size in bytes
    """
    total = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total += os.path.getsize(file_path)
    except Exception:
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format (B, KB, MB, GB, TB).
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., '1.50 MB')
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def clean_project(project_name: str, project_path: str, clean_logs_opt: bool, keep_logs_structure: bool):
    """Clean a specific project with configurable cleanup options.
    
    Performs comprehensive cleanup including Python cache, Node modules (for frontend),
    build artifacts, logs, HTML output, and temporary files. Reports space freed.
    
    Args:
        project_name (str): Name of the project for display purposes
        project_path (str): Path to project directory
        clean_logs_opt (bool): Whether to remove logs directories
        keep_logs_structure (bool): Whether to keep empty logs structure (currently unused)
    """
    if not os.path.exists(project_path):
        print(f"Directory not found: {project_path}")
        return
    
    print(f"\n{project_name}")
    print("   " + "-" * 50)
    
    initial_size = get_directory_size(project_path)
    
    # Python cache
    pycache = clean_pycache(project_path)
    pyc = clean_pyc_files(project_path)
    if pycache + pyc > 0:
        print(f"Python cache: {pycache} dirs, {pyc} files")
    
    # Node modules (for frontend)
    if project_name == "frontend":
        node_modules = clean_node_modules(project_path)
        if node_modules > 0:
            print(f"Node modules: {node_modules} directories")
    
    # Build/dist directories
    build = clean_build_dist(project_path)
    if build > 0:
        print(f"Build/dist: {build} directories")
    
    # Logs
    if clean_logs_opt:
        logs = clean_logs(project_path)
        if logs > 0:
            print(f"Logs: {logs} directories")
    
    # HTML output
    if project_name == "ScrapyTMP":
        html = clean_html_output(project_path)
        if html > 0:
            print(f"HTML output: removed directory")
    
    # Temp files
    temp = clean_temp_files(project_path)
    if temp > 0:
        print(f"Temp files: {temp} files")
    
    final_size = get_directory_size(project_path)
    space_freed = initial_size - final_size
    
    if space_freed > 0:
        print(f"Space freed: {format_size(space_freed)}")
    else:
        print(f"Already clean")


def main():
    """Main entry point for project cleanup utility.
    
    Interactive cleanup utility that:
    1. Calculates initial project size
    2. Prompts user for cleanup preferences
    3. Cleans multiple project directories (ScrapyTMP, frontend, scrapy)
    4. Reports space freed for each project
    5. Shows total cleanup summary
    
    User can choose to clean all projects and optionally remove logs.
    """
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("SCRAPY PROJECT - GLOBAL CLEANUP")
    print("=" * 60)
    print(f"Root directory: {project_root}\n")
    
    # Calculate initial size
    initial_size = get_directory_size(str(project_root))
    print(f"Initial total size: {format_size(initial_size)}\n")
    
    # Get user preferences
    print("Cleanup options:")
    response = input("   Clean all projects? (y/n): ").lower().strip()
    if response != 'y':
        print("Cleanup cancelled")
        return
    
    clean_logs_opt = input("   Remove logs directories? (y/n): ").lower().strip() == 'y'
    keep_logs_structure = False
    if clean_logs_opt:
        keep_logs_structure = input("   Keep logs directory structure? (y/n): ").lower().strip() == 'y'
    
    print("\n" + "=" * 60)
    print(" Starting cleanup...")
    print("=" * 60)
    
    # Define projects to clean
    projects = [
        ("ScrapyTMP", project_root),
        ("frontend", project_root / "frontend"),
        ("scrapy", project_root / "scrapy")
    ]
    
    # Clean each project
    for project_name, project_path in projects:
        clean_project(project_name, str(project_path), clean_logs_opt, keep_logs_structure)
    
    # Calculate final size
    final_size = get_directory_size(str(project_root))
    total_freed = initial_size - final_size
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)
    print(f"Final total size: {format_size(final_size)}")
    print(f"Total space freed: {format_size(total_freed)}")
    print("=" * 60)

def reset_all():
    """Reset database tables and initialize fresh structure.
    
    Performs database maintenance based on configuration flags:
    - Drops market data tables if configured
    - Drops sentiment analysis tables if configured
    - Drops trading scores and trades tables if configured
    - Recreates all necessary tables if configured
    - Inserts initial Twitter accounts for tracking if configured
    
    All operations are controlled by flags in scrapy.config.settings.
    """
    db = CryptoDatabase()
    if conf.DROP_MARKET_DATA_TABLES:
        db.drop_tables()
    if conf.DROP_SENTIMENT_DATA_TABLES:
        db.drop_sentiment_tables()
    if conf.DROP_SCORES_AND_TRADES_TABLES:
        db.drop_tables_scores_and_trade()
    
    if conf.CREATE_ALL_TABLES_IF_MISSING:
        db.create_table_listing()
        db.create_table_crypto_ranks()
        db.create_table_base()
        db.create_table_detail()
        db.create_table_data_binance()
        db.create_sentiment_tables()
        db.create_score_table()
        db.create_trade_table()
    
    if conf.ADD_ALL_TWITTER_ACCOUNTS:
        accounts = conf.TWITTER_ACCOUNTS
        for account_name in accounts:
            db.insert_new_account(account_name)
    db.close()
        
if __name__ == "__main__":
    reset_all()
    main()
    