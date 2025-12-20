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
    command:
    - cat
    tty: true
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
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
      privileged: true  # Needed to run Docker daemon
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""  # Disable TLS for simplicity
    volumeMounts:
    - name: docker-config
      mountPath: /etc/docker/daemon.json
      subPath: daemon.json  # Mount the file directly here
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
                container('dind') {
                    sh '''
                      docker build -t course-recommender:latest .
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh '''
                      sonar-scanner \
                        -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000
                    '''
                }
            }
        }

        stage('Login to Docker Registry') {
            steps {
                container('dind') {
                    sh 'docker --version'
                    sh 'sleep 10'
                    sh 'docker login nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085 -u admin -p Changeme@2025'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                container('dind') {
                    sh '''
                      docker tag course-recommender:latest ${REGISTRY}/course-recommender:latest

                      docker push ${REGISTRY}/course-recommender:latest
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
