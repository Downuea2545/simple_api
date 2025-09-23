pipeline {
    agent any

    environment {
        // ข้อมูล Registry ของคุณ
        REGISTRY = 'ghcr.io/Downuea2545'
        IMAGE_NAME = 'simple-api'

        // ข้อมูล VM
        VM_TEST_HOST = '192.168.1.107'      // เปลี่ยนเป็น IP ของ VM Test
        VM_PREPROD_HOST = '192.168.1.108'   // เปลี่ยนเป็น IP ของ VM Pre-Prod
        VM_REMOTE_USER = 'jenkins'          // เปลี่ยนเป็นชื่อผู้ใช้บน VM ที่ใช้รัน SSH

        // ID ของ Credentials ใน Jenkins
        // ต้องสร้าง Credentials เหล่านี้ก่อนใน Jenkins -> Manage Credentials
        VM_SSH_CREDENTIALS_ID = 'jenkins_ssh_key'       // Credentials สำหรับ SSH
        GITHUB_CREDENTIALS_ID = 'simple-api'            // Credentials สำหรับ Git และ Docker Login
        
        // URL ของ Repo Robot Test
        ROBOT_REPO_URL = 'https://github.com/Downuea2545/simple-api-robot.git'
    }

    stages {
        stage('1. Unit Test & Build Image') {
            steps {
                script {
                    def fullImageName = "${REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                    echo "Building and testing Docker image: ${fullImageName}"
                    
                    // ใช้ docker build เพื่อสร้าง image โดย Unit Test อยู่ใน Dockerfile
                    // ถ้า pytest ล้มเหลว ขั้นตอนนี้ก็จะล้มเหลวไปด้วย
                    docker.build(fullImageName, '.')
                }
            }
        }
        
        stage('2. Push Image to Registry') {
            steps {
                script {
                    def fullImageName = "${REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                    
                    // ใช้ withRegistry เพื่อ login เข้า ghcr.io ด้วย Credentials
                    docker.withRegistry("https://ghcr.io", GITHUB_CREDENTIALS_ID) {
                        docker.image(fullImageName).push()
                    }
                }
            }
        }

        stage('3. Deploy & Robot Test on Test VM') {
            agent any // ให้ Jenkins เลือก Agent ที่มี Docker ได้
            steps {
                sshagent(credentials: [VM_SSH_CREDENTIALS_ID]) {
                    script {
                        def fullImageName = "${REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}"
                        
                        // Login to ghcr.io on the remote Test VM
                        withCredentials([usernamePassword(credentialsId: GITHUB_CREDENTIALS_ID, usernameVariable: 'GITHUB_USER', passwordVariable: 'GITHUB_TOKEN')]) {
                            sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_TEST_HOST} 'echo ${GITHUB_TOKEN} | docker login ghcr.io -u ${GITHUB_USER} --password-stdin'"
                        }
                        
                        // Pull and Run the application on the Test VM
                        sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_TEST_HOST} 'docker pull ${fullImageName}'"
                        sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_TEST_HOST} 'docker stop ${IMAGE_NAME}-test || true && docker rm ${IMAGE_NAME}-test || true'"
                        sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_TEST_HOST} 'docker run -d --name ${IMAGE_NAME}-test -p 8080:5000 ${fullImageName}'"
                        
                        // Run Robot Test
                        echo "Running Robot Tests from separate repository..."
                        dir('robot-tests-workspace') {
                            git url: ROBOT_REPO_URL, branch: 'main', credentialsId: GITHUB_CREDENTIALS_ID
                            sh '''
                                #!/bin/bash
                                set -e
                                if [ ! -d "venv" ]; then
                                    python3 -m venv venv
                                fi
                                ./venv/bin/pip install -r requirements.txt
                                ./venv/bin/robot --variable API_URL:${VM_TEST_HOST}:8080 tests/api_tests.robot
                            '''
                        }
                    }
                }
            }
        }
        
        stage('4. Deploy to Pre-Prod VM') {
            input { message "Ready to deploy to Pre-Production? (VM 3)" }
            steps {
                sshagent(credentials: [VM_SSH_CREDENTIALS_ID]) {
                    script {
                        def fullImageName = "${REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}"

                        // Login to ghcr.io on the remote Pre-Prod VM
                        withCredentials([usernamePassword(credentialsId: GITHUB_CREDENTIALS_ID, usernameVariable: 'GITHUB_USER', passwordVariable: 'GITHUB_TOKEN')]) {
                            sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_PREPROD_HOST} 'echo ${GITHUB_TOKEN} | docker login ghcr.io -u ${GITHUB_USER} --password-stdin'"
                        }

                        // Pull and Run the application on the Pre-Prod VM
                        sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_PREPROD_HOST} 'docker pull ${fullImageName}'"
                        sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_PREPROD_HOST} 'docker stop ${IMAGE_NAME}-preprod || true && docker rm ${IMAGE_NAME}-preprod || true'"
                        sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_PREPROD_HOST} 'docker run -d --name ${IMAGE_NAME}-preprod -p 80:5000 ${fullImageName}'"
                    }
                }
            }
        }
        
        stage('5. Ready for Manual Load Test') {
            steps {
                echo "Deployment to Pre-Prod is complete."
                echo "You can now run JMeter tests against http://${VM_PREPROD_HOST}"
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline finished. Cleaning up...'
            cleanWs()
            
            sshagent(credentials: [VM_SSH_CREDENTIALS_ID]) {
                sh "ssh -o StrictHostKeyChecking=no ${VM_REMOTE_USER}@${VM_TEST_HOST} 'docker stop ${IMAGE_NAME}-test || true && docker rm ${IMAGE_NAME}-test || true'"
            }
        }
    }
}
