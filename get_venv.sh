#!/usr/bin/env bash

# Function to find .venv directories
find_venv_directories() {
    local target_directory="$1"
    find "$target_directory" -type d -name ".venv" 2>/dev/null
}

# Main script logic
main() {
    local target="${1:-$HOME}"  # Use $HOME if no argument provided

    # Iterate over all found .venv directories
    find_venv_directories "$target" | while read -r venv_path; do
        # Check for pyvenv.cfg file inside the .venv directory
        if [[ -f "$venv_path/pyvenv.cfg" ]]; then
            if grep -q '^uv =' "$venv_path/pyvenv.cfg"; then
                echo "$venv_path"
            fi
            
        fi
    done
}

echo "searching all uv .venv in ${1:-$HOME} ..."
echo " ... be patient as it may take a minute ..."
echo " ... or two ..."

main "$@" > $(pwd)/env_list

echo "done"