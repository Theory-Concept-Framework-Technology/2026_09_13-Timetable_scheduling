pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(
            name: 'DEPLOY',
            defaultValue: false,
            description: 'After a green build, replace the mouse-gaze container on this agent.'
        )
    }

    environment {
        IMAGE = 'mouse-gaze'
    }

    stages {
        stage('Build image') {
            steps {
                script {
                    def tag = "${env.IMAGE}:${env.BUILD_NUMBER}"
                    def latest = "${env.IMAGE}:latest"
                    if (isUnix()) {
                        sh "docker version"
                        sh "docker build -t ${tag} -t ${latest} ."
                    } else {
                        bat "docker version"
                        bat "docker build -t ${tag} -t ${latest} ."
                    }
                }
            }
        }

        stage('Smoke test') {
            steps {
                script {
                    def tag = "${env.IMAGE}:${env.BUILD_NUMBER}"
                    def run = "docker run --rm -e SDL_VIDEODRIVER=dummy -e SDL_AUDIODRIVER=dummy ${tag} python scripts/smoke_test.py"
                    if (isUnix()) {
                        sh run
                    } else {
                        bat run
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                expression { return params.DEPLOY }
            }
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            docker rm -f mouse-gaze || true
                            docker run -d --name mouse-gaze --restart unless-stopped mouse-gaze:latest
                        '''
                    } else {
                        bat '''
                            docker rm -f mouse-gaze
                            docker run -d --name mouse-gaze --restart unless-stopped mouse-gaze:latest
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Image ${env.IMAGE}:${env.BUILD_NUMBER} is ready."
        }
        failure {
            echo 'Build failed. The previous mouse-gaze container, if any, was left running.'
        }
    }
}
