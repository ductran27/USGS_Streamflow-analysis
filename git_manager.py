"""
Git Manager Module
Handles automatic Git commits and pushes
"""

import subprocess
from pathlib import Path
from datetime import datetime


class GitManager:
    """Manage Git operations for automatic commits"""
    
    def __init__(self, config):
        """Initialize Git manager with configuration"""
        self.config = config
        self.repo_path = Path.cwd()
    
    def commit_and_push(self, commit_message):
        """
        Add, commit, and push changes to GitHub
        
        Args:
            commit_message: str, commit message
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if there are changes to commit
            if not self._has_changes():
                print("  No changes to commit")
                return False
            
            # Add all changes
            self._run_git_command(['add', '.'])
            print("  ✓ Changes staged")
            
            # Commit
            self._run_git_command(['commit', '-m', commit_message])
            print("  ✓ Changes committed")
            
            # Push to remote
            if self.config.get('auto_push', True):
                self._run_git_command(['push'])
                print("  ✓ Changes pushed to remote")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            return False
    
    def _has_changes(self):
        """Check if there are uncommitted changes"""
        try:
            result = self._run_git_command(['status', '--porcelain'], capture_output=True)
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def _run_git_command(self, args, capture_output=False):
        """
        Run a git command
        
        Args:
            args: list of command arguments
            capture_output: bool, whether to capture output
        
        Returns:
            CompletedProcess if capture_output=True, None otherwise
        """
        cmd = ['git'] + args
        
        if capture_output:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result
        else:
            subprocess.run(
                cmd,
                cwd=self.repo_path,
                check=True
            )
    
    def get_repo_status(self):
        """Get current repository status"""
        try:
            result = self._run_git_command(['status'], capture_output=True)
            return result.stdout
        except:
            return "Unable to get repository status"
    
    def get_last_commit(self):
        """Get information about the last commit"""
        try:
            result = self._run_git_command(
                ['log', '-1', '--pretty=format:%h - %s (%cr)'],
                capture_output=True
            )
            return result.stdout
        except:
            return "Unable to get last commit"
