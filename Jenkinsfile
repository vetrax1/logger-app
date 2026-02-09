pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = "docker.io"
        DOCKER_USERNAME = "anunukemsam"
        FRONTEND_IMAGE = "${DOCKER_USERNAME}/logger-frontend-image"
        BACKEND_IMAGE = "${DOCKER_USERNAME}/logger-backend-image"
        SNYK_TOKEN = credentials('snyk-token')
    }

    stages {
        stage('Test Backend') {
            steps {
                echo 'Testing...'
                sh '''
                    cd backend
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    flake8 app.py
                '''
            }
        }
        stage('Image Build') {
            steps {
                echo 'Building...'
                sh '''
                    docker build -t ${FRONTEND_IMAGE}:1.${BUILD_NUMBER} frontend
                    docker build -t ${BACKEND_IMAGE}:1.${BUILD_NUMBER} backend
                '''
            }
        }
        stage('Image Scan') {
            steps {
                echo 'Scanning...'
                sh '''
                    snyk auth ${SNYK_TOKEN}
                    snyk container test ${FRONTEND_IMAGE}:1.${BUILD_NUMBER} --severity-threshold=critical --file=frontend/Dockerfile
                    snyk container test ${BACKEND_IMAGE}:1.${BUILD_NUMBER} --severity-threshold=critical --file=backend/Dockerfile
                '''
            }
        }
        stage('Push to remote registry') {
            steps {
                echo 'Deploying...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh '''
                        echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin
                        docker push ${FRONTEND_IMAGE}:1.${BUILD_NUMBER}
                        docker push ${BACKEND_IMAGE}:1.${BUILD_NUMBER}
                    '''
                }
            }
        }
    }
    post {
        always {
            echo 'Cleaning up...'
            sh '''
                docker logout
                docker rmi ${FRONTEND_IMAGE}:1.${BUILD_NUMBER} || true
                docker rmi ${BACKEND_IMAGE}:1.${BUILD_NUMBER} || true
            '''
        }
    }
}
