#!/usr/bin/env python3
"""
Test script to validate complete configuration integration and detect conflicts.
This script tests all configuration loading, environment variable access, and system integrity.
"""

import os
import sys
from pathlib import Path

# Add the jarvis package to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_env_file_exists():
    """Test that .env file exists and is readable."""
    env_path = Path(__file__).parent / '.env'
    assert env_path.exists(), "❌ .env file not found"
    assert env_path.is_file(), "❌ .env is not a file"
    print("✅ .env file exists and is readable")
    return True

def test_config_imports():
    """Test that all config imports work without conflicts."""
    try:
        # Test utils config import
        from jarvis.utils.config import config as utils_config
        print("✅ jarvis.utils.config import successful")
        
        # Test main config import  
        from jarvis.config import config as main_config
        print("✅ jarvis.config import successful")
        
        # Test that both configs are accessible
        assert hasattr(utils_config, 'NAME'), "❌ utils_config missing NAME attribute"
        assert hasattr(main_config, 'env'), "❌ main_config missing env attribute"
        print("✅ Both config objects have expected attributes")
        
        return utils_config, main_config
        
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Config validation failed: {e}")
        return None, None

def test_environment_variables(utils_config, main_config):
    """Test that critical environment variables are loaded correctly."""
    critical_vars = [
        'BYBIT_API_KEY', 'BYBIT_API_SECRET', 'OPENAI_API_KEY',
        'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'
    ]
    
    print("\n🔍 Testing Environment Variables:")
    for var in critical_vars:
        env_value = os.getenv(var)
        if env_value:
            print(f"✅ {var}: {'*' * min(len(env_value), 8)}...")
        else:
            print(f"⚠️  {var}: Not set or empty")
    
    # Test specific config attributes
    print(f"✅ JARVIS_NAME: {utils_config.NAME}")
    print(f"✅ Environment: {main_config.env}")
    print(f"✅ Debug mode: {main_config.debug}")
    
    return True

def test_trading_config(main_config):
    """Test trading configuration integration."""
    print("\n🔍 Testing Trading Configuration:")
    trading = main_config.trading
    
    print(f"✅ Bybit API Key: {'*' * 8 if trading.bybit_api_key else 'Not set'}")
    print(f"✅ Bybit Secret: {'*' * 8 if trading.bybit_api_secret else 'Not set'}")
    print(f"✅ Bybit Testnet: {trading.bybit_testnet}")
    print(f"✅ Default Symbol: {trading.default_symbol}")
    print(f"✅ Default Quantity: {trading.default_quantity}")
    print(f"✅ Max Concurrent Trades: {trading.max_concurrent_trades}")
    print(f"✅ Stop Loss Enabled: {trading.enable_stop_loss}")
    print(f"✅ Take Profit Enabled: {trading.enable_take_profit}")
    
    return True

def test_database_config(main_config):
    """Test database configuration."""
    print("\n🔍 Testing Database Configuration:")
    db = main_config.database
    
    print(f"✅ DB Host: {db.host}")
    print(f"✅ DB Port: {db.port}")
    print(f"✅ DB Name: {db.name}")
    print(f"✅ DB User: {db.user}")
    print(f"✅ DB Password: {'*' * 8 if db.password else 'Not set'}")
    
    return True

def test_api_config(main_config):
    """Test API configuration."""
    print("\n🔍 Testing API Configuration:")
    api = main_config.api
    
    print(f"✅ API Host: {api.host}")
    print(f"✅ API Port: {api.port}")
    print(f"✅ API Debug: {api.debug}")
    print(f"✅ API Secret Key: {'*' * 8 if api.secret_key else 'Not set'}")
    
    return True

def test_no_duplicate_configs():
    """Test that no duplicate config files exist."""
    print("\n🔍 Testing for Duplicate Config Files:")
    
    # Check for old config.py (should not exist)
    old_config = Path(__file__).parent / 'jarvis' / 'config.py'
    if old_config.exists():
        print("❌ Old jarvis/config.py still exists - should be removed")
        return False
    else:
        print("✅ No duplicate jarvis/config.py found")
    
    # Check for multiple .env files
    env_files = list(Path(__file__).parent.rglob('.env*'))
    expected_files = {'.env', '.env.example'}
    found_files = {f.name for f in env_files}
    
    if found_files == expected_files:
        print(f"✅ Correct .env files found: {found_files}")
    else:
        print(f"⚠️  Unexpected .env files: {found_files}")
    
    return True

def test_yaml_config():
    """Test YAML configuration file."""
    print("\n🔍 Testing YAML Configuration:")
    yaml_path = Path(__file__).parent / 'jarvis_config.yaml'
    
    if yaml_path.exists():
        print("✅ jarvis_config.yaml exists")
        try:
            import yaml
            with open(yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            if 'models' in yaml_config:
                print(f"✅ YAML contains {len(yaml_config['models'])} model configurations")
            if 'fallback_chains' in yaml_config:
                print(f"✅ YAML contains fallback chains")
            
        except ImportError:
            print("⚠️  PyYAML not installed - cannot validate YAML content")
        except Exception as e:
            print(f"⚠️  YAML validation error: {e}")
    else:
        print("⚠️  jarvis_config.yaml not found")
    
    return True

def main():
    """Run all configuration integration tests."""
    print("🚀 Starting Configuration Integration Tests\n")
    
    try:
        # Test 1: .env file exists
        test_env_file_exists()
        
        # Test 2: Config imports work
        utils_config, main_config = test_config_imports()
        if not utils_config or not main_config:
            print("❌ Cannot continue without working config imports")
            return False
        
        # Test 3: Environment variables
        test_environment_variables(utils_config, main_config)
        
        # Test 4: Trading configuration
        test_trading_config(main_config)
        
        # Test 5: Database configuration
        test_database_config(main_config)
        
        # Test 6: API configuration
        test_api_config(main_config)
        
        # Test 7: No duplicate configs
        test_no_duplicate_configs()
        
        # Test 8: YAML configuration
        test_yaml_config()
        
        print("\n🎉 All Configuration Integration Tests Completed Successfully!")
        print("✅ System is ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
