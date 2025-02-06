#!/bin/bash

detect_changed_projects() {
    local changed_files="$1"
    local project_files="$2"

    declare -A changed_projects

    for project in $project_files; do
        project_dir=$(dirname "$project")

        for file in $changed_files; do
            if [[ "$file" == "$project_dir"* ]]; then
                changed_projects["$project"]=1
                break
            fi
        done
    done

    printf "%s\n" "${!changed_projects[@]}"
}


if [[ "$1" != "test" ]]; then
    changed_files=$(git diff --name-only master HEAD)
    if [[ -z "$changed_files" ]]; then
      #echo "No changed files" >&3
      exit 0
    fi

    changed_files=$(git diff --name-only master HEAD | xargs realpath --relative-to="$(pwd)")
    # for f in $changed_files; do
    #     echo "Changes file $f" >&3
    # done

    project_files=$(find . -name "*.csproj" -print)
    if [[ -z "$project_files" ]]; then
      #echo "No csproj files" >&3
      exit 0
    fi

    project_files=$(find . -name "*.csproj" -print | xargs realpath --relative-to="$(pwd)")
    # for f in $project_files; do
    #     echo "Project file $f" >&3
    # done

    detect_changed_projects "$changed_files" "$project_files"
else
    detect_changed_projects "$2" "$3"     
fi
