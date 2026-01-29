import sys
import os

# Add src to path for development mode
if not getattr(sys, 'frozen', False):
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

try:
    from sd_backup_tool.__main__ import main
except Exception as e:
    import traceback
    print("\n" + "!"*60)
    print(f" CRITICAL ERROR: Application failed to start.")
    print(f" Error Type: {type(e).__name__}")
    print(f" Error Message: {e}")
    print("!"*60 + "\n")
    
    traceback.print_exc()
    
    # Show search paths and bundle contents for debugging
    print(f"\nPython Search Paths:")
    for p in sys.path:
        print(f"  - {p}")
        
    if getattr(sys, 'frozen', False):
        bundle_dir = getattr(sys, '_MEIPASS', 'unknown')
        print(f"\nBundle Directory (_MEIPASS): {bundle_dir}")
        if os.path.exists(bundle_dir):
            try:
                print(f"\nFiles in Bundle Root (first 50):")
                files = os.listdir(bundle_dir)
                for f in sorted(files)[:50]:
                    print(f"  [ {'DIR ' if os.path.isdir(os.path.join(bundle_dir, f)) else 'FILE'} ] {f}")
                
                pkg_path = os.path.join(bundle_dir, 'sd_backup_tool')
                if os.path.exists(pkg_path):
                    print(f"\nPackage 'sd_backup_tool' contents (first 20):")
                    for f in sorted(os.listdir(pkg_path))[:20]:
                        print(f"  {f}")
                else:
                    print("\nWARNING: 'sd_backup_tool' package directory NOT FOUND in bundle root!")
            except Exception as le:
                print(f"Diagnostic failed: {le}")
    
    print("\nPlease take a photo or screenshot of this window.")
    print("This window will close in 60 seconds...")
    import time
    time.sleep(60)
    sys.exit(1)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nRuntime Error: {e}")
        import time
        time.sleep(60)
        sys.exit(1)
