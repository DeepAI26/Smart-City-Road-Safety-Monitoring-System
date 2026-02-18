"""Start the Flask server"""
import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from web_app.app_enhanced import app

if __name__ == "__main__":
    print("=" * 70)
    print("Starting Smart City AI - Enhanced Web Server")
    print("=" * 70)
    print("\nServer starting on http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

