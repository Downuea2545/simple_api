pipeline {
    agent any

    environment {
        API_REPO_URL = 'https://github.com/your-username/your-api-repo.git'
        ROBOT_REPO_URL = 'https://github.com/your-username/your-robot-repo.git'
        IMAGE_NAME = "your-gitlab-registry/your-project/api-app:${BUILD_ID}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: "${API_REPO_URL}"
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    // This assumes you have a Dockerfile in your repo
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    echo "Running Python Unit Tests..."
                    sh "docker run --rm ${IMAGE_NAME} pytest"
                }
            }
        }
        
        stage('Push Image to Registry') {
            steps {
                script {
                    echo "Pushing Docker image to registry..."
                    sh "docker push ${IMAGE_NAME}"
                }
            }
        }

        stage('Run Robot Tests') {
            steps {
                script {
                    echo "Running Robot Framework Tests..."
                    // Clone the robot test repository
                    dir('robot-tests') {
                        git branch: 'main', url: "${ROBOT_REPO_URL}"
                    }

                    // Run the API service in a detached container
                    sh "docker run -d --name api-service -p 5000:5000 ${IMAGE_NAME}"
                    
                    // Wait a bit for the service to start
                    sh "sleep 5"

                    // Run the robot tests against the running service
                    sh "robot --outputdir robot-results robot-tests/plus_test.robot"

                    // Clean up the running container
                    sh "docker rm -f api-service"
                }
            }
        }
    }

    post {
        always {
            // Clean up any containers that might still be running
            script {
                try {
                    sh "docker rm -f api-service"
                } catch (error) {
                    echo "Container 'api-service' not found. It might have been cleaned up already."
                }
            }
        }
    }
}
