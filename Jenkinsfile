pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command: ["cat"]
    tty: true

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true
    securityContext:
      runAsUser: 0
      readOnlyRootFilesystem: false
    env:
    - name: KUBECONFIG
      value: /kube/config
    volumeMounts:
    - name: kubeconfig-secret
      mountPath: /kube/config
      subPath: kubeconfig

  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    volumeMounts:
    - name: docker-config
      mountPath: /etc/docker/daemon.json
      subPath: daemon.json

  volumes:
  - name: docker-config
    configMap:
      name: docker-daemon-config
  - name: kubeconfig-secret
    secret:
      secretName: kubeconfig-secret
'''
        }
    }

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
                sh '''
                    rm -rf *
                    git clone ${GIT_REPO} .
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        sleep 15
                        docker build -t ${APP_NAME}:latest .
                        docker image ls
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    withCredentials([string(credentialsId: 'sonar-token-2401007', variable: 'SONAR_TOKEN')]) {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.login=$SONAR_TOKEN \
                                -Dsonar.sources=. \
                                -Dsonar.python.version=3.10
                        '''
                    }
                }
            }
        }

        stage('Login to Nexus') {
            steps {
                container('dind') {
                    sh '''
                        docker login ${REGISTRY_HOST} -u admin -p Changeme@2025
                    '''
                }
            }
        }

        stage('Build - Tag - Push Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        docker tag ${APP_NAME}:latest ${REGISTRY}/${APP_NAME}:latest
                        docker push ${REGISTRY}/${APP_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    script {
                        dir('k8s') {
                            sh """
                            # Ensure namespace exists
                            kubectl get namespace ${NAMESPACE} || kubectl create namespace ${NAMESPACE}

                            # Apply deployment & service
                            kubectl apply -f deployment.yaml -n ${NAMESPACE}
                            kubectl apply -f service.yaml -n ${NAMESPACE}

                            # Force rollout
                            kubectl delete pod -l app=${APP_NAME} -n ${NAMESPACE} || true
                            kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE}
                            """
                        }
                    }
                }
            }
        }

        stage('Debug Kubernetes State') {
            steps {
                container('kubectl') {
                    sh """
                    echo "========== PODS =========="
                    kubectl get pods -n ${NAMESPACE}

                    echo "========== SERVICES =========="
                    kubectl get svc -n ${NAMESPACE}

                    echo "========== POD LOGS =========="
                    kubectl logs -l app=${APP_NAME} -n ${NAMESPACE} || true
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
