import subprocess
import argparse
import sys

def parse(s):
    parser = argparse.ArgumentParser(s)
    parser.add_argument('-n', '--name', default='input')

    parsed_args = parser.parse_args()
    return parsed_args.name

def run_program(script_name, *args):
    """Run a Python script with arguments and pipe its output to our stdout"""
    try:
        # Prepare the command (python script.py arg1 arg2...)
        command = [sys.executable, script_name] + list(args)
        
        print(f"\nStarting {script_name} with arguments: {args if args else 'None'}...")
        
        # Run the script and capture its output in real-time
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Print each line of output as it comes
        for line in process.stdout:
            print(line, end='')
            
        # Wait for the process to complete
        process.wait()
        
        # Check return code
        if process.returncode != 0:
            print(f"Warning: {script_name} exited with code {process.returncode}", file=sys.stderr)
            
        return process.returncode
            
    except Exception as e:
        print(f"Error running {script_name}: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    name: str = parse(sys.argv[0])

    run_program('lexical_analyse.py', '-i', name)


    run_program('parser.py', '-n', name)