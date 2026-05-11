import sys
import json
import argparse
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format='[Social-Publisher] %(levelname)s - %(message)s')

def deploy_to_make(platform, text):
    """
    Simulates sending the validated post over to a Make.com webhook.
    Since this is a setup phase, you would replace MAKE_WEBHOOK_URL with your real Hook.
    """
    logging.info(f"Preparing to send publication to: {platform}")
    
    # Placeholder for the user's actual Make URL
    MAKE_WEBHOOK_URL = "https://hook.us1.make.com/XXXXXXXXXXXXX" 
    
    payload = {
        "platform": platform,
        "content_text": text,
        "action": "AUTO_PUBLISH",
        "human_validated": True
    }
    
    encoded_data = json.dumps(payload).encode('utf-8')
    logging.info(f"Payload Created: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    # Simulating the network request to Make...
    try:
        # req = urllib.request.Request(MAKE_WEBHOOK_URL, data=encoded_data, headers={'Content-Type': 'application/json'})
        # response = urllib.request.urlopen(req)
        # logging.info(f"Make.com Webhook trigger success! Response Code: {response.getcode()}")
        
        # We comment the real request out until the Webhook is set up.
        logging.info("--> MOCK API HIT SUCCESSFUL <--")
        logging.info("Your post has been successfully queued for API distribution!")
    except Exception as e:
        logging.error(f"Error executing webhook: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RRSS Automator Script Endpoint')
    parser.add_argument('--platform', type=str, required=True, help='La red social destino')
    parser.add_argument('--text', type=str, required=True, help='Texto o Copy del Post')
    
    args = parser.parse_args()
    deploy_to_make(args.platform, args.text)

