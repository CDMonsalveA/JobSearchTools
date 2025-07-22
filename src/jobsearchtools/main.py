# Main entry point for the Job Search Tools application
import time


def main():
    while True:
        print(
            f"running job search tools... {time.strftime('%Y-%m-%d %H:%M:%S')}",
            end="\r",
        )
        time.sleep(1)  # Sleep for 1 second before the next iteration


if __name__ == "__main__":
    main()
