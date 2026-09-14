// School_Timetable_Fresh — Jenkins CI/CD Pipeline
//
// Python + Faker + pandas + DOcplex/CPLEX + Plotly
//
// Pipeline:
//   Checkout
//      ↓
//   Python environment
//      ↓
//   Generate sample data
//      ↓
//   Run CPLEX timetable optimizer
//      ↓
//   Generate dashboard
//      ↓
//   Validate generated files
//      ↓
//   Build Docker image
//      ↓
//   Test Docker container
//
// Jenkins credential required for pushing Docker image:
//   docker-registry
//
// Optional SSH deployment credential:
//   ssh-school-timetable

pipeline {

    agent any

    options {
        timestamps()

        disableConcurrentBuilds(
            abortPrevious: true
        )

        buildDiscarder(
            logRotator(
                numToKeepStr: '10',
                artifactNumToKeepStr: '5'
            )
        )

        timeout(
            time: 30,
            unit: 'MINUTES'
        )

        ansiColor('xterm')
    }

    parameters {

        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip timetable validation tests'
        )

        booleanParam(
            name: 'BUILD_DOCKER',
            defaultValue: true,
            description: 'Build Docker image'
        )

        booleanParam(
            name: 'RUN_DOCKER_TEST',
            defaultValue: true,
            description: 'Run generated dashboard inside Docker'
        )
    }

    environment {

        APP_NAME = 'school-timetable-fresh'

        IMAGE_NAME = "${env.DOCKER_REGISTRY ?: 'docker.io'}/${env.DOCKER_NAMESPACE ?: 'yourusername'}/school-timetable-fresh"

        IMAGE_TAG = "${BUILD_NUMBER}"

        PYTHON_VERSION = '3.10'

        VENV_DIR = '.jenkins-venv'

        OUTPUT_DIR = 'output'
    }

    stages {

        // ============================================================
        // 1. CLEAN
        // ============================================================

        stage('Pre-clean') {

            steps {

                sh '''
                    set +e

                    echo "======================================"
                    echo "Cleaning old Jenkins workspace"
                    echo "======================================"

                    rm -rf .jenkins-venv
                    rm -rf output/*.csv
                    rm -f output/timetable_gantt.html

                    docker container prune -f || true
                    docker image prune -f || true

                    df -h || true
                '''
            }
        }


        // ============================================================
        // 2. CHECKOUT
        // ============================================================

        stage('Checkout') {

            steps {

                checkout scm

                script {

                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    env.GIT_BRANCH_NAME = sh(
                        script: 'git rev-parse --abbrev-ref HEAD',
                        returnStdout: true
                    ).trim()

                    echo """
                    ======================================
                    School Timetable Project
                    ======================================
                    Commit : ${env.GIT_COMMIT_SHORT}
                    Branch : ${env.GIT_BRANCH_NAME}
                    Build  : ${env.BUILD_NUMBER}
                    ======================================
                    """
                }
            }
        }


        // ============================================================
        // 3. PYTHON SETUP
        // ============================================================

        stage('Python Setup') {

            steps {

                sh '''
                    set -eu

                    echo "Python version:"
                    python3 --version

                    echo "Creating Jenkins virtual environment..."

                    python3 -m venv "${VENV_DIR}"

                    . "${VENV_DIR}/bin/activate"

                    python -m pip install --upgrade pip

                    echo "Installing project requirements..."

                    pip install -r requirements.txt

                    echo "Installed packages:"
                    pip list
                '''
            }
        }


        // ============================================================
        // 4. GENERATE DATA
        // ============================================================

        stage('Generate Sample Data') {

            steps {

                sh '''
                    set -eu

                    . "${VENV_DIR}/bin/activate"

                    echo "Generating Faker sample data..."

                    python -m src.data_generation.generate_data

                    echo ""
                    echo "Generated files:"
                    ls -lh output/
                '''
            }
        }


        // ============================================================
        // 5. RUN CPLEX MODEL
        // ============================================================

        stage('Run CPLEX Timetable Model') {

            steps {

                sh '''
                    set -eu

                    . "${VENV_DIR}/bin/activate"

                    echo "Running CPLEX timetable optimization..."

                    python -m src.model.build_model

                    echo ""
                    echo "Checking timetable output..."

                    test -f output/timetable.csv

                    echo "Timetable generated successfully."

                    echo ""
                    echo "Timetable:"
                    cat output/timetable.csv
                '''
            }
        }


        // ============================================================
        // 6. GENERATE DASHBOARD
        // ============================================================

        stage('Generate Dashboard') {

            steps {

                sh '''
                    set -eu

                    . "${VENV_DIR}/bin/activate"

                    echo "Generating Plotly dashboard..."

                    python -m src.visualization.build_dashboard

                    test -f output/timetable_gantt.html

                    echo ""
                    echo "Dashboard generated successfully."

                    ls -lh output/timetable_gantt.html
                '''
            }
        }


        // ============================================================
        // 7. VALIDATE OUTPUT
        // ============================================================

        stage('Validate Output') {

            when {
                expression {
                    !params.SKIP_TESTS
                }
            }

            steps {

                sh '''
                    set -eu

                    echo "======================================"
                    echo "Validating timetable output"
                    echo "======================================"

                    . "${VENV_DIR}/bin/activate"

                    python - <<'PY'

                    import pandas as pd
                    from pathlib import Path

                    output = Path("output")

                    required_files = [
                        "teachers.csv",
                        "rooms.csv",
                        "courses.csv",
                        "timetable.csv",
                        "timetable_gantt.html"
                    ]

                    for file in required_files:

                        path = output / file

                        if not path.exists():
                            raise SystemExit(
                                f"Missing required file: {path}"
                            )

                        print(f"✓ {path}")

                    timetable = pd.read_csv(
                        output / "timetable.csv"
                    )

                    if timetable.empty:
                        raise SystemExit(
                            "Timetable is empty."
                        )

                    print(
                        f"✓ Timetable contains "
                        f"{len(timetable)} scheduled classes"
                    )

                    print("✓ Output validation successful.")

                    PY
                '''
            }
        }


        // ============================================================
        // 8. BUILD DOCKER IMAGE
        // ============================================================

        stage('Build Docker Image') {

            when {
                expression {
                    params.BUILD_DOCKER
                }
            }

            steps {

                script {

                    echo "Building Docker image..."

                    def image = docker.build(
                        "${env.IMAGE_NAME}:${env.IMAGE_TAG}",
                        "--pull ."
                    )

                    image.tag('latest')

                    env.BUILT_IMAGE =
                        "${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                }
            }
        }


        // ============================================================
        // 9. DOCKER TEST
        // ============================================================

        stage('Docker Test') {

            when {
                expression {
                    params.BUILD_DOCKER &&
                    params.RUN_DOCKER_TEST
                }
            }

            steps {

                sh '''
                    set -eu

                    echo "Starting Docker container..."

                    docker rm -f school-timetable-test 2>/dev/null || true

                    docker run -d \
                        --name school-timetable-test \
                        -p 8080:80 \
                        "${BUILT_IMAGE}"

                    echo "Waiting for application..."

                    sleep 5

                    echo "Testing dashboard..."

                    curl --fail \
                        http://127.0.0.1:8080/

                    echo ""
                    echo "✓ Docker container is serving dashboard."

                    docker logs school-timetable-test || true

                    docker rm -f school-timetable-test
                '''
            }
        }


        // ============================================================
        // 10. ARCHIVE OUTPUT
        // ============================================================

        stage('Archive Timetable') {

            steps {

                archiveArtifacts(
                    artifacts: 'output/*.csv,output/*.html',
                    fingerprint: true,
                    allowEmptyArchive: false
                )
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        success {

            echo """
            ==========================================
            BUILD SUCCESSFUL
            ==========================================
            Project : ${APP_NAME}
            Build   : ${BUILD_NUMBER}
            Commit  : ${GIT_COMMIT_SHORT}

            Timetable generated successfully.
            Dashboard generated successfully.
            Docker image built successfully.

            ==========================================
            """
        }

        failure {

            echo """
            ==========================================
            BUILD FAILED
            ==========================================
            Project : ${APP_NAME}
            Build   : ${BUILD_NUMBER}

            Check the Jenkins console output.
            ==========================================
            """
        }

        always {

            sh '''
                set +e

                echo "Cleaning Jenkins resources..."

                docker rm -f school-timetable-test 2>/dev/null || true

                rm -rf "${VENV_DIR}"

                docker container prune -f || true
                docker image prune -f || true

                df -h || true
            '''

            cleanWs(
                deleteDirs: true,
                notFailBuild: true
            )
        }
    }
}