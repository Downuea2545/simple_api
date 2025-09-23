pipeline {
    agent none  // ตั้งค่า agent เป็น none ที่ระดับ pipeline เพื่อให้กำหนด agent ได้ที่แต่ละ stage

    environment {
        API_REPO_URL = 'https://github.com/Downuea2545/simple_api.git'
        ROBOT_REPO_URL = 'https://github.com/Downuea2545/simple-api-robot.git'
        IMAGE_NAME = "your-gitlab-registry/your-project/api-app:${BUILD_ID}"
        DOCKER_REGISTRY_CREDENTIALS = 'gitlab-registry-credentials' // ตัวแปรสำหรับ Credential ID ที่คุณสร้างใน Jenkins
    }

    stages {
        stage('Checkout & Build') {
            agent { label 'test' } // Stage นี้จะรันบน VM ที่มี Label เป็น 'test' (vm2)
            steps {
                script {
                    echo "Checking out code and building Docker image..."
                    // Checkout code
                    git branch: 'main', url: "${API_REPO_URL}"
                    // Build Docker Image
                    sh "docker build -t simple-api-image ."
                }
            }
        }

        stage('Run Unit Tests') {
            agent { label 'test' } // Stage นี้จะรันบน VM ที่มี Label เป็น 'test'
            steps {
                script {
                    echo "Running Python Unit Tests..."
                    sh "docker run --rm simple-api-image pytest"
                }
            }
        }
        
        stage('Tag & Push Image') {
            agent { label 'test' } // Stage นี้จะรันบน VM ที่มี Label เป็น 'test'
            steps {
                script {
                    echo "Tagging and pushing Docker image to registry..."
                    sh "docker tag simple-api-image ${IMAGE_NAME}"
                    // ใช้ withCredentials เพื่อ login ก่อน push
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_REGISTRY_CREDENTIALS}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD} your-gitlab-registry"
                        sh "docker push ${IMAGE_NAME}"
                    }
                }
            }
        }

        stage('Run Robot Tests') {
            agent { label 'preprod' } // Stage นี้จะรันบน VM ที่มี Label เป็น 'preprod' (vm3)
            steps {
                script {
                    echo "Running Robot Framework Tests..."
                    // Clone the robot test repository
                    sh "git clone ${ROBOT_REPO_URL} robot-tests"

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
            // Clean up any containers that might still be running on all agents
            script {
                sh "docker rm -f simple-api-image || true"
                sh "docker rmi simple-api-image || true"
                sh "docker rm -f api-service || true"
            }
        }
    }
}
