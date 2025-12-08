import requests
import sys

def test_tts():
    url = "http://localhost:8000/v1/audio/speech"
    
    # Test 1: English (Default Voice from ENV or fallback)
    print("Test 1: English (Default Voice)")
    data_en = {
        "instructions": "Hello! This is a test using the default voice.",
        # "voice" omitted to test default
    }
    send_request(url, data_en, "output_en.wav")

    # Test 2: Arabic with specific voice (string)
    print("\nTest 2: Arabic with voice 'alloy'")
    data_ar = {
        "instructions": "مرحبا, هذا اختبار للنظام.",
        "voice": "alloy", # String identifier
        "language": "ar"
    }
    send_request(url, data_ar, "output_ar.wav")

    # Test 3: Speaker Index (as string digit)
    print("\nTest 3: Speaker Index '0' (backward compatibility)")
    data_idx = {
        "instructions": "Testing speaker index 0.",
        "voice": "0"
    }
    send_request(url, data_idx, "output_idx_0.wav")

def send_request(url, data, filename):
    print(f"Sending request to {url} with data: {data}")
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Success! Audio saved to {filename}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_tts()
