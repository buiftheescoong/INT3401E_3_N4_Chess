# test_import_global.py
import sys

print("--- Python Executable ---")
print(sys.executable) # In ra đường dẫn của trình thông dịch Python đang được sử dụng
print("--- End Python Executable ---")

print("\n--- sys.version ---")
print(sys.version) # In ra phiên bản Python chi tiết
print("--- End sys.version ---")

print("\n--- sys.path (Python Module Search Paths) ---")
for p in sys.path:
    print(p)
print("--- End sys.path ---")

try:
    print("\n--- Attempting to import 'lichess' ---")
    import lichess
    print(f"Successfully imported 'lichess'")
    
    print(f"\nLocation of imported 'lichess' module (lichess.__file__):")
    try:
        print(lichess.__file__)
    except AttributeError:
        print("'lichess' module does not have a __file__ attribute (might be a built-in or namespace package without __init__.py).")
    
    print(f"\n--- Contents of 'lichess' module (dir(lichess)) ---")
    print(dir(lichess))
    print(f"--- End Contents of 'lichess' module ---")

    # Check for lichess.api.Client
    print(f"\nIs 'api' an attribute of 'lichess'? {'api' in dir(lichess)}")
    if hasattr(lichess, 'api'):
        print(f"Type of 'lichess.api': {type(lichess.api)}")
        try:
            print(f"Location of 'lichess.api' (if it's a module): {getattr(lichess.api, '__file__', 'Not a separate file/module')}")
        except Exception as e_api_file:
            print(f"Could not get __file__ for lichess.api: {e_api_file}")

        print(f"\n--- Contents of 'lichess.api' (dir(lichess.api)) ---")
        print(dir(lichess.api))
        print(f"--- End Contents of 'lichess.api' ---")

        print(f"\nIs 'Client' an attribute of 'lichess.api'? {'Client' in dir(lichess.api)}")
        if hasattr(lichess.api, 'Client'):
            print("Attempting to initialize lichess.api.Client (test)...")
            try:
                # For testing, we don't need a real token if it's just an AttributeError issue
                client_test1 = lichess.api.Client(token="dummy_token_for_attribute_test")
                print("SUCCESS: lichess.api.Client was found and could be referenced.")
            except AttributeError as e_attr1:
                print(f"ATTRIBUTE ERROR initializing lichess.api.Client: {e_attr1}")
            except Exception as e1:
                print(f"OTHER ERROR initializing lichess.api.Client: {e1}")
        else:
            print("FAIL: 'Client' attribute NOT found in lichess.api.")
    else:
        print("FAIL: 'api' attribute NOT found in 'lichess' module.")

    # Check for lichess.Client (top-level)
    print(f"\nIs 'Client' an attribute of 'lichess' (top-level)? {'Client' in dir(lichess)}")
    if hasattr(lichess, 'Client'):
        print("Attempting to initialize lichess.Client (test)...")
        try:
            client_test2 = lichess.Client(token="dummy_token_for_attribute_test")
            print("SUCCESS: lichess.Client (top-level) was found and could be referenced.")
        except AttributeError as e_attr2:
            print(f"ATTRIBUTE ERROR initializing lichess.Client (top-level): {e_attr2}")
        except Exception as e2:
            print(f"OTHER ERROR initializing lichess.Client (top-level): {e2}")
    else:
        print("FAIL: 'Client' attribute (top-level) NOT found in 'lichess' module.")

except ImportError:
    print("\nCRITICAL ERROR: Failed to import 'lichess'.")
    print("Please ensure 'python-lichess' is installed in the Python environment being used.")
    print(f"Python executable: {sys.executable}")
except Exception as e_global:
    print(f"\nAn unexpected global error occurred: {e_global}")

print("\n--- Test Script Finished ---")