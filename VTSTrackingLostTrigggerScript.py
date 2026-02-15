import asyncio
import pyvts
import json
import os
import obsws_python as obs

#Required Libs
#pip install obsws-python
#pip install pyvts


PLUGIN_INFO = {
    "plugin_name": "TrackingHider",
    "developer": "KatVolts",
    "authentication_token_path": "./token.txt"
}

def set_source_visibility(scene_name, source_name, is_visible, host='localhost', port=4455, password='VrYlmRVkidEkH5TB'):
    """
    Connects to OBS and sets the visibility of a specific source in a scene.
    
    :param scene_name: The name of the scene containing the source.
    :param source_name: The name of the source/input to show or hide.
    :param is_visible: Boolean (True to show, False to hide).
    """
    try:
        # 1. Establish the connection
        cl = obs.ReqClient(host=host, port=port, password=password)

        # 2. Get the Scene Item ID (required for v5 protocol)
        # We need the ID to target the specific instance of the source in that scene
        scene_item_id = None
        items = cl.get_scene_item_list(scene_name)
        
        for item in items.scene_items:
            if item['sourceName'] == source_name:
                scene_item_id = item['sceneItemId']
                break

        if scene_item_id is None:
            print(f"Error: Source '{source_name}' not found in scene '{scene_name}'.")
            return

        # 3. Set the visibility
        cl.set_scene_item_enabled(scene_name, scene_item_id, is_visible)
        
        status = "Visible" if is_visible else "Hidden"
        print(f"Successfully set '{source_name}' in '{scene_name}' to {status}.")

    except Exception as e:
        print(f"Failed to connect or update OBS: {e}")



async def authenticate_with_retry(vts):
    """Handles authentication and deletes bad tokens automatically."""
    
    # 1. Read existing token or generate a new request
    await vts.request_authenticate_token()
    
    # 2. Try to login (Returns True or False)
    is_authenticated = await vts.request_authenticate()
    
    if is_authenticated:
        print("Authentication Successful.")
        return True
    
    # 3. If Failed, delete token and retry
    print("Authentication Failed (Token invalid). Deleting old token...")
    
    if os.path.exists("./token.txt"):
        os.remove("./token.txt")
        
    print("Requesting new token... PLEASE CLICK 'ALLOW' IN VTUBE STUDIO!")
    await vts.request_authenticate_token()
    
    # 4. Try login again
    is_authenticated = await vts.request_authenticate()
    
    if is_authenticated:
        print("Re-Authentication Successful!")
        return True
    else:
        print("FATAL: Could not authenticate even after retry.")
        return False

async def connect_and_listen():
    vts = pyvts.vts(plugin_info=PLUGIN_INFO)

    print("Attempting to connect to VTube Studio...")
    await vts.connect()
    print("Connected.")

    # Run the robust auth logic
    if not await authenticate_with_retry(vts):
        await vts.close()
        return # Stop if we can't log in

    # Subscribe to Tracking Events
    subscribe_msg = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "TrackingSubscribe",
        "messageType": "EventSubscriptionRequest",
        "data": {
            "eventName": "TrackingStatusChangedEvent",
            "config": {
                "subscribe": True
            }
        }
    }
    
    await vts.request(subscribe_msg)
    print(f"Running!")

    # Inner Loop: Listen for messages
    while True:
        try:
            recv_text = await vts.websocket.recv()
            msg = json.loads(recv_text)
            
            if msg.get("messageType") == "TrackingStatusChangedEvent":
                data = msg.get("data", {})
                face_found = data.get("faceFound") 
                
                if face_found is False:
                    print("[EVENT] Tracking LOST!")
                    set_source_visibility("TestScene", "VtubeStudio", False)
                    set_source_visibility("TestScene", "KatReact", True)
                
                elif face_found is True:
                    print("[EVENT] Tracking FOUND!")
                    set_source_visibility("TestScene", "VtubeStudio", True)
                    set_source_visibility("TestScene", "KatReact", False)
        
        except Exception as e:
            # Propagate error up to trigger reconnect
            raise e

async def main():
    while True:
        try:
            await connect_and_listen()
        except KeyboardInterrupt:
            print("Stopping script...")
            break
        except Exception as e:
            print(f"Connection lost or error: {e}")
            print("Reconnecting in 3 seconds...")
            await asyncio.sleep(3) 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass