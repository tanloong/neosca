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

# Check for uncommitted changes in the git repository
if [ -d ".git" ] && [[ -n $(git status --porcelain) ]]; then
  printf "\033[31mWarning: There are uncommitted changes in the repository.\nPlease commit or stash them before bumping.\033[0m\n"
  exit 1
fi

if ! [ $# -eq 1 ] ||\
   ! [[ $1 =~ ^(patch|major|minor)$ ]]; then
  echo "Usage: bash $(basename "$0") {patch, minor, major}"
  exit 1
fi
component=$1

ns_about_path=./src/neosca/ns_about.py
ns_readme_path=./README.md
ns_citings_path=./src/neosca/ns_data/citings.json

curr_version=$(grep -Eo '\b[0-9]+(\.[0-9]+){2}\b' "$ns_about_path")
next_version=$(bump "$curr_version" "$component")

# Inform the user of the changes
printf "Bumping from version \033[33m%s\033[0m to \033[33m%s\033[0m\n" "$curr_version" "$next_version"
printf "The following files will be modified:\n"
printf "\033[33m  %s\n\033[0m" "$ns_about_path"
printf "\033[33m  %s\n\033[0m" "$ns_readme_path"
printf "\033[33m  %s\033[0m\n" "$ns_citings_path"

# Ask for user confirmation
read -p "Do you want to continue? (y/n) " -n 1 -r
echo    # Move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  # Perform the version bump
  sed -E -i "s/$curr_version/$next_version/g" "$ns_about_path" "$ns_readme_path" "$ns_citings_path"
  printf "\033[32mVersion bumped successfully.\033[0m\n"
else
  printf "\033[33mOperation cancelled.\033[0m\n"
  exit 1
fi

# vim:tabstop=2:shiftwidth=2
