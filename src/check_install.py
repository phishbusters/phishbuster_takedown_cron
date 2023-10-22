import subprocess
import shutil

def is_tool(name):
    """Check if a tool is installed."""
    return shutil.which(name) is not None

def main():
    # Check if Chrome and ChromeDriver are installed
    if not is_tool("google-chrome-stable") or not is_tool("chromedriver"):
        print("Installing Google Chrome and ChromeDriver...")
        subprocess.run(["bash", "../scripts/run.sh"])
    else:
        print("Google Chrome and ChromeDriver are already installed.")

if __name__ == "__main__":
    main()