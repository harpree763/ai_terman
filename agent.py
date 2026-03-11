
#!/usr/bin/env python3
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
import sys
import json
import subprocess
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- ANSI COLOR CODES ---
GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# --- SYSTEM INSTRUCTION ---
SYSTEM_INSTRUCTION = """
You are a world-class Kali Linux and cybersecurity expert. 
The user will provide a request in English, which may be simple or complex.

CRITICAL RULES FOR COMPLEX PROMPTS:
1. If a prompt has multiple parts (e.g., "find a file and then search for text"), break it down into a logical sequence.
2. Use shell operators like pipes (|), AND (&&), or semicolons (;) to chain commands efficiently.
3. For search tasks, use robust tools like 'find', 'grep', 'locate', or 'awk'.
4. If a task requires variables or loops, provide a one-liner bash script.

OUTPUT FORMAT (JSON ONLY):
{
  "command": "The complete, executable shell command(s).",
  "explanation": "A high-level overview of the final result.",
  "steps": ["Step 1: Description", "Step 2: Description", ...],
  "is_dangerous": boolean
}

5. Assume the user is root or has sudo.
6. Safety: Provide valid commands for security auditing and system management.
"""

def load_env():
    """Manually load .env file."""
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip('\'"')
                        os.environ[key.strip()] = value.strip()
            return True
        except Exception:
            return False
    return False

def print_banner():
    banner = f"""
{CYAN}{BOLD}┌──────────────────────────────────────────────────────────┐
│             KALI {RESET}{RED}AI{RESET}{CYAN}{BOLD} INTEGRATED TERMINAL                │
│       {RESET}{BLUE}Multi-Step Reasoning Engine v1.4{RESET}{CYAN}{BOLD}           │
└──────────────────────────────────────────────────────────┘{RESET}
    """
    print(banner)

def get_ai_response(prompt, model):
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response.candidates or response.candidates[0].finish_reason == 3:
             print(f"{RED}[!] Error: Request was blocked by safety filters.{RESET}")
             return None

        data = json.loads(response.text)
        return data
    except Exception as e:
        if "finish_reason" in str(e) or "Part" in str(e):
            print(f"{RED}[!] Error: AI refused due to safety filters. Try rephrasing.{RESET}")
        else:
            print(f"{RED}[!] AI Error: {e}{RESET}")
        return None

def execute_command(command):
    print(f"{YELLOW}[*] Running: {BOLD}{command}{RESET}\n")
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        if process.returncode == 0:
            print(f"\n{GREEN}[+] Success.{RESET}")
        else:
            print(f"\n{RED}[!] Failed (Exit Code: {process.returncode}){RESET}")
            
    except Exception as e:
        print(f"{RED}[!] Execution error: {e}{RESET}")

def main():
    load_env()
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print(f"{RED}[!] API_KEY not found in .env{RESET}")
        sys.exit(1)

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=SYSTEM_INSTRUCTION,
            safety_settings=safety_settings
        )
    except Exception as e:
        print(f"{RED}[!] Init Failed: {e}{RESET}")
        sys.exit(1)

    print_banner()

    while True:
        try:
            print(f"{GREEN}┌──({BOLD}root㉿kali{RESET}{GREEN})-[{CYAN}~{GREEN}]")
            user_input = input(f"└─{BOLD}${RESET} ").strip()

            if not user_input: continue
            if user_input.lower() in ['exit', 'quit', 'clear']:
                if user_input.lower() == 'clear':
                    os.system('clear')
                    print_banner()
                    continue
                break

            print(f"{BLUE}[~] Thinking step-by-step...{RESET}")
            result = get_ai_response(user_input, model)
            
            if result:
                command = result.get("command")
                explanation = result.get("explanation")
                steps = result.get("steps", [])
                is_dangerous = result.get("is_dangerous", False)

                #print(f"\n{CYAN}{BOLD}PLAN:{RESET}")
                #for i, step in enumerate(steps, 1):
                    #print(f" {CYAN}{i}.{RESET} {step}")

                #print(f"\n{YELLOW}{BOLD}COMMAND:{RESET} {BOLD}{command}{RESET}")
                #print(f"{BLUE}GOAL:{RESET} {explanation}")

                if is_dangerous:
                    print(f"{RED}{BOLD}[!] DANGER: High-risk operation detected.{RESET}")

                confirm = 'y'
                if confirm == 'y':
                    execute_command(command)
                else:
                    print(f"{BLUE}[-] Aborted.{RESET}")
            
            print("") 

        except KeyboardInterrupt:
            print(f"\n{YELLOW}[!] Use 'exit' to quit.{RESET}")
        except Exception as e:
            print(f"{RED}[!] Error: {e}{RESET}")

    print(f"{CYAN}Session ended.{RESET}")

if __name__ == "__main__":
    main()
