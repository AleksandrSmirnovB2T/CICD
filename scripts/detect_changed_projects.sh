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

    for project in "${!changed_projects[@]}"; do
        echo "$project"
    done
}


if [[ "$1" != "test" ]]; then
    changed_files=$(git diff --name-only)
    project_files=$(find . -name "*.csproj" -print)
    detect_changed_projects "$changed_files" "$project_files"
else
    detect_changed_projects "$2" "$3"     
fi
