import json
from flagsmith import Flagsmith

# 1. Connect to your local Flagsmith instance
flagsmith = Flagsmith(
    environment_key="ser.DsZ34fgrbYdcLjnCaQW63E",
    api_url="http://localhost:8000/api/v1/",  # Change 8000 if your dashboard uses a different port
)

# 2. Fetch the latest flag states from Flagsmith
flags = flagsmith.get_environment_flags()

# 3. Check the Kill Switch first
kill_switch_on = flags.is_feature_enabled("ai_kill_switch")

if kill_switch_on:
    print("🚨 KILL SWITCH IS ON!")
    print("Router action: Blocking AI call and returning safe fallback message.")
else:
    # 4. Read and parse our JSON config
    raw_config = flags.get_feature_value("ai_router_config")
    config = json.loads(raw_config)

    print("✅ KILL SWITCH IS OFF — Router is live!")
    print(f"Model to use:  {config['model']}")
    print(f"System prompt: {config['system_prompt']}")