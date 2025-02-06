#!/usr/bin/env bats

# Setup: Create a fake repo structure
setup() {
    mkdir -p test-repo/src/ProjectA test-repo/src/ProjectB
    echo "test content" > test-repo/src/ProjectA/SomeFile.cs
    echo "test content" > test-repo/src/ProjectB/AnotherFile.cs
    echo "<Project></Project>" > test-repo/src/ProjectA/ProjectA.csproj
    echo "<Project></Project>" > test-repo/src/ProjectB/ProjectB.csproj
}

teardown() {
    rm test-repo -r
}

@test "Detect changed projects from mock input" {
    # Mock changed files
    changed_files="test-repo/src/ProjectA/SomeFile.cs test-repo/src/ProjectB/AnotherFile.cs"

    # Mock project files
    project_files="test-repo/src/ProjectA/ProjectA.csproj test-repo/src/ProjectB/ProjectB.csproj"

    # Run the function and capture output
    output=$(./scripts/detect_changed_projects.sh "test" "$changed_files" "$project_files")

    echo "output" $output

    # Assert output contains expected projects
    [[ "$output" == *"test-repo/src/ProjectA/ProjectA.csproj"* ]]
    [[ "$output" == *"test-repo/src/ProjectB/ProjectB.csproj"* ]]
}

@test "Detect no changes when no files changed" {
    changed_files=""
    project_files="test-repo/src/ProjectA/ProjectA.csproj test-repo/src/ProjectB/ProjectB.csproj"

    output=$(./scripts/detect_changed_projects.sh "test" "$changed_files" "$project_files")

    # Assert no output
    [ -z "$output" ]
}
