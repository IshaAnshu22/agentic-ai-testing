import sys
from orchestrator.supervisor import Supervisor
from utils.logger import setup_logger

logger = setup_logger("main")

def main():
    print("Welcome to the Agentic SUT Test CLI.")
    print("Type 'exit' to quit.")
    
    supervisor = Supervisor()
    
    while True:
        try:
            user_input = input("\nUser> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not user_input.strip():
                continue
                
            response = supervisor.run(user_input)
            print(f"\nAgent> {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
