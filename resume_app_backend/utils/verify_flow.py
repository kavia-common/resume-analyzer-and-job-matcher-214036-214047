import httpx
import time
import uuid
import os

# Configuration
BASE_URL = "http://localhost:8000"
UPLOAD_URL = f"{BASE_URL}/api/v1/resumes/upload"
STATUS_URL_TPL = f"{BASE_URL}/api/v1/analysis/{{analysis_id}}/status"
RESULTS_URL_TPL = f"{BASE_URL}/api/v1/analysis/{{analysis_id}}/results"
USER_ID = str(uuid.uuid4())
FILE_CONTENT = "This is a simple resume with skills like Python and Java."
FILE_NAME = "test_resume.txt"

def run_verification():
    """Runs the end-to-end verification flow."""
    try:
        print("--- Starting Verification ---")
        print(f"User ID: {USER_ID}")

        # Create a dummy resume file in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, FILE_NAME)
        with open(file_path, "w") as f:
            f.write(FILE_CONTENT)

        # 1. Upload resume
        print(f"\n1. Uploading resume to {UPLOAD_URL}...")
        with open(file_path, "rb") as f:
            files = {"file": (FILE_NAME, f, "text/plain")}
            data = {"user_id": USER_ID}
            
            # Using verify=False to ignore SSL issues in test environments
            with httpx.Client(verify=False) as client:
                response = client.post(UPLOAD_URL, files=files, data=data)

        if response.status_code != 201:
            print(f"  [FAIL] Expected status 201, but got {response.status_code}")
            print(f"  Response body: {response.text}")
            return

        print(f"  [SUCCESS] Got status {response.status_code}")
        response_json = response.json()
        analysis_id = response_json.get("analysis_id")

        if not analysis_id:
            print("  [FAIL] 'analysis_id' not found in response.")
            print(f"  Response JSON: {response_json}")
            return

        print(f"  Analysis ID: {analysis_id}")

        # 2. Poll for status
        status_url = STATUS_URL_TPL.format(analysis_id=analysis_id)
        print(f"\n2. Polling status at {status_url}...")

        with httpx.Client(verify=False) as client:
            for i in range(20):  # Poll for max 20 seconds
                time.sleep(1)
                status_response = client.get(status_url)

                if status_response.status_code != 200:
                    print(f"  [WARN] Polling failed with status {status_response.status_code}.")
                    continue

                status_json = status_response.json()
                status = status_json.get("status")
                print(f"  Attempt {i+1}: Status is '{status}'")

                if status == "complete":
                    print("  [SUCCESS] Analysis completed.")
                    break
                elif status == "failed":
                    print("  [FAIL] Analysis failed.")
                    # Still try to fetch results to see if there is more info
                    break
            else:
                print("  [FAIL] Timeout: Analysis did not complete in time.")
                return
        
        # 3. Get results
        results_url = RESULTS_URL_TPL.format(analysis_id=analysis_id)
        print(f"\n3. Fetching results from {results_url}...")
        with httpx.Client(verify=False) as client:
            results_response = client.get(results_url)

        if results_response.status_code != 200:
            print(f"  [FAIL] Expected status 200, but got {results_response.status_code}")
            print(f"  Response body: {response.text}")
            return

        print(f"  [SUCCESS] Got status {results_response.status_code}")
        results_json = results_response.json()
        print("  Results received:")
        import json
        print(json.dumps(results_json, indent=2))

    except httpx.RequestError as e:
        print(f"\n[ERROR] An HTTP request failed: {e}")
        print("Please ensure the backend service is running and accessible.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
    finally:
        print("\n--- Verification Finished ---")
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    run_verification()
