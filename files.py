import os
import json

# Configuration
folder_path = 'gamefiles-all'  # Update this if needed
base_url = 'http://104.234.180.137/Mobile/GameFiles-all/'

def get_gpu_type(filename):
    """Determines the GPU type based on the filename extension and new rules."""
    lower_filename = filename.lower()

    # New rules: if menu.*.* or player.*.* or samp.*.* then gpu = all
    if 'menu.' in lower_filename or 'player.' in lower_filename or 'samp.' in lower_filename:
        return 'all'

    # Existing rules (processed only if the new rules are not met)
    if '.dxt.' in lower_filename:
        return 'dxt'
    elif '.etc.' in lower_filename:
        return 'etc'
    elif '.pvr.' in lower_filename:
        return 'pvr'
    elif '.unc.' in lower_filename:
        return 'unc'
    else:
        return 'all'

def generate_json(mode, output_filename):
    files_list = []

    for root, dirs, files in os.walk(folder_path):
        # Directory handling based on mode
        if mode == 'all_except_samp':
            # Remove both 'SAMP' and 'samp' directories
            dirs[:] = [d for d in dirs if d.lower() != 'samp']
        elif mode == 'only_samp':
            # Keep only 'SAMP', 'samp', and 'texdb/samp' in the first level
            if root == folder_path:
                dirs[:] = [d for d in dirs if d.lower() in ['samp', 'texdb']]
            elif os.path.basename(root).lower() == 'texdb':
                dirs[:] = [d for d in dirs if d.lower() == 'samp']

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)

            # Convert paths to forward slashes
            normalized_path = relative_path.replace('\\', '/')
            normalized_path = normalized_path.replace('//', '/')  # Remove duplicates

            # Mode filtering
            if mode == 'only_samp':
                # Include texdb/samp.img, texdb/SAMPCOL.img, and texdb/samp/ folder
                if not (normalized_path.startswith(('SAMP/', 'samp/', 'texdb/samp')) or 
                        normalized_path in ['texdb/samp.img', 'texdb/SAMPCOL.img']):
                    continue  # Only keep relevant files
            elif mode == 'all_except_samp':
                # Exclude texdb/samp.img, texdb/SAMPCOL.img, and texdb/samp/ folder
                if normalized_path.startswith(('SAMP/', 'samp/', 'texdb/samp')) or \
                   normalized_path in ['texdb/samp.img', 'texdb/SAMPCOL.img']:
                    continue  # Exclude these files

            gpu_type = get_gpu_type(file)  # Determine GPU type based on filename

            files_list.append({
                "name": file,
                "size": str(os.path.getsize(file_path)),
                "path": normalized_path,  # Now guaranteed forward slashes
                "url": f"{base_url}{normalized_path}",
                "gpu": gpu_type  # Add the determined GPU type
            })

    # Save to JSON
    with open(output_filename, 'w') as f:
        json.dump({"files": files_list}, f, indent=4, ensure_ascii=False)
    print(f"Created {output_filename} ({mode} mode)")

# Generate both configurations
generate_json('all_except_samp', 'lite_list.json')
generate_json('only_samp', 'samp_list.json')
