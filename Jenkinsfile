properties([pipelineTriggers([]), durabilityHint('PERFORMANCE_OPTIMIZED')])

pipeline {

    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:20.10.24
    command:
    - cat
    tty: true
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-socket

  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
    tty: true
    securityContext:
      runAsUser: 0
      readOnlyRootFilesystem: false
    volumeMounts:
    - mountPath: /home/jenkins/agent
      name: workspace-volume

  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command:
    - cat
    tty: true
    volumeMounts:
    - mountPath: /home/jenkins/agent
      name: workspace-volume

  volumes:
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock
  - name: workspace-volume
    emptyDir: {}
"""
        }
    }

    options { skipDefaultCheckout() }

    environment {
        APP_NAME = "course-recommender"
        GIT_REPO = "https://github.com/shalakabajaj/Course-Recommendation.git"

        REGISTRY_HOST = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REGISTRY_NAMESPACE = "2401007"
        REGISTRY = "${REGISTRY_HOST}/${REGISTRY_NAMESPACE}"

        NAMESPACE = "2401007"

        SONAR_PROJECT_KEY = "2401007_Course_Recommendation_System"
        SONAR_HOST_URL = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"
        SONAR_TOKEN = "sqp_e660f7a442e917c6a49c5b81f0506e1f52c4e61e"
    }

    stages {

        stage('Checkout Code') {
            steps {
                sh """
                    rm -rf *
                    git clone ${GIT_REPO} .
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                container('docker') {
                    sh """
                        docker build --no-cache \
                          -t ${APP_NAME}:${BUILD_NUMBER} \
                          -t ${APP_NAME}:latest .
                    """
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh "sonar-scanner"
                }
            }
        }

        stage('Login to Nexus') {
            steps {
                container('docker') {
                    sh """
                        docker login ${REGISTRY_HOST} \
                          -u admin \
                          -p Imcc@2025
                    """
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                container('docker') {
                    sh """
                        docker tag ${APP_NAME}:${BUILD_NUMBER} ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                        docker tag ${APP_NAME}:${BUILD_NUMBER} ${REGISTRY}/${APP_NAME}:latest

                        docker push ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                        docker push ${REGISTRY}/${APP_NAME}:latest
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh """
                        kubectl apply -f deployment.yaml -n ${NAMESPACE}
                        kubectl apply -f service.yaml -n ${NAMESPACE}
                        kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE}
                    """
                }
            }
        }
    }

    post {
        success { echo "🎉 Course Recommendation CI/CD Pipeline SUCCESS" }
        failure { echo "❌ Course Recommendation CI/CD Pipeline FAILED" }
        always  { echo "🔁 Pipeline Finished" }
    }
}
