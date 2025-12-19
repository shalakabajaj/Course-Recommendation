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
    command: ["cat"]
    tty: true
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-socket

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true
    securityContext:
      runAsUser: 0
      readOnlyRootFilesystem: false
    volumeMounts:
    - mountPath: /home/jenkins/agent
      name: workspace-volume

  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command: ["cat"]
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

        SONAR_HOST_URL = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"
    }

    stages {

        stage('Checkout Code') {
            steps {
                sh '''
                  rm -rf *
                  git clone https://github.com/shalakabajaj/Course-Recommendation.git .
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                container('docker') {
                    sh '''
                      docker build --no-cache \
                        -t course-recommender:${BUILD_NUMBER} \
                        -t course-recommender:latest .
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh '''
                      sonar-scanner \
                        -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
                        -Dsonar.projectBaseDir=/home/jenkins/agent/workspace/2401007
                    '''
                }
            }
        }

        // stage('Login to Nexus') {
        //     steps {
        //         container('docker') {
        //             sh '''
        //               docker login nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085 \
        //                 -u student \
        //                 -p Imcc@2025
        //             '''
        //         }
        //     }
        // }

        stage('Login to Nexus') {
            steps {
                container('dind') {
                    sh """
                        echo 'Logging into Nexus registry...'
                        docker login ${REGISTRY_HOST} -u admin -p Changeme@2025
                    """
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                container('docker') {
                    sh '''
                      docker tag course-recommender:${BUILD_NUMBER} nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401007/course-recommender:${BUILD_NUMBER}
                      docker tag course-recommender:${BUILD_NUMBER} nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401007/course-recommender:latest

                      docker push nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401007/course-recommender:${BUILD_NUMBER}
                      docker push nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401007/course-recommender:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                      kubectl apply -f deployment.yaml -n 2401007
                      kubectl apply -f service.yaml -n 2401007
                      kubectl rollout status deployment/course-recommender -n 2401007
                    '''
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
