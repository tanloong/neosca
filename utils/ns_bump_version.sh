#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

function bump() {
    if ! [ $# -eq 2 ] || \
       ! [[ $1 =~ ^[0-9]+(\.[0-9]+){2}$ ]] || \
       ! [[ $2 =~ ^(patch|major|minor)$ ]]; then
        echo "Usage: bash $(basename "$0") 0.1.1 {patch, minor, major}"
        exit 1
    fi

    # Input version number and component
    version=$1
    component=$2
    # Split version number into components
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)
    patch=$(echo "$version" | cut -d. -f3)
    # Bump version based on component
    if [ "$component" == "patch" ]; then
        patch=$((patch + 1))
    elif [ "$component" == "minor" ]; then
        minor=$((minor + 1))
        patch=0
    elif [ "$component" == "major" ]; then
        major=$((major + 1))
        minor=0
        patch=0
    else
        echo "Usage: bash $(basename "$0") 0.1.1 {patch, minor, major}"
        exit 1
    fi

    # Concatenate components back together
    new_version="$major.$minor.$patch"
    echo "$new_version"
}

if ! [ $# -eq 1 ] ||\
   ! [[ $1 =~ ^(patch|major|minor)$ ]]; then
    echo "Usage: bash $(basename "$0") {patch, minor, major}"
    exit 1
fi
component=$1

curr_folder=$(cd "$(dirname "$0")" && pwd)
ns_home=$(dirname "$curr_folder")
ns_about_path="$ns_home"/src/neosca/ns_about.py
ns_readme_path="$ns_home"/README.md
ns_citings_path="$ns_home"/src/neosca/ns_data/citings.json

curr_version=$(grep -Eo '\b[0-9]+(\.[0-9]+){2}\b' "$ns_about_path")
next_version=$(bump "$curr_version" "$component")

sed -E -i "s/$curr_version/$next_version/g" "$ns_about_path" "$ns_readme_path" "$ns_citings_path"
